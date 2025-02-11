from logging import Logger, getLogger
from typing import Any

import punq

from src.common.services.base import (
    BaseNotificationService,
)
from src.common.services.notifications import (
    CeleryNotificationService,
    ComposedNotificationService,
    EmailNotificationService,
    PhoneNotificationService,
)
from src.apps.profiles.services.employers import ORMEmployerService
from src.apps.profiles.services.jobseekers import ORMJobSeekerService

from src.apps.vacancies.usecases.create_vacancy import CreateVacancyUseCase
from src.apps.vacancies.usecases.filter_candidates import FilterCandidatesInVacancyUseCase

from src.apps.profiles.usecases.apply_to_vacancy import ApplyToVacancyUseCase
from src.apps.profiles.usecases.update_profile import UpdateJobSeekerProfileUseCase
from src.apps.profiles.services.base import (
    BaseEmployerService,
    BaseJobSeekerService,
)
from src.apps.vacancies.services.vacancies import (
    BaseVacancyService,
    ORMVacancyService,
)


class Container:
    def __init__(self) -> None:
        self.container = self._init()

    def resolve(self, base_cls) -> Any:
        return self.container.resolve(base_cls)

    @staticmethod
    def _init():
        container = punq.Container()

        # Logger
        lg = getLogger('custom')
        container.register(Logger, instance=lg)

        # Notification Service
        celery_notification_service = CeleryNotificationService(
            notification_service=ComposedNotificationService(
                notification_services=(
                    EmailNotificationService(lg),
                    PhoneNotificationService(lg),
                )
            ),
            logger=lg,
        )
        container.register(
            BaseNotificationService,
            instance=celery_notification_service,
        )

        # JobSeeker Profile Service
        orm_jobseeker_service = ORMJobSeekerService(logger=lg)
        container.register(
            BaseJobSeekerService,
            instance=orm_jobseeker_service,
        )

        # Employer Profile Service
        orm_employer_service = ORMEmployerService(logger=lg)
        container.register(
            BaseEmployerService,
            instance=orm_employer_service,
        )

        # Vacancy Service
        orm_vacancy_service = ORMVacancyService(
            jobseeker_service=orm_jobseeker_service,
            employer_service=orm_employer_service,
            logger=lg,
        )
        container.register(
            BaseVacancyService,
            instance=orm_vacancy_service,
        )

        # Use Cases
        container.register(CreateVacancyUseCase)
        container.register(ApplyToVacancyUseCase)
        container.register(FilterCandidatesInVacancyUseCase)
        container.register(UpdateJobSeekerProfileUseCase)

        return container


container = Container()
