from dataclasses import dataclass
from logging import Logger
from typing import Iterable
from django.db.models import Q

from core.exceptions import NotFound
from src.apps.profiles.entities.employers import EmployerEntity
from src.apps.profiles.models.employers import EmployerProfile
from src.apps.profiles.filters import EmployerFilter

from .base import BaseEmployerService


@dataclass
class ORMEmployerService(BaseEmployerService):
    logger: Logger

    def _get_model_or_raise_exception(
        self,
        message: str | None = None,
        related: bool = False,
        **lookup_parameters,
    ) -> EmployerProfile:
        try:
            if related:
                profile = EmployerProfile.objects.select_related('user').get(
                    **lookup_parameters
                )
            else:
                profile = EmployerProfile.objects.get(**lookup_parameters)
        except EmployerProfile.DoesNotExist:
            self.logger.info(
                'Profile not found',
                extra={'info': lookup_parameters},
            )
            if not message:
                raise NotFound('Profile not found')
            raise NotFound(message)
        return profile

    def _build_queryset(self, filters: EmployerFilter) -> Q:
        query = Q()
        if filters.company_name:
            query &= Q(company_name=filters.company_name)
        return query

    def get_list(
        self, filters: EmployerFilter, offset: int, limit: int
    ) -> list[EmployerEntity]:
        query = self._build_queryset(filters)
        employers = EmployerProfile.objects.filter(query)[offset : offset + limit]
        return [employer.to_entity() for employer in employers]

    def get_total_count(self, filters: EmployerFilter) -> int:
        query = self._build_queryset(filters)
        total_count = EmployerProfile.objects.filter(query).count()
        return total_count

    def get_all(self, filters: EmployerFilter) -> Iterable[EmployerEntity]:
        query = self._build_queryset(filters)
        for employer in EmployerProfile.objects.filter(query):
            yield employer.to_entity()

    def get(self, id: int) -> EmployerEntity | None:
        try:
            employer = EmployerProfile.objects.get(id=id)
        except EmployerProfile.DoesNotExist:
            return None
        return employer.to_entity()
