##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils import translation
from base import models as mdl
from base.views import layout
from django.utils.translation import ugettext as _

@login_required
def my_osis_index(request):
    return layout.render(request, "my_osis/my_osis_home.html", {})


@login_required
def my_messages_index(request):
    person = mdl.person.find_by_user(request.user)
    my_messages = mdl.message_history.find_my_messages(person)
    if not my_messages:
        messages.add_message(request, messages.INFO, _('no_messages'))
    return layout.render(request, "my_osis/my_messages.html", {'my_messages': my_messages, })


@login_required
def delete_from_my_messages(request,message_id):
    mdl.message_history.delete_my_message(message_id)
    return my_messages_index(request)


@login_required
def read_message(request, message_id):
    message = mdl.message_history.find_by_id(message_id).update(read_in_myosis=True)
    return layout.render(request, "my_osis/my_message.html", {'my_message': message, })



@login_required
def profile(request):
    person = mdl.person.find_by_user(request.user)
    addresses = mdl.person_address.find_by_person(person)
    tutor = mdl.tutor.find_by_person(person)
    attributions = mdl.attribution.search(tutor=tutor)
    student = mdl.student.find_by_person(person)
    offer_enrollments = mdl.offer_enrollment.find_by_student(student)
    programs_managed = mdl.program_manager.find_by_person(person)
    return layout.render(request, "my_osis/profile.html", {'person':                person,
                                                           'addresses':             addresses,
                                                           'tutor':                 tutor,
                                                           'attributions':          attributions,
                                                           'student':               student,
                                                           'offer_enrollments':     offer_enrollments,
                                                           'programs_managed':      programs_managed,
                                                           'supported_languages':   settings.LANGUAGES,
                                                           'default_language':      settings.LANGUAGE_CODE})


@login_required
def profile_lang(request):
    ui_language = request.POST.get('ui_language')
    mdl.person.change_language(request.user, ui_language)
    translation.activate(ui_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = ui_language
    return profile(request)


@login_required
@user_passes_test(lambda u: u.has_perm('base.management_tasks') and u.has_perm('base.change_messagetemplate'))
def messages_templates_index(request):
    return HttpResponseRedirect(reverse('admin:base_messagetemplate_changelist'))


