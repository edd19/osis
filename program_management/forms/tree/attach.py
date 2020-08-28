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

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseModelFormSet, modelformset_factory

from base.models.enums import education_group_categories
from base.models.group_element_year import GroupElementYear
from program_management.business.group_element_years.management import CheckAuthorizedRelationshipAttach


class GroupElementYearForm(forms.ModelForm):
    class Meta:
        model = GroupElementYear
        fields = [
            "relative_credits",
            "is_mandatory",
            "block",
            "link_type",
            "comment",
            "comment_english",
            "access_condition"
        ]
        widgets = {
            "comment": forms.Textarea(attrs={'rows': 5}),
            "comment_english": forms.Textarea(attrs={'rows': 5}),
            "block": forms.TextInput(),
            "relative_credits": forms.TextInput(attrs={'style': 'min-width: 40px;'})
        }

    def __init__(self, *args, parent=None, child_branch=None, child_leaf=None, **kwargs):
        super().__init__(*args, **kwargs)
        # No need to attach FK to an existing GroupElementYear
        if not self.instance.pk:
            self.instance.parent = parent
            self.instance.child_leaf = child_leaf
            self.instance.child_branch = child_branch
            self.initial['relative_credits'] = int(self.instance.child.credits) \
                if self.instance.child and self.instance.child.credits else None

        if self.instance.parent:
            self._define_fields()

    def _define_fields(self):
        if self.instance.child_branch and not self._check_authorized_relationship(
                self.instance.child_branch.education_group_type):
            self.fields.pop("access_condition")

        elif self._is_education_group_year_a_minor_major_option_list_choice(self.instance.parent) and \
                not self._is_education_group_year_a_minor_major_option_list_choice(self.instance.child_branch):
            self._keep_only_fields(["access_condition"])

        elif self.instance.parent.education_group_type.category == education_group_categories.TRAINING and \
                self._is_education_group_year_a_minor_major_option_list_choice(self.instance.child_branch):
            self._disable_all_fields(["block"])

        elif self.instance.child_leaf:
            self.fields.pop("link_type")
            self.fields.pop("access_condition")

        else:
            self.fields.pop("relative_credits")
            self.fields.pop("access_condition")

    def save(self, commit=True):
        return super().save(commit)

    def clean_link_type(self):
        """
        All of these controls only work with child branch.
        The validation with learning_units (child_leaf) is in the model.
        """
        data_cleaned = self.cleaned_data.get('link_type')
        if not self.instance.child_branch:
            return data_cleaned

        link = GroupElementYear(pk=self.instance.pk, child_branch=self.instance.child_branch, link_type=data_cleaned)
        check = CheckAuthorizedRelationshipAttach(
            self.instance.parent,
            link_to_attach=link,
        )
        if not check.is_valid():
            raise ValidationError(check.errors)
        return data_cleaned

    def _check_authorized_relationship(self, child_type):
        return self.instance.parent.education_group_type.authorized_parent_type.filter(child_type=child_type).exists()

    def _disable_all_fields(self, fields_to_not_disable):
        for name, field in self.fields.items():
            if name not in fields_to_not_disable:
                field.disabled = True

    def _keep_only_fields(self, fields_to_keep):
        self.fields = {name: field for name, field in self.fields.items() if name in fields_to_keep}

    @staticmethod
    def _is_education_group_year_a_minor_major_option_list_choice(egy):
        return egy.is_minor_major_option_list_choice if egy else False


class BaseGroupElementYearFormset(BaseModelFormSet):
    def changed_forms(self):
        return [f for f in self if f.has_changed()]

    def save(self, commit=True):
        for f in self:
            f.save()

    def get_form_kwargs(self, index):
        if self.form_kwargs:
            return self.form_kwargs[index]
        return {}


GroupElementYearFormset = modelformset_factory(
    model=GroupElementYear,
    form=GroupElementYearForm,
    formset=BaseGroupElementYearFormset,
    extra=0,
)
