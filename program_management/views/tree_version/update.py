##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List

from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View

from base.views.common import display_success_messages
from base.views.mixins import AjaxTemplateMixin
from education_group.ddd.domain.service.identity_search import TrainingIdentitySearch
from education_group.ddd.domain.training import TrainingIdentity
from education_group.templatetags.academic_year_display import display_as_academic_year
from osis_role.contrib.views import AjaxPermissionRequiredMixin
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.forms.version import SpecificVersionForm
from program_management.models.education_group_version import EducationGroupVersion


class UpdateProgramTreeVersion(AjaxPermissionRequiredMixin, AjaxTemplateMixin, View):
    template_name = "tree_version/update_specific_version_inner.html"
    form_class = SpecificVersionForm
    permission_required = 'base.can_edit_programtreeversion'

    @cached_property
    def node_identity(self) -> 'NodeIdentity':
        return NodeIdentity(code=self.kwargs['code'], year=self.kwargs['year'])

    @cached_property
    def training_identity(self) -> 'TrainingIdentity':
        return TrainingIdentitySearch().get_from_node_identity(self.node_identity)

    @cached_property
    def program_tree_version_identity(self) -> ProgramTreeVersionIdentity:
        return ProgramTreeVersionIdentity(
            offer_acronym=self.training_identity.acronym,
            year=self.kwargs['year'],
            version_name=self.kwargs['version_name'],
            is_transition=False)

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def education_group_year(self):
        return self.education_group_version.offer

    @cached_property
    def education_group_version(self):
        return get_object_or_404(
            EducationGroupVersion,
            root_group__academic_year__year=self.kwargs['year'],
            root_group__partial_acronym=self.kwargs['code'],
        )

    def get(self, request, *args, **kwargs):
        form = SpecificVersionForm(
            training_identity=self.training_identity,
            node_identity=self.node_identity,
            program_tree_version=ProgramTreeVersionRepository.get(self.program_tree_version_identity),
            last_year=ProgramTreeVersionRepository.get_last(self.program_tree_version_identity).entity_identity.year
        )
        return render(request, self.template_name, self.get_context_data(form))

    def post(self, request, *args, **kwargs):
        form = SpecificVersionForm(
            data=request.POST,
            training_identity=self.training_identity
        )
        if form.is_valid():
            pass
        return render(request, self.template_name, self.get_context_data(form))

    def _call_rule(self, rule):
        return rule(self.person, self.education_group_year)

    def get_context_data(self, form: SpecificVersionForm):
        return {
            'training_identity': self.training_identity,
            'node_identity': self.node_identity,
            'form': form,
        }

    def get_success_url(self):
        return reverse(
            "training_identification",
            args=[
                self.education_group_year.academic_year.year,
                self.education_group_year.partial_acronym,
            ]
        )

    def _display_success_messages(self, identities: List['ProgramTreeVersionIdentity']):
        success_messages = []
        for created_identity in identities:
            success_messages.append(
                _(
                    "Specific version for education group year %(offer_acronym)s[%(acronym)s] (%(academic_year)s) "
                    "successfully updated."
                ) % {
                    "offer_acronym": created_identity.offer_acronym,
                    "acronym": created_identity.version_name,
                    "academic_year": display_as_academic_year(created_identity.year)
                }
            )
        display_success_messages(self.request, success_messages, extra_tags='safe')
