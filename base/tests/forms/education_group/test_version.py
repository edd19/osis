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

from django.test import TestCase
from django.utils import timezone

from base.forms.education_group.version import SpecificVersionForm
from base.tests.factories.academic_year import AcademicYearFactory
from education_group.tests.ddd.factories.training import TrainingIdentityFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory


class TestSpecificVersionForm(TestCase):
    def setUp(self):
        AcademicYearFactory.produce(base_year=2020, number_past=10, number_future=10)
        self.training_identity = TrainingIdentityFactory(year=timezone.now().year)
        self.program_tree_version = ProgramTreeVersionFactory()

    def test_init(self):
        form = SpecificVersionForm(
            program_tree_version=self.program_tree_version,
            training_identity=self.training_identity
        )
        self.assertEqual(form.fields["end_year"].choices[0][0], None)
        self.assertEqual(form.fields["version_name"].initial, self.program_tree_version.version_name)
        self.assertEqual(form.fields["title"].initial, self.program_tree_version.title_fr)
        self.assertEqual(form.fields["title_english"].initial, self.program_tree_version.title_en)


