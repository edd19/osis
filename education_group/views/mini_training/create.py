# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import collections
from typing import List, Dict, Optional

from django.http import response
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from rules.contrib.views import LoginRequiredMixin

from base.models.academic_year import starting_academic_year
from base.utils.cache import RequestCache
from base.views.common import display_success_messages
from education_group.ddd import command
from education_group.ddd.domain import mini_training, exception
from education_group.ddd.service.read import get_group_service
from education_group.ddd.service.write import create_orphan_mini_training_service
from education_group.forms import mini_training as mini_training_form
from education_group.templatetags.academic_year_display import display_as_academic_year
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd import command as command_pgrm
from program_management.ddd.business_types import *
from program_management.ddd.service.read import node_identity_service
from program_management.ddd.service.write import create_mini_training_and_paste_service

FormTab = collections.namedtuple("FormTab", "text active display include_html")


class MiniTrainingCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'base.add_minitraining'
    raise_exception = True

    form_class = mini_training_form.MiniTrainingForm

    template_name = "education_group_app/mini_training/upsert/create.html"

    def get_form_kwargs(self) -> Dict:
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        form_kwargs["mini_training_type"] = self.kwargs['type']
        form_kwargs["initial"] = self._get_initial_form()
        return form_kwargs

    def form_valid(self, form: mini_training_form.MiniTrainingForm) -> response.HttpResponseBase:
        try:
            if self.get_attach_path():
                mini_training_identity = create_mini_training_and_paste_service.create_mini_training_and_paste(
                    self._generate_create_and_paste_command_from_valid_form(form)
                )
            else:
                mini_training_identity = create_orphan_mini_training_service.create_orphan_mini_training(
                    self._generate_create_command_from_valid_form(form)
                )
            self.set_success_url(mini_training_identity)
            display_success_messages(self.request, self.get_success_msg(mini_training_identity), extra_tags='safe')
            return super().form_valid(form)

        except exception.MiniTrainingCodeAlreadyExistException as e:
            form.add_error("code", e.message)
        except exception.ContentConstraintTypeMissing as e:
            form.add_error('constraint_type', e.message)
        except (exception.ContentConstraintMinimumMaximumMissing,
                exception.ContentConstraintMaximumShouldBeGreaterOrEqualsThanMinimum) as e:
            form.add_error('min_constraint', e.message)
            form.add_error('max_constraint', '')
        except exception.StartYearGreaterThanEndYearException as e:
            form.add_error('academic_year', e.message)
            form.add_error('end_year', '')

        return self.form_invalid(form)

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context["mini_training_form"] = context["form"]
        context["tabs"] = self.get_tabs()
        context["cancel_url"] = self.get_cancel_url()
        return context

    def get_attach_path(self) -> Optional['Path']:
        return self.request.GET.get('path_to') or None

    def set_success_url(self, mini_training_identity: mini_training.MiniTrainingIdentity) -> None:
        self.success_url = self._generate_success_url(mini_training_identity)

    def get_success_msg(self, mini_training_identity: mini_training.MiniTrainingIdentity) -> str:
        return _("Mini-training <a href='%(link)s'> %(code)s (%(academic_year)s) </a> successfully created.") % {
            "link": self.success_url,
            "code": mini_training_identity.code,
            "academic_year": display_as_academic_year(mini_training_identity.year),
        }

    def get_tabs(self) -> List[FormTab]:
        return [
            FormTab(
                _("Identification"),
                True,
                True,
                "education_group_app/mini_training/upsert/identification_form.html"
            )
        ]

    def get_cancel_url(self) -> str:
        if self.get_attach_path():
            parent_identity = self.get_parent_identity()
            return reverse(
                'element_identification',
                kwargs={'code': parent_identity.code, 'year': parent_identity.year}
            ) + "?path={}".format(self.get_attach_path())
        return reverse('version_program')

    def _get_initial_form(self) -> Dict:
        request_cache = RequestCache(self.request.user, reverse('version_program'))
        default_academic_year = request_cache.get_value_cached('academic_year') or starting_academic_year()
        default_management_entity = None

        parent_identity = self.get_parent_identity()
        if parent_identity:
            default_academic_year = parent_identity.year
            domain_obj = get_group_service.get_group(
                command.GetGroupCommand(code=parent_identity.code, year=parent_identity.year)
            )
            default_management_entity = domain_obj.management_entity.acronym

        return {
            'academic_year': default_academic_year,
            'management_entity': default_management_entity
        }

    def get_parent_identity(self) -> Optional['NodeIdentity']:
        if self.get_attach_path():
            cmd_get_node_id = command_pgrm.GetNodeIdentityFromElementId(
                int(self.get_attach_path().split('|')[-1])
            )
            parent_id = node_identity_service.get_node_identity_from_element_id(cmd_get_node_id)
            return parent_id
        return None

    def _generate_create_command_from_valid_form(
            self,
            form: mini_training_form.MiniTrainingForm) -> command.CreateOrphanMiniTrainingCommand:
        return command.CreateOrphanMiniTrainingCommand(
            code=form.cleaned_data['code'],
            year=form.cleaned_data["academic_year"],
            type=form.cleaned_data["type"],
            abbreviated_title=form.cleaned_data['abbreviated_title'],
            title_fr=form.cleaned_data['title_fr'],
            title_en=form.cleaned_data['title_en'],
            status=form.cleaned_data['status'],
            schedule_type=form.cleaned_data['schedule_type'],
            credits=form.cleaned_data['credits'],
            constraint_type=form.cleaned_data['constraint_type'],
            min_constraint=form.cleaned_data['min_constraint'],
            max_constraint=form.cleaned_data['max_constraint'],
            management_entity_acronym=form.cleaned_data['management_entity'],
            teaching_campus_name=form.cleaned_data['teaching_campus']['name'],
            organization_name=form.cleaned_data['teaching_campus']['organization_name'],
            remark_fr=form.cleaned_data['remark_fr'],
            remark_en=form.cleaned_data['remark_en'],
            start_year=form.cleaned_data['academic_year'],
            end_year=form.cleaned_data['end_year'],
        )

    def _generate_create_and_paste_command_from_valid_form(
            self,
            form: mini_training_form.MiniTrainingForm) -> command_pgrm.CreateMiniTrainingAndPasteCommand:
        return command_pgrm.CreateMiniTrainingAndPasteCommand(
            code=form.cleaned_data['code'],
            year=form.cleaned_data["academic_year"],
            type=self.kwargs['type'],
            abbreviated_title=form.cleaned_data['abbreviated_title'],
            title_fr=form.cleaned_data['title_fr'],
            title_en=form.cleaned_data['title_en'],
            status=form.cleaned_data['status'],
            schedule_type=form.cleaned_data['schedule_type'],
            credits=form.cleaned_data['credits'],
            constraint_type=form.cleaned_data['constraint_type'],
            min_constraint=form.cleaned_data['min_constraint'],
            max_constraint=form.cleaned_data['max_constraint'],
            management_entity_acronym=form.cleaned_data['management_entity'],
            teaching_campus_name=form.cleaned_data['teaching_campus']['name'],
            organization_name=form.cleaned_data['teaching_campus']['organization_name'],
            remark_fr=form.cleaned_data['remark_fr'],
            remark_en=form.cleaned_data['remark_en'],
            start_year=form.cleaned_data['academic_year'],
            end_year=form.cleaned_data['end_year'],
            path_to_paste=self.get_attach_path()
        )

    def _generate_success_url(self, mini_training_identity: mini_training.MiniTrainingIdentity) -> str:
        success_url = reverse(
            "mini_training_identification",
            kwargs={"code": mini_training_identity.code, "year": mini_training_identity.year}
        )
        path = self.get_attach_path()
        if path:
            success_url += "?path={}".format(path)
        return success_url
