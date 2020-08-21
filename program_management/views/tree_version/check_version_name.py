import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from base.models.enums.education_group_types import TrainingType
from education_group.models.group_year import GroupYear
from osis_common.decorators.ajax import ajax_required
from program_management.models.education_group_version import EducationGroupVersion


@login_required
@ajax_required
def check_version_name(request, year, code):
    version_name = request.GET['version_name']
    existed_version_name = False
    existing_version_name = check_existing_version(version_name, year, code)
    last_using = None
    old_specific_versions = find_last_existed_version(version_name, year, code)
    if old_specific_versions:
        last_using = str(old_specific_versions.offer.academic_year)
        existed_version_name = True
    valid = bool(re.match("^[A-Z]{0,15}$", request.GET['version_name'].upper()))
    return JsonResponse({
        "existed_version_name": existed_version_name,
        "existing_version_name": existing_version_name,
        "last_using": last_using,
        "valid": valid,
        "version_name": request.GET['version_name']}, safe=False)


def check_existing_version(version_name: str, year: int, code: str) -> bool:
    return EducationGroupVersion.objects.filter(
        version_name=version_name.upper(),
        root_group__academic_year__year=year,
        root_group__partial_acronym=code
    ).exists()


def find_last_existed_version(version_name, year, code):
    group_year = GroupYear.objects.get(
        academic_year__year=year,
        partial_acronym=code,
    )
    return EducationGroupVersion.objects.filter(
        version_name=version_name.upper(),
        root_group__academic_year__year__lt=year,
        root_group__acronym=group_year.acronym,
    ).order_by(
        'offer__academic_year'
    ).last()


@login_required
@ajax_required
def check_update_version_name(request, year, code, default_version_name):
    is_a_master = False
    version_name = request.GET['version_name']
    existing_version_name = check_exists_version(default_version_name, version_name, year, code)
    version_name_change = version_name != default_version_name
    valid = bool(re.match("^[A-Z]{0,15}$", request.GET['version_name'].upper()))
    if valid and not existing_version_name:
        is_a_master = get_education_group_version(
            default_version_name, code, year
        ).root_group.education_group_type.name in TrainingType.root_master_2m_types()
    return JsonResponse({
        "existing_version_name": existing_version_name,
        "valid": valid,
        "version_name": request.GET['version_name'],
        "version_name_change": version_name_change,
        "is_a_master": is_a_master,
    }, safe=False)


def check_exists_version(default_version_name: str, version_name: str, year: int, code: str) -> bool:
    group_year = GroupYear.objects.get(
        academic_year__year=year,
        partial_acronym=code,
    )
    return EducationGroupVersion.objects.filter(
        version_name=version_name.upper(),
        root_group__acronym=group_year.acronym
    ).exclude(version_name=default_version_name).exists()


def get_education_group_version(version_name: str, code: str, year: int):
    group_year = GroupYear.objects.get(
        academic_year__year=year,
        partial_acronym=code,
    )
    return EducationGroupVersion.objects.filter(
        version_name=version_name.upper(),
        root_group__acronym=group_year.acronym,
        root_group__academic_year__year=year
    ).first()
