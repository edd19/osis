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

from django.db import transaction

from education_group.ddd.repository.group import GroupRepository
from program_management.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain.training import TrainingBuilder
from education_group.ddd.repository.training import TrainingRepository
from education_group.ddd.service.write import create_group_service
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionBuilder
from program_management.ddd.repositories.program_tree import ProgramTreeRepository


@transaction.atomic()
def create_standard_program_version(create_standard_cmd: command.CreateStandardVersionCommand) -> 'TrainingIdentity':
    group_identity = GroupIdentity(code=create_standard_cmd.code, year=create_standard_cmd.year)
    root_group = GroupRepository().get(entity_id=group_identity)

    program_tree_version = ProgramTreeVersionBuilder().build_standard_version(
        cmd=create_standard_cmd,
        tree_repository=ProgramTreeRepository()
    )

    
    return training_id


def __get_create_group_command(training_cmd: command.CreateTrainingCommand) -> command.CreateOrphanGroupCommand:
    return command.CreateOrphanGroupCommand(
        code=training_cmd.code,
        year=training_cmd.year,
        type=training_cmd.type,
        abbreviated_title=training_cmd.abbreviated_title,
        title_fr=training_cmd.title_fr,
        title_en=training_cmd.title_en,
        credits=training_cmd.credits,
        constraint_type=training_cmd.constraint_type,
        min_constraint=training_cmd.min_constraint,
        max_constraint=training_cmd.max_constraint,
        management_entity_acronym=training_cmd.management_entity_acronym,
        teaching_campus_name=training_cmd.teaching_campus_name,
        organization_name=training_cmd.teaching_campus_organization_name,
        remark_fr=training_cmd.remark_fr,
        remark_en=training_cmd.remark_en,
        start_year=training_cmd.year,
        end_year=training_cmd.end_year,
    )