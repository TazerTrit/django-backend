from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.postgres.fields import ArrayField

from src.apps.profiles.entities.jobseekers import JobSeekerEntity

from .base import BaseProfile

from django.core.exceptions import ValidationError


class JobSeekerProfile(BaseProfile):
    phone = models.CharField(
        max_length=25,
        blank=False,
    )
    age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(limit_value=18),
            MaxValueValidator(limit_value=100),
        ]
    )
    about_me = models.TextField()
    experience = models.PositiveIntegerField(
        default=0,
    )
    skills = ArrayField(
        models.CharField(max_length=30),
        blank=False,
    )
    allow_notifications = models.BooleanField(
        default=False,
    )
    
    resume = models.FileField(
        upload_to='resumes/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])],
        verbose_name="Резюме",
        help_text="Только PDF, DOC, DOCX. Макс. 10 МБ",
    )

    def clean(self):
        super().clean()
        if self.resume and self.resume.size > 10 * 1024 * 1024:  # 10 МБ
            raise ValidationError("Резюме не должно превышать 10 МБ")

    class Meta:
        ordering = ('-first_name',)

    def save(self, *args, **kwargs):
        self.skills = [skill.lower() for skill in self.skills]
        return super().save(*args, **kwargs)

    def to_entity(self) -> JobSeekerEntity:
        return JobSeekerEntity(
            id=self.id,  # type: ignore
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            age=self.age,
            about_me=self.about_me,
            experience=self.experience,
            skills=self.skills,
            phone=self.phone,
            resume_url=self.resume.url if self.resume else None,
        )

    @classmethod
    def from_entity(cls, entity: JobSeekerEntity) -> 'JobSeekerProfile':
        return cls(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            age=entity.age,
            about_me=entity.about_me,
            experience=entity.experience,
            skills=entity.skills,
            phone=entity.phone,
        )
