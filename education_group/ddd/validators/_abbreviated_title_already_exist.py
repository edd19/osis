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

from base.ddd.utils import business_validator
from education_group.ddd.business_types import *
from education_group.ddd.domain.exception import AcronymAlreadyExist
from education_group.ddd.domain.service.abbreviated_title_exist import CheckAcronymExist


class AcronymAlreadyExistValidator(business_validator.BusinessValidator):
    def __init__(self, acronym: 'str'):
        super().__init__()
        self.acronym = acronym

    def validate(self, *args, **kwargs):
        if CheckAcronymExist.exists(self.acronym):
            raise AcronymAlreadyExist(self.acronym)