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
from typing import List

from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.models.enums import link_type
from base.models.enums.proposal_type import ProposalType
from program_management.ddd.business_types import *
from program_management.ddd.domain.program_tree import PATH_SEPARATOR
from program_management.models.enums.node_type import NodeType


def serialize_children(children: List['Link'], path: str, context=None) -> List[dict]:
    serialized_children = []
    for link in children:
        child_path = path + PATH_SEPARATOR + str(link.child.pk)
        if link.child.is_learning_unit():
            serialized_node = _leaf_view_serializer(link, child_path, context=context)
        else:
            serialized_node = _get_node_view_serializer(link, child_path, context=context)
        serialized_children.append(serialized_node)
    return serialized_children


def _get_node_view_attribute_serializer(link: 'Link', path: 'Path', context=None) -> dict:
    return {
        'href': reverse('element_identification', args=[link.child.year, link.child.code]) + "?path=%s" % path,
        'root': context['root'].pk,
        'group_element_year': link.pk,
        'element_id': link.child.pk,
        'element_type': link.child.type.name,
        'title': link.child.code,
        'attach_url': reverse('education_group_attach', args=[context['root'].pk, link.child.pk]) + "?path=%s" % path,
        'detach_url': reverse('tree_detach_node', args=[context['root'].pk]) + "?path=%s" % path,
        'modify_url': reverse('group_element_year_update', args=[context['root'].pk, link.child.pk, link.pk]),
        'attach_disabled': False,
        'attach_msg': None,
        'detach_disabled': False,
        'detach_msg': None,
        'modification_disabled': False,
        'modification_msg': None,
        'search_url': reverse('quick_search_education_group', args=[context['root'].pk, path]),
    }


def _get_leaf_view_attribute_serializer(link: 'Link', path: str, context=None) -> dict:
    attrs = _get_node_view_attribute_serializer(link, path, context=context)
    attrs.update({
        'path': path,
        'icon': None,
        'href': reverse('learning_unit_utilization', args=[context['root'].pk, link.child.pk]),
        'attach_url': None,
        'has_prerequisite': link.child.has_prerequisite,
        'is_prerequisite': link.child.is_prerequisite,
        'css_class': __get_css_class(link),
        'element_type': NodeType.LEARNING_UNIT.name,
        'title': __get_title(link),
    })
    return attrs


def __get_css_class(link: 'Link'):
    return {
               ProposalType.CREATION: "proposal proposal_creation",
               ProposalType.MODIFICATION: "proposal proposal_modification",
               ProposalType.TRANSFORMATION: "proposal proposal_transformation",
               ProposalType.TRANSFORMATION_AND_MODIFICATION: "proposal proposal_transformation_modification",
               ProposalType.SUPPRESSION: "proposal proposal_suppression"
           }.get(link.child.proposal_type) or ""


def __get_title(obj: 'Link') -> str:
    title = obj.child.title
    if obj.child.has_prerequisite and obj.child.is_prerequisite:
        title = "%s\n%s" % (title, _("The learning unit has prerequisites and is a prerequisite"))
    elif obj.child.has_prerequisite:
        title = "%s\n%s" % (title, _("The learning unit has prerequisites"))
    elif obj.child.is_prerequisite:
        title = "%s\n%s" % (title, _("The learning unit is a prerequisite"))
    return title


def _get_node_view_serializer(link: 'Link', path: str, context=None) -> dict:
    return {
        'id': path,
        'path': path,
        'icon': _get_group_node_icon(link),
        'text': '%(code)s - %(title)s' % {'code': link.child.code, 'title': link.child.title},
        'children': serialize_children(
            children=link.child.children,
            path=path,
            context=context
        ),
        'a_attr': _get_node_view_attribute_serializer(link, path, context=context),
    }


def _get_group_node_icon(obj: 'Link'):
    if obj.link_type == link_type.LinkTypes.REFERENCE:
        return static('img/reference.jpg')
    return None


def _leaf_view_serializer(link: 'Link', path: str, context=None) -> dict:
    return {
        'id': path,
        'path': path,
        'icon': __get_learning_unit_node_icon(link),
        'text': __get_learning_unit_node_text(link, context=context),
        'a_attr': _get_leaf_view_attribute_serializer(link, path, context=context),
    }


def __get_learning_unit_node_icon(link: 'Link') -> str:
    if link.child.has_prerequisite and link.child.is_prerequisite:
        return "fa fa-exchange-alt"
    elif link.child.has_prerequisite:
        return "fa fa-arrow-left"
    elif link.child.is_prerequisite:
        return "fa fa-arrow-right"
    return "far fa-file"


def __get_learning_unit_node_text(link: 'Link', context=None):
    text = link.child.code
    if context['root'].year != link.child.year:
        text += '|{}'.format(link.child.year)
    return text
