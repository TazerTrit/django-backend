from dataclasses import dataclass

from src.apps.profiles.entities.jobseekers import JobSeekerEntity
from src.apps.profiles.services.base import BaseJobSeekerService


@dataclass
class UpdateJobSeekerProfileUseCase:
    jobseeker_service: BaseJobSeekerService

    def execute(self, profile: JobSeekerEntity) -> JobSeekerEntity:
        updated_profile = self.jobseeker_service.update(entity=profile)
        return updated_profile
