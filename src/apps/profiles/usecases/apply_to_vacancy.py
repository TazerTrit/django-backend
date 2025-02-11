from dataclasses import dataclass

from src.core.exceptions import (
    CandidateDoesNotExist,
    NotFound,
    VacancyDoesNotExist,
)
from src.apps.vacancies.entities import VacancyEntity
from src.apps.vacancies.services.base import BaseVacancyService
from src.common.services.base import BaseNotificationService


@dataclass(eq=False, repr=False, slots=True)
class ApplyToVacancyUseCase:
    vacancy_service: BaseVacancyService
    notification_service: BaseNotificationService

    def execute(self, candidate_id: int, vacancy_id: int) -> None:
        vacancy: VacancyEntity | None = self.vacancy_service.get(id=vacancy_id)
        if not vacancy:
            raise VacancyDoesNotExist(vacancy_id)

        try:
            self.vacancy_service.add_candidate(
                candidate_id=candidate_id,
                vacancy_id=vacancy_id,
            )
        except NotFound:
            raise CandidateDoesNotExist(candidate_id)

        employer = vacancy.employer
        self.notification_service.send_notification(
            object=employer,
            message=(
                f'Someone applied for your vacancy with title: {vacancy.title}'
            ),
            subject=f'{employer.first_name} {employer.last_name}',
        )
