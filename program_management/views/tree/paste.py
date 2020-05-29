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
import itertools
from typing import List

from django import shortcuts
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import formset_factory
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.views.generic.base import View

import program_management.ddd.command
from base.ddd.utils import business_validator
from base.models.education_group_year import EducationGroupYear
from base.utils.cache import ElementCache
from base.views.common import display_warning_messages
from base.views.mixins import AjaxTemplateMixin
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.domain import node
from program_management.ddd.repositories import node as node_repository
from program_management.ddd.service import attach_node_service
from program_management.ddd.service.read import element_selected_service
from program_management.forms.tree.paste import PasteNodesFormset, paste_form_factory, PasteToMinorMajorListChoiceForm


class PasteNodesView(PermissionRequiredMixin, AjaxTemplateMixin, SuccessMessageMixin, FormView):
    template_name = "tree/paste_inner.html"
    permission_required = "base.attach_educationgroup"

    def has_permission(self):
        return self._has_permission_to_detach() & super().has_permission()

    def _has_permission_to_detach(self) -> bool:
        nodes_to_detach_from = [
            int(element_selected["path_to_detach"].split("|")[-2]) for element_selected in self.nodes_to_paste if element_selected["path_to_detach"]
        ]
        objs_to_detach_from = EducationGroupYear.objects.filter(id__in=nodes_to_detach_from)
        return all(self.request.user.has_perms(("base.detach_educationgroup",), obj_to_detach)
                   for obj_to_detach in objs_to_detach_from)

    def get_permission_object(self) -> EducationGroupYear:
        node_to_paste_to_id = int(self.request.GET['path'].split("|")[-1])
        return shortcuts.get_object_or_404(EducationGroupYear, pk=node_to_paste_to_id)

    @cached_property
    def nodes_to_paste(self) -> List[dict]:
        year = self.request.GET.get("year")
        codes = self.request.GET.getlist("codes", [])
        if codes and year:
            return [{"element_code": code, "element_year": int(year), "path_to_detach": None} for code in codes]
        node_to_paste = element_selected_service.retrieve_element_selected(self.request.user.id)
        return [node_to_paste] if node_to_paste else []

    def get_form_class(self):
        return formset_factory(form=paste_form_factory, formset=PasteNodesFormset, extra=len(self.nodes_to_paste))

    def get_form_kwargs(self) -> List[dict]:
        return [self._get_form_kwargs(element_selected)
                for element_selected in self.nodes_to_paste]

    def _get_form_kwargs(
            self,
            element_selected: dict,
    ) -> dict:
        return {
            'node_to_paste_code': element_selected["element_code"],
            'node_to_paste_year': element_selected["element_year"],
            'path_of_node_to_paste_into': self.request.GET['path'],
            'path_to_detach': element_selected["path_to_detach"],
        }

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(form_kwargs=self.get_form_kwargs(), data=self.request.POST or None)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["formset"] = context_data["form"]
        context_data["is_parent_a_minor_major_list_choice"] = self._is_parent_a_minor_major_list_choice(
            context_data["formset"]
        )
        context_data["nodes_by_id"] = {
            ele["element_code"]: node_repository.NodeRepository.get(
                node.NodeIdentity(ele["element_code"], ele["element_year"])
            ) for ele in self.nodes_to_paste}
        if not self.nodes_to_paste:
            display_warning_messages(self.request, _("Please cut or copy an item before paste"))
        return context_data

    def form_valid(self, formset: PasteNodesFormset):
        node_entities_ids = formset.save()
        if None in node_entities_ids:
            return self.form_invalid(formset)
        ElementCache(self.request.user).clear()

        return super().form_valid(formset)

    def _is_parent_a_minor_major_list_choice(self, formset):
        return any(isinstance(form, PasteToMinorMajorListChoiceForm) for form in formset)

    def get_success_message(self, cleaned_data):
        return _("The content has been updated.")

    def get_success_url(self):
        return


class CheckPasteView(LoginRequiredMixin, View):
    def _retrieve_elements_selected(self) -> List[dict]:
        year = self.request.GET.get("year")
        codes = self.request.GET.getlist("codes", [])
        if codes and year:
            return [{"element_code": code, "element_year": int(year), "path_to_detach": None} for code in codes]
        return []

    def _check_paste(self, element_selected: dict) -> List[str]:
        check_command = program_management.ddd.command.CheckPasteNodeCommand(
            root_id=self.kwargs["root_id"],
            node_to_past_code=element_selected["element_code"],
            node_to_paste_year=element_selected["element_year"],
            path_to_detach=element_selected["path_to_detach"],
            path_to_paste=self.request.GET["path"],
        )

        try:
            attach_node_service.check_paste(check_command)
        except business_validator.BusinessExceptions as business_exception:
            return business_exception.messages
        return []

    def get(self, request, *args, **kwargs):
        elements_to_paste = self._retrieve_elements_selected()
        if not elements_to_paste:
            return JsonResponse({"error_messages": [_("Please cut or copy an item before paste")]})

        error_messages = list(itertools.chain.from_iterable(
            self._check_paste(element) for element in elements_to_paste
        ))
        if error_messages:
            return JsonResponse({"error_messages": error_messages})

        return JsonResponse({"error_messages": []})

