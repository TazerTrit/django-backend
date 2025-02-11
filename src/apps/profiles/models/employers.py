from django.db import models

from src.apps.profiles.entities.employers import EmployerEntity

from .base import BaseProfile


class EmployerProfile(BaseProfile):
    company_name = models.CharField(max_length=50)

    def to_entity(self) -> EmployerEntity:
        return EmployerEntity(
            id=self.id,  # type: ignore
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            company_name=self.company_name,
        )

    @classmethod
    def from_entity(cls, entity: EmployerEntity) -> 'EmployerProfile':
        return cls(
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            id=entity.id,
            company_name=entity.company_name,
        )

    def save(self, *args, **kwargs):
        if not self.email:
            if self.user.email:  # type: ignore
                self.email = self.user.email  # type: ignore
        return super().save(*args, **kwargs)
