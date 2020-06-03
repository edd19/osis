##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from dal import autocomplete
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.forms import ModelChoiceField, modelformset_factory, BaseModelFormSet
from django.utils.translation import gettext_lazy as _

from base.forms.education_group.common import PermissionFieldTrainingMixin
from base.forms.utils.choice_field import BLANK_CHOICE_DISPLAY
from base.models.education_group_organization import EducationGroupOrganization
from base.models.organization import Organization
from reference.models.country import Country


class CoorganizationEditForm(PermissionFieldTrainingMixin, forms.ModelForm):
    country = ModelChoiceField(
        queryset=Country.objects.filter(organizationaddress__isnull=False).distinct().order_by('name'),
        label=_("Country")
    )

    organization = ModelChoiceField(
        queryset=Organization.objects.all(),
        required=True,
        label=_("Institution"),
        widget=autocomplete.ModelSelect2(
            url='organization_autocomplete',
            attrs={'data-theme': 'bootstrap', 'data-placeholder': BLANK_CHOICE_DISPLAY, 'required': 'required'},
            forward=['country']
        ),
    )

    class Meta:
        model = EducationGroupOrganization
        fields = ['country', 'organization', 'all_students', 'enrollment_place', 'diploma',
                  'is_producing_cerfificate', 'is_producing_annexe']

    class Media:
        css = {
            'all': ('css/select2-bootstrap.css',)
        }
        js = (
            'js/education_group/coorganization.js',
        )

    def __init__(self, education_group_year=None, *args, **kwargs):
        self.user = kwargs.get('user')
        if not education_group_year and not kwargs.get('instance'):
            raise ImproperlyConfigured("Provide an education_group_year or an instance")

        super().__init__(*args, **kwargs)
        if not kwargs.get('instance'):
            self.instance.education_group_year = education_group_year

        if self.instance.pk:
            country = Country.objects.filter(organizationaddress__organization=self.instance.organization).first()
        else:
            country = Country.objects.filter(organizationaddress__isnull=False, iso_code="BE").first()
        self.fields['country'].initial = country.pk

    def check_unique_constraint_between_education_group_year_organization(self):
        qs = EducationGroupOrganization.objects.filter(
            education_group_year=self.instance.education_group_year,
            organization=self.cleaned_data['organization'],
        )
        if self.instance and self.instance.pk:
            qs = qs.exclude(id=self.instance.pk)

        if qs.exists():
            self.add_error('organization', _('There is already a coorganization with this organization'))
            return False
        return True

    def is_valid(self):
        return super(CoorganizationEditForm, self).is_valid() and \
               self.check_unique_constraint_between_education_group_year_organization()


class CoorganizationFormset(BaseModelFormSet):
    def __init__(self, queryset=None, *args, **kwargs):
        super().__init__(queryset=queryset, *args, **kwargs)
        # Have to set empty_permitted to False (by default, it is True for modelformset_factory (not with inlineformset)
        for form in self.forms:
            form.empty_permitted = False


OrganizationFormset = modelformset_factory(
    model=EducationGroupOrganization,
    form=CoorganizationEditForm,
    formset=CoorganizationFormset,
    extra=0,
    can_delete=True
)
