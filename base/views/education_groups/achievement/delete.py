############################################################################
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
############################################################################
from django.urls import reverse

from education_group.views.general_information.common import Tab
from osis_role.contrib.views import PermissionRequiredMixin

from base.views.education_groups.achievement.common import EducationGroupAchievementMixin, \
    EducationGroupDetailedAchievementMixin
from base.views.mixins import DeleteViewWithDependencies
from education_group.views.proxy.read import Tab


class DeleteEducationGroupAchievement(PermissionRequiredMixin, DeleteViewWithDependencies,
                                      EducationGroupAchievementMixin):
    template_name = "education_group/delete.html"
    permission_required = 'base.delete_educationgroupachievement'
    raise_exception = True

    def get_permission_object(self):
        return self.education_group_year

    def get_success_url(self):
        if self.education_group_year.category == 'TRAINING':
            return reverse('training_skills_achievements',
                           args=[self.kwargs['year'],
                                 self.kwargs['code']]
                           ) + '?path={}&tab={}'.format(self.request.POST['path'], Tab.SKILLS_ACHIEVEMENTS)
        else:
            return reverse('mini_training_skills_achievements',
                           args=[self.kwargs['year'],
                                 self.kwargs['code']]
                           ) + '?path={}&tab={}'.format(self.request.POST['path'], Tab.SKILLS_ACHIEVEMENTS)


class DeleteEducationGroupDetailedAchievement(PermissionRequiredMixin,
                                              EducationGroupDetailedAchievementMixin, DeleteViewWithDependencies):
    template_name = "education_group/delete.html"
    permission_required = 'base.delete_educationgroupachievement'
    raise_exception = True

    def get_permission_object(self):
        return self.education_group_year
