from typing import List

from django.utils.functional import cached_property
from reversion.models import Version

from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.repository.training import TrainingRepository
from education_group.views.training.common_read import TrainingRead, Tab
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.business_types import *
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository


class TrainingReadIdentification(TrainingRead):
    template_name = "training/identification_read.html"
    active_tab = Tab.IDENTIFICATION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "all_versions_available": self.all_versions_available,
            "current_version": self.current_version,  # Template : panel_version_information.html
            "education_group_year": self.get_training(),
            # "history": self.get_related_versions(),
        }

    @cached_property
    def all_versions_available(self) -> List['ProgramTreeVersion']:
        return ProgramTreeVersionRepository.search_all_versions_from_root_node(
            NodeIdentity(self.get_tree().root_node.code, self.get_tree().root_node.year)
        )

    @cached_property
    def current_version(self):
        current_version_name = self.education_group_version.version_name
        is_transition = self.education_group_version.is_transition
        return next(
            (
                version for version in self.all_versions_available
                if version.version_name == current_version_name and version.is_transition == is_transition
            ),
            None
        )

    def get_related_history(self):
        return Version.objects.none()

    def get_training(self):
        offer = self.education_group_version.offer
        return TrainingRepository.get(TrainingIdentity(acronym=offer.acronym, year=offer.academic_year.year))
