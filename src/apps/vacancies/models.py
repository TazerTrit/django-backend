from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField

from src.apps.vacancies.entities import VacancyEntity
from src.apps.profiles.models.jobseekers import JobSeekerProfile
from src.apps.profiles.models.employers import EmployerProfile
from src.common.models.base import TimedBaseModel


class AvailableManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return Vacancy.objects.filter(open=True)


class Vacancy(TimedBaseModel):
    # Relationships
    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.CASCADE,
        related_name='vacancies',
    )
    interested_candidates = models.ManyToManyField(
        JobSeekerProfile,
        related_name='interested_in',
        blank=True,
    )
    # Fields
    title = models.CharField(
        max_length=300,
    )
    description = models.TextField(
        blank=False,
    )
    salary = models.PositiveIntegerField(
        default=0,
        blank=True,
    )
    location = models.CharField(
        max_length=255,
        default='',
        blank=True,
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    is_remote = models.BooleanField(
        blank=True,
        null=True,
    )
    required_experience = models.PositiveIntegerField(
        blank=True,
        default=0,
    )
    required_skills = ArrayField(
        models.CharField(max_length=30),
        blank=False,
    )
    # Other fields
    open = models.BooleanField(
        default=True,
    )
    slug = models.SlugField(
        blank=True,
        null=False,
        unique_for_date='created_at',
    )
    # Managers
    objects = models.Manager()
    available = AvailableManager()

    class Meta:
        ordering = ('created_at',)
        indexes = (models.Index(fields=['slug']),)
        verbose_name_plural = 'vacancies'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.slug:
            self.slug = self.id  # type: ignore
        self.required_skills = [skill.lower() for skill in self.required_skills]
        return super().save(*args, **kwargs)

    @classmethod
    def from_entity(cls, entity: VacancyEntity) -> 'Vacancy':
        model = cls(
            id=entity.id,
            employer=entity.employer,
            interested_candidates=entity.interested_candidates,
            title=entity.title,
            company_name=entity.company_name,
            description=entity.description,
            is_remote=entity.is_remote,
            required_experience=entity.required_experience,
            location=entity.location,
            required_skills=entity.required_skills,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        return model

    def to_entity(self) -> VacancyEntity:
        candidates = self.interested_candidates.all()
        entity = VacancyEntity(
            id=self.id,  # type: ignore
            employer=self.employer.to_entity(),
            interested_candidates=[cand.to_entity() for cand in candidates],
            title=self.title,
            description=self.description,
            company_name=self.company_name,
            is_remote=self.is_remote,
            required_experience=self.required_experience,
            location=self.location,
            required_skills=self.required_skills,
            updated_at=self.updated_at,
            created_at=self.created_at,
        )
        return entity
