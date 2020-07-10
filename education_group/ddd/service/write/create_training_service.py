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
import attr
from django.db import transaction

from education_group.ddd import command
from education_group.ddd.business_types import *
from education_group.ddd.domain.training import TrainingBuilder
from education_group.ddd.repository.training import TrainingRepository
from education_group.ddd.service.write import create_group_service


@transaction.atomic()
def create_orphan_training(create_training_cmd: command.CreateTrainingCommand) -> 'TrainingIdentity':
    # GIVEN
    command = create_training_cmd

    # WHEN
    training = TrainingBuilder().get_training(create_training_cmd)

    # THEN
    # 1. Create orphan training
    training_id = TrainingRepository.create(training)
    # 2. TODO :: create training until + 6 (postpone)
    # 3. Create orphan group
    group_id = create_group_service.create_orphan_group(__convert_to_group_command(training_cmd=create_training_cmd))
    # 4. TODO :: Create group until +6
    # 5. TODO :: Create programTreeVersion
    # 5.1. TODO :: Create ProgramTree
    # 5.1.1. TODO :: Get orphan root group
    # 5.1.2. TODO :: create mandatory children
    # 5.2. TODO :: create Version


    return training_id


def create_mandatory_children(cmd: CreateMandatoryChildrenCommand) -> List['GroupIdentity']:
    existing_tree = ProgramTreeRepository.get(ProgramTreeIdentity())
    mandatory_types = existing_tree.root_node.get_mandatory_types()

    created_group_identities = []
    for type in mandatory_types:
        created_group_identities.append(create_group_service.create_orphan_group())

    return created_group_identities



def __convert_to_group_command(training_cmd: command.CreateTrainingCommand) -> command.CreateOrphanGroupCommand:
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


def postpone_training(postpone_cmd: command.PostponeTrainingCommand) -> 'TrainingIdentity':
    # attr.evolve(instance, x=25)
    pass


class Point:
    x = attr.ib(type=int)
    y = attr.ib(type=str)

p = Point()