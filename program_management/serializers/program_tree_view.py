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
from rest_framework import serializers

from program_management.serializers.node_view import ChildrenField
from program_management.ddd.business_types import *


class ProgramTreeViewSerializer(serializers.Serializer):
    text = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    children = ChildrenField(source='root_node.children', many=True)

    def __init__(self, instance: 'ProgramTree', **kwargs):
        kwargs['context'] = {
            **kwargs.get('context', {}),
            'root': instance.root_node,
            'path': str(instance.root_node.pk)
        }
        super().__init__(instance, **kwargs)

    def get_icon(self, tree: 'ProgramTree'):
        return None

    def get_text(self, obj: 'ProgramTree'):
        return '%(acronym)s - %(title)s' % {'acronym': obj.root_node.acronym, 'title': obj.root_node.title}
