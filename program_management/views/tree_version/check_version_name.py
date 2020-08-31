import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from base.models.enums.education_group_types import TrainingType
from education_group.models.group_year import GroupYear
from education_group.templatetags.academic_year_display import display_as_academic_year
from osis_common.decorators.ajax import ajax_required
from program_management.ddd.command import GetLastExistingVersionNameCommand
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.service.read import get_last_existing_version_service
from program_management.models.education_group_version import EducationGroupVersion


@login_required
@ajax_required
@require_http_methods(['GET'])
def check_version_name(request, year, code):
    version_name = request.GET['version_name']
    existed_version_name = False
    existing_version = __get_last_existing_version(version_name, code)
    last_using = None
    if existing_version and existing_version.year < year:
        last_using = display_as_academic_year(existing_version.year)
        existed_version_name = True
    valid = bool(re.match("^[A-Z]{0,15}$", request.GET['version_name'].upper()))
    return JsonResponse({
        "existed_version_name": existed_version_name,
        "existing_version_name": bool(existing_version and existing_version.year >= year),
        "last_using": last_using,
        "valid": valid,
        "version_name": request.GET['version_name']}, safe=False)


def __get_last_existing_version(version_name: str, offer_acronym: str) -> ProgramTreeVersionIdentity:
    return get_last_existing_version_service.get_last_existing_version_identity(
        GetLastExistingVersionNameCommand(
            version_name=version_name.upper(),
            offer_acronym=offer_acronym.upper(),
            is_transition=False,
        )
    )


@login_required
@ajax_required
def check_update_version_name(request, year, code, default_version_name):
    version_name = request.GET['version_name']
    is_a_master = False
    existing_version = __get_last_existing_version(version_name, code)
    version_name_change = version_name != default_version_name
    valid = bool(re.match("^[A-Z]{0,15}$", request.GET['version_name'].upper()))
    if valid and not existing_version:
        program_tree_version = ProgramTreeVersionRepository().get(
            __get_last_existing_version("", code)
        )
        program_tree = program_tree_version.get_tree()
        is_a_master = program_tree.is_master_2m()
    return JsonResponse({
        "existing_version_name": existing_version and version_name_change,
        "valid": valid,
        "version_name": request.GET['version_name'],
        "version_name_change": version_name_change,
        "is_a_master": is_a_master,
    }, safe=False)
