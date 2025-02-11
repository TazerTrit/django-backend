from dataclasses import dataclass

from src.common.services.base import BaseNotificationService
from src.apps.profiles.filters import JobSeekerFilters
from src.apps.profiles.services.base import BaseJobSeekerService
from src.apps.vacancies.entities import VacancyEntity
from src.apps.vacancies.services.base import BaseVacancyService


@dataclass(eq=False, slots=True, repr=False)
class CreateVacancyUseCase:
    vacancy_service: BaseVacancyService
    jobseeker_service: BaseJobSeekerService
    notification_service: BaseNotificationService

    def execute(
        self,
        employer_id: int,
        entity: VacancyEntity,
    ) -> VacancyEntity:
        new_vacancy = self.vacancy_service.create(
            entity=entity, employer_id=employer_id
        )
        filters = JobSeekerFilters(allow_notifications=True)
        jobseekers = self.jobseeker_service.get_all(filters=filters)
        self.notification_service.send_notification_group(
            message='New vacancy with skills that you have appeared!',
            objects=jobseekers,
        )
        return new_vacancy
