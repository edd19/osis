##############################################################################
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
##############################################################################
import waffle
from django import template
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from base.business.education_group import can_user_edit_administrative_data
from base.business.education_groups.perms import is_eligible_to_change_education_group, is_eligible_to_add_training, \
    is_eligible_to_add_mini_training, is_eligible_to_add_group, is_eligible_to_postpone_education_group, \
    is_eligible_to_delete_education_group_year, is_eligible_to_edit_certificate_aims, \
    is_eligible_to_change_education_group_content
from base.models.academic_year import AcademicYear
from base.models.enums.education_group_types import GroupType
from base.models.utils.utils import get_verbose_field_value
from base.templatetags.common import ICONS
from program_management.templatetags.group_element_year import get_action_with_permission

register = template.Library()


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_with_deletion_perm(context, url, message, url_id="link_delete"):
    return li_with_permission(context, is_eligible_to_delete_education_group_year, url, message, url_id, True)


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_with_update_perm(context, url, message, url_id="link_update"):
    person = context['person']

    if person.is_program_manager and \
            not any((person.user.is_superuser, person.is_faculty_manager, person.is_central_manager)):
        return li_with_permission(context, is_eligible_to_edit_certificate_aims, url, message, url_id, load_modal=True)

    return li_with_permission(context, is_eligible_to_change_education_group, url, message, url_id)


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_with_create_perm_training(context, url, message, url_id="link_create_training"):
    return li_with_permission(context, is_eligible_to_add_training, url, message, url_id, True)


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_with_create_perm_mini_training(context, url, message, url_id="link_create_mini_training"):
    return li_with_permission(context, is_eligible_to_add_mini_training, url, message, url_id, True)


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_with_create_perm_group(context, url, message, url_id="link_create_group"):
    return li_with_permission(context, is_eligible_to_add_group, url, message, url_id, True)


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_with_postpone_perm_training(context, url_id="link_postpone_training"):
    root = context['root']
    education_group_year = context['education_group_year']
    url = reverse('postpone_education_group', args=[root.pk, education_group_year.pk])

    try:
        last_academic_year = education_group_year.academic_year.past()
    except AcademicYear.DoesNotExist:
        last_academic_year = "last year"

    message = _('Copy the content from %(previous_anac)s to %(current_anac)s') % {
        'previous_anac': str(last_academic_year),
        'current_anac': str(education_group_year.academic_year)

    }
    return li_with_permission(context, is_eligible_to_postpone_education_group, url, message, url_id, True)


def li_with_permission(context, permission, url, message, url_id, load_modal=False):
    permission_denied_message, disabled, root = _get_permission(context, permission)

    if not disabled:
        href = url
    else:
        href = "#"
        load_modal = False
    return {
        "class_li": disabled,
        "load_modal": load_modal,
        "url": href,
        "id_li": url_id,
        "title": permission_denied_message,
        "text": message,
    }


def _get_permission(context, permission):
    permission_denied_message = ""

    education_group_year = context.get('education_group_year')
    person = context.get('person')
    root = context.get("root") or context.get("parent")

    try:
        result = permission(person, education_group_year, raise_exception=True)

    except PermissionDenied as e:
        result = False
        permission_denied_message = str(e)
    return permission_denied_message, "" if result else "disabled", root


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def button_edit_administrative_data(context):
    education_group_year = context.get('education_group_year')

    permission_denied_message, is_disabled, root = _get_permission(context, can_user_edit_administrative_data)
    if not permission_denied_message and is_disabled:
        permission_denied_message = _("Only program managers of the education group OR "
                                      "central manager linked to entity can edit.")

    return {
        'class_li': is_disabled,
        'title': permission_denied_message,
        'text': _('Modify'),
        'url': '#' if is_disabled else
        reverse('education_group_edit_administrative', args=[root.pk, education_group_year.pk])
    }


@register.inclusion_tag("blocks/button/button_order.html", takes_context=True)
def button_order_with_permission(context, title, id_button, value):
    permission_denied_message, disabled, root = _get_permission(
        context, is_eligible_to_change_education_group_content
    )

    if disabled:
        title = permission_denied_message
    else:
        education_group_year = context.get('education_group_year')
        person = context.get('person')

        if person.is_faculty_manager and education_group_year.type in GroupType.minor_major_list_choice():
            disabled, permission_denied_message = get_action_with_permission(context)
            if disabled:
                title = permission_denied_message

    if value == "up" and context["forloop"]["first"]:
        disabled = "disabled"

    if value == "down" and context["forloop"]["last"]:
        disabled = "disabled"

    return {
        'title': title,
        'id': id_button,
        'value': value,
        'disabled': disabled,
        'icon': ICONS[value],
    }


@register.simple_tag(takes_context=True)
def url_resolver_match(context):
    return context.request.resolver_match.url_name


@register.simple_tag(takes_context=True)
def link_detach_education_group(context, url):
    onclick = """onclick="select()" """
    action = "Detach"
    if context['can_change_education_group'] and context['group_to_parent'] != '0':
        li_attributes = """ id="btn_operation_detach_{group_to_parent}" class="trigger_modal" data-url={url} """.format(
            group_to_parent=context['group_to_parent'],
            url=url,
        )
        a_attributes = """ href="#" title="{title}" {onclick} """.format(title=_(action), onclick=onclick)
    else:
        li_attributes = """ class="disabled" """
        title = ""
        if not context['can_change_education_group']:
            title += _("The user has not permission to change education groups.")
        if context['group_to_parent'] == '0':
            title += " " + _("It is not possible to %(action)s the root element.") % {
                "action": str.lower(_(action))
            }

        a_attributes = """ title="{title}" """.format(title=title)
    text = _(action)
    html_template = """
        <li {li_attributes}>
            <a {a_attributes} data-toggle="tooltip">{text}</a>
        </li>
    """

    return mark_safe(
        html_template.format(
            li_attributes=li_attributes,
            a_attributes=a_attributes,
            text=text,
        )
    )


@register.inclusion_tag('blocks/button/li_template.html')
def link_pdf_content_education_group(url):
    action = _("Generate pdf")
    if waffle.switch_is_active('education_group_year_generate_pdf'):
        disabled = ''
        title = action
        load_modal = True
    else:
        disabled = 'disabled'
        title = _('Generate PDF not available. Please use EPC.')
        load_modal = False
        url = '#'

    return {
        "class_li": disabled,
        "load_modal": load_modal,
        "url": url,
        "id_li": "btn_operation_pdf_content",
        "title": title,
        "text": action,
    }


@register.inclusion_tag("blocks/dl/dl_with_parent.html", takes_context=True)
def dl_with_parent(context, key, dl_title="", class_dl="", default_value=None):
    """
    Tag to render <dl> for details of education_group.
    If the fetched value does not exist for the current education_group_year,
    the method will try to fetch the parent's value and display it in another style
    (strong, blue).
    """
    obj = context["education_group_year"]
    parent = context["parent"]

    return dl_with_parent_without_context(key, obj, parent, dl_title=dl_title, class_dl=class_dl,
                                          default_value=default_value)


@register.inclusion_tag("blocks/dl/dl_with_parent.html", takes_context=False)
def dl_with_parent_without_context(key, obj, parent, dl_title="", class_dl="", default_value=None):
    value = None
    parent_value = None
    if obj:
        value = get_verbose_field_value(obj, key)

        if not dl_title:
            dl_title = obj._meta.get_field(key).verbose_name

        if value is None or value == "":
            parent_value = get_verbose_field_value(parent, key)
        else:
            parent, parent_value = None, None

    return {
        'label': _(dl_title),
        'value': _bool_to_string(value),
        'parent_value': _bool_to_string(parent_value),
        'class_dl': class_dl,
        'default_value': default_value,
    }


def _bool_to_string(value):
    if value is None:
        return value

    # In this case, None has a different value meaning than usual (maybe)
    if isinstance(value, bool):
        return "yes" if value else "no"

    return str(value)
