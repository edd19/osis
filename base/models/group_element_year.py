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
from collections import Counter

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, connection
from django.db.models import Q
from django.utils import translation
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel
from reversion.admin import VersionAdmin

from backoffice.settings.base import LANGUAGE_CODE_EN
from base.models.education_group_year import EducationGroupYear
from base.models.enums import quadrimesters
from base.models.enums.education_group_types import GroupType, MiniTrainingType, TrainingType
from base.models.enums.link_type import LinkTypes
from base.utils.db import dict_fetchall
from osis_common.models.osis_model_admin import OsisModelAdmin
from program_management.models.element import Element

COMMON_FILTER_TYPES = [MiniTrainingType.OPTION.name]
DEFAULT_ROOT_TYPES = TrainingType.get_names() + MiniTrainingType.get_names()


class GroupElementYearAdmin(VersionAdmin, OsisModelAdmin):
    list_display = ('parent', 'child_branch', 'child_leaf',)
    readonly_fields = ('order',)
    search_fields = [
        'child_branch__acronym',
        'child_branch__partial_acronym',
        'child_leaf__acronym',
        'parent__acronym',
        'parent__partial_acronym'
    ]
    list_filter = ('is_mandatory', 'access_condition', 'parent__academic_year')


def validate_block_value(value):
    max_authorized_value = 6
    _error_msg = _(
        "Please register a maximum of %(max_authorized_value)s digits in ascending order, "
        "without any duplication. Authorized values are from 1 to 6. Examples: 12, 23, 46"
    ) % {'max_authorized_value': max_authorized_value}

    MinValueValidator(1, message=_error_msg)(value)
    if not all([
        _check_integers_max_authorized_value(value, max_authorized_value),
        _check_integers_duplications(value),
        _check_integers_orders(value),
    ]):
        raise ValidationError(_error_msg)


def _check_integers_max_authorized_value(value, max_authorized_value):
    return all(int(char) <= max_authorized_value for char in str(value))


def _check_integers_duplications(value):
    if any(integer for integer, occurence in Counter(str(value)).items() if occurence > 1):
        return False
    return True


def _check_integers_orders(value):
    digit_values = [int(char) for char in str(value)]
    return list(sorted(digit_values)) == digit_values


class GroupElementYearManager(models.Manager):
    def get_adjacency_list(self, root_elements_ids):
        if not isinstance(root_elements_ids, list):
            raise Exception('root_elements_ids must be an instance of list')
        if not root_elements_ids:
            return []

        adjacency_query_template = """
            WITH RECURSIVE
                adjacency_query AS (
                    SELECT
                        parent_element_id as starting_node_id,
                        id,
                        child_element_id,
                        parent_element_id,
                        "order",
                        0 AS level,
                        CAST(parent_element_id || '|' ||
                            (
                                child_element_id
                            ) as varchar(1000)
                        ) As path
                    FROM base_groupelementyear
                    WHERE parent_element_id IN %(root_element_ids)s

                    UNION ALL

                    SELECT parent.starting_node_id,
                           child.id,
                           child.child_element_id,
                           child.parent_element_id,
                           child.order,
                           parent.level + 1,
                           CAST(
                                parent.path || '|' ||
                                    (
                                        child.child_element_id
                                    ) as varchar(1000)
                               ) as path
                    FROM base_groupelementyear AS child
                    INNER JOIN adjacency_query AS parent on parent.child_element_id = child.parent_element_id
                )
            SELECT distinct starting_node_id, adjacency_query.id, parent_element_id as parent_id,
                   child_element_id AS child_id, "order", level, path
            FROM adjacency_query
            JOIN program_management_element elem on elem.id = adjacency_query.child_element_id
            LEFT JOIN base_learningunityear bl on bl.id = elem.learning_unit_year_id
            WHERE bl.id is null or bl.learning_container_year_id is not null
            ORDER BY starting_node_id, level, "order";
        """
        parameters = {
            "root_element_ids": tuple(root_elements_ids)
        }
        return self.fetch_all(adjacency_query_template, parameters)

    def get_reverse_adjacency_list(
            self,
            child_element_ids=None,
            academic_year_id=None,
            link_type: LinkTypes = None
    ):
        if not isinstance(child_element_ids, list):
            raise Exception('child_element_ids must be an instance of list')
        if not child_element_ids:
            return []

        where_statement = self.__build_where_statement(None, child_element_ids)

        reverse_adjacency_query_template = """
            WITH RECURSIVE
                reverse_adjacency_query AS (
                    SELECT
                           gey.child_element_id as starting_node_id,
                           gey.id,
                           gey.child_element_id,
                           gey.parent_element_id,
                           gey.order,
                           gpyc.academic_year_id,
                           0 AS level
                    FROM base_groupelementyear gey
                    INNER JOIN program_management_element elem on elem.id = gey.parent_element_id
                    INNER JOIN education_group_groupyear AS gpyc on elem.group_year_id = gpyc.id
                    WHERE {where_statement}
                    AND (%(link_type)s IS NULL or gey.link_type = %(link_type)s)

                    UNION ALL

                    SELECT 	child.starting_node_id,
                            parent.id,
                            parent.child_element_id,
                            parent.parent_element_id,
                            parent.order,
                            gpyp.academic_year_id,
                            child.level + 1
                    FROM base_groupelementyear AS parent
                    INNER JOIN reverse_adjacency_query AS child on parent.child_element_id = child.parent_element_id
                    INNER JOIN program_management_element elem on elem.id = parent.parent_element_id
                    INNER JOIN education_group_groupyear AS gpyp on elem.group_year_id = gpyp.id
                )

            SELECT distinct starting_node_id, id, parent_element_id AS parent_id, child_element_id AS child_id, 
                            "order", level
            FROM reverse_adjacency_query
            WHERE %(academic_year_id)s IS NULL OR academic_year_id = %(academic_year_id)s
            ORDER BY starting_node_id,  level DESC, "order";
        """.format(where_statement=where_statement)

        parameters = {
            "child_element_ids": tuple(child_element_ids),
            "link_type": link_type.name if link_type else None,
            "academic_year_id": academic_year_id,
        }
        return self.fetch_all(reverse_adjacency_query_template, parameters)

    def get_root_list(
            self,
            child_element_ids=None,
            academic_year_id=None,
            link_type: LinkTypes = None,
            root_category_name=None
    ):
        root_category_name = root_category_name or []
        child_element_ids = child_element_ids or []
        if not isinstance(child_element_ids, list):
            raise Exception('child_element_ids must be an instance of list')

        if not len(child_element_ids) and not academic_year_id:
            return []

        where_statement = self.__build_where_statement(academic_year_id, child_element_ids)
        root_query_template = """
            WITH RECURSIVE
                root_query AS (
                    SELECT
                        gey.child_element_id as starting_node_id,
                        gey.id,
                        gey.child_element_id,
                        gey.parent_element_id,
                        gpyp.academic_year_id,
                        CASE
                            WHEN egt.name in %(root_categories_names)s THEN true
                            ELSE false
                          END as is_root_row
                    FROM base_groupelementyear gey
                    INNER JOIN program_management_element parent_elem on parent_elem.id = gey.parent_element_id

                    INNER JOIN education_group_groupyear AS gpyp on parent_elem.group_year_id = gpyp.id
                    INNER JOIN base_educationgrouptype AS egt on gpyp.education_group_type_id = egt.id

                    INNER JOIN program_management_element child_element on child_element.id = gey.child_element_id
                    LEFT JOIN base_learningunityear bl on child_element.learning_unit_year_id = bl.id
                    LEFT JOIN education_group_groupyear AS gpyc on parent_elem.group_year_id = gpyc.id
                    WHERE {where_statement}  AND
                          (%(link_type)s IS NULL or gey.link_type = %(link_type)s)

                    UNION ALL

                    SELECT 	child.starting_node_id,
                      parent.id,
                      parent.child_element_id,
                      parent.parent_element_id,
                      gpyp.academic_year_id,
                      CASE
                        WHEN egt.name in %(root_categories_names)s THEN true
                        ELSE false
                      END as is_root_row
                    FROM base_groupelementyear AS parent
                    INNER JOIN root_query AS child on parent.child_element_id = child.parent_element_id
                    and child.is_root_row = false

                    INNER JOIN program_management_element parent_elem on parent_elem.id = parent.parent_element_id
                    INNER JOIN education_group_groupyear gpyp on parent_elem.group_year_id = gpyp.id
                    INNER JOIN base_educationgrouptype AS egt on gpyp.education_group_type_id = egt.id
                )

            SELECT distinct starting_node_id AS child_id, parent_element_id AS root_id
            FROM root_query
            WHERE (%(academic_year_id)s IS NULL OR academic_year_id = %(academic_year_id)s) AND
                  (is_root_row is not Null and is_root_row = true)
            ORDER BY starting_node_id;
        """.format(where_statement=where_statement)

        parameters = {
            "child_element_ids": tuple(child_element_ids),
            "link_type": link_type.name if link_type else None,
            "academic_year_id": academic_year_id,
            "root_categories_names": tuple(root_category_name)

        }
        return self.fetch_all(root_query_template, parameters)

    def fetch_all(self, query_template, parameters):
        with connection.cursor() as cursor:
            cursor.execute(query_template, parameters)
            return dict_fetchall(cursor)

    def __build_where_statement(self, academic_year_id, child_element_ids):
        where_statement_element = "child_element_id in %(child_element_ids)s" if child_element_ids else ""
        where_statement_academic_year = "(gpyc.academic_year_id = %(academic_year_id)s " \
                                        "OR bl.academic_year_id = %(academic_year_id)s)"
        if academic_year_id:
            return where_statement_academic_year
        elif child_element_ids:
            return where_statement_element


class GroupElementYear(OrderedModel):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    parent_element = models.ForeignKey(
        Element,
        related_name='parent_elements',
        null=True,  # TODO: To remove after data migration
        on_delete=models.PROTECT,
    )

    child_element = models.ForeignKey(
        Element,
        related_name='children_elements',
        null=True,  # TODO: To remove after data migration
        on_delete=models.PROTECT,
    )

    parent = models.ForeignKey(
        EducationGroupYear,
        null=True,  # TODO: can not be null, dirty data
        on_delete=models.PROTECT,
    )

    child_branch = models.ForeignKey(
        EducationGroupYear,
        related_name='child_branch',  # TODO: can not be child_branch
        blank=True, null=True,
        on_delete=models.CASCADE,
    )

    child_leaf = models.ForeignKey(
        'LearningUnitYear',
        related_name='child_leaf',  # TODO: can not be child_leaf
        blank=True, null=True,
        on_delete=models.CASCADE,
    )

    relative_credits = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("relative credits"),
    )

    min_credits = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("Min. credits"),
    )

    max_credits = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("Max. credits"),
    )

    is_mandatory = models.BooleanField(
        default=True,
        verbose_name=_("Mandatory"),
    )

    block = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("Block"),
        validators=[validate_block_value]
    )

    access_condition = models.BooleanField(
        default=False,
        verbose_name=_('Access condition')
    )

    comment = models.TextField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("comment"),
    )
    comment_english = models.TextField(
        max_length=500,
        blank=True, null=True,
        verbose_name=_("english comment"),
    )

    own_comment = models.CharField(max_length=500, blank=True, null=True)

    quadrimester_derogation = models.CharField(
        max_length=10,
        choices=quadrimesters.DerogationQuadrimester.choices(),
        blank=True, null=True, verbose_name=_('Quadrimester derogation')
    )

    link_type = models.CharField(
        max_length=25,
        choices=LinkTypes.choices(),
        blank=True, null=True, verbose_name=_('Link type')
    )

    order_with_respect_to = 'parent'

    objects = GroupElementYearManager()

    def __str__(self):
        return "{} - {}".format(self.parent, self.child)

    @property
    def verbose_comment(self):
        if self.comment_english and translation.get_language() == LANGUAGE_CODE_EN:
            return self.comment_english
        return self.comment

    class Meta:
        unique_together = (('parent', 'child_branch'), ('parent', 'child_leaf'))
        ordering = ('order',)

    # DEPRECATED Move all those validations into forms with ddd validators
    def clean(self):
        if self.child_branch and self.child_leaf:
            raise ValidationError(_("It is forbidden to save a GroupElementYear with a child branch and a child leaf."))

        if self.child_branch == self.parent:
            raise ValidationError(_("It is forbidden to add an element to itself."))

        if self.parent and self.child_branch in self.parent.ascendants_of_branch:
            raise ValidationError(_("It is forbidden to add an element to one of its included elements."))

        if self.child_leaf and self.link_type == LinkTypes.REFERENCE.name:
            raise ValidationError(
                {'link_type': _("You are not allowed to create a reference with a learning unit")}
            )
        self._check_same_academic_year_parent_child_branch()

    def _check_same_academic_year_parent_child_branch(self):
        if (self.parent and self.child_branch) and \
                (self.parent.academic_year.year != self.child_branch.academic_year.year):
            raise ValidationError(_("It is prohibited to attach a group, mini-training or training to an element of "
                                    "another academic year."))

        self._clean_link_type()

    def _clean_link_type(self):
        if getattr(self.parent, 'type', None) in [GroupType.MINOR_LIST_CHOICE.name,
                                                  GroupType.MAJOR_LIST_CHOICE.name] and \
                isinstance(self.child, EducationGroupYear) and self.child.type in MiniTrainingType.minors() + \
                [MiniTrainingType.FSA_SPECIALITY.name, MiniTrainingType.DEEPENING.name]:
            self.link_type = LinkTypes.REFERENCE.name

    @cached_property
    def child(self):
        return self.child_branch or self.child_leaf


def fetch_row_sql(root_ids):
    return GroupElementYear.objects.get_adjacency_list(root_ids)
