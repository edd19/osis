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

from program_management.ddd.command import UpdateProgramTreeVersionCommand
from program_management.ddd.domain.program_tree_version import STANDARD, UpdateProgramTreeVersiongData, \
    ProgramTreeVersionIdentity
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository


def update_program_tree_version(
        command: 'UpdateProgramTreeVersionCommand',
) -> 'ProgramTreeVersionIdentity':
    identity = ProgramTreeVersionIdentity(
        offer_acronym=command.offer_acronym,
        year=command.year,
        version_name=command.version_name,
        is_transition=command.is_transition,
    )
    program_tree_version = ProgramTreeVersionRepository().get(entity_id=identity)

    program_tree_version.update(__convert_command_to_update_data(command))

    identity = ProgramTreeVersionRepository.update(
        program_tree_version=program_tree_version,
    )

    return identity


def __convert_command_to_update_data(cmd: UpdateProgramTreeVersionCommand) -> 'UpdateProgramTreeVersiongData':
    return UpdateProgramTreeVersiongData(
        title_fr=cmd.title_fr,
        title_en=cmd.title_en,
        end_year_of_existence=cmd.end_year,
    )
