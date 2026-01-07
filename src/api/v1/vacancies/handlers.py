from django.http import HttpRequest, HttpResponseBadRequest
from ninja import Query, Router
from ninja.security import django_auth

from src.core.exceptions import ApplicationException
from src.api.schemas import APIResponseSchema, ListPaginatedResponse
from src.api.v1.profiles.jobseekers.schemas import JobSeekerProfileOut
from src.apps.profiles.filters import JobSeekerFilters
from src.apps.profiles.services.base import BaseJobSeekerService
from src.apps.vacancies.entities import VacancyEntity
from src.apps.vacancies.filters import VacancyFilters
from src.apps.vacancies.services.vacancy import BaseVacancyService
from src.apps.vacancies.usecases.create_vacancy import CreateVacancyUseCase
from src.apps.vacancies.usecases.filter_candidates import (
    FilterCandidatesInVacancyUseCase,
)

from src.common.container import container
from src.common.filters.pagination import PaginationIn, PaginationOut

from .schemas import VacancyIn, VacancyOut

from src.apps.vacancies.models import Vacancy
from src.apps.profiles.models.jobseekers import JobSeekerProfile
from src.apps.vacancies.models import VacancyInterest



router = Router(tags=['vacancies'])


@router.get('', response=APIResponseSchema[ListPaginatedResponse[VacancyOut]])
def get_vacancy_list(
    request: HttpRequest,
    pagination_in: Query[PaginationIn],
    filters: Query[VacancyFilters],
) -> APIResponseSchema[ListPaginatedResponse[VacancyOut]]:
    service = container.resolve(BaseVacancyService)
    vacancy_entity_list = service.get_list(
        offset=pagination_in.offset,
        limit=pagination_in.limit,
        filters=filters,
    )
    vacancy_count = service.get_total_count(filters=filters)
    vacancy_list = [
        VacancyOut.from_entity(vacancy) for vacancy in vacancy_entity_list
    ]
    pagination_out = PaginationOut(
        total=vacancy_count,
        offset=pagination_in.offset,
        limit=pagination_in.limit,
    )
    response = APIResponseSchema(
        data=ListPaginatedResponse(
            items=vacancy_list,
            pagination=pagination_out,
        )
    )
    return response


@router.post('', response=APIResponseSchema[VacancyOut])
def create_vacancy(
    request: HttpRequest,
    vacancy_data: VacancyIn,
) -> APIResponseSchema[VacancyOut] | HttpResponseBadRequest:
    if not hasattr(request.user, 'employerprofile'):
        return HttpResponseBadRequest(content="Только работодатели могут создавать вакансии")
    usecase = container.resolve(CreateVacancyUseCase)
    data = vacancy_data.model_dump()
    employer_id = data.pop('employer_id')
    if employer_id != request.user.employerprofile.id:
        return HttpResponseBadRequest(content="Нельзя создавать вакансию от чужого имени")
    entity = VacancyEntity(**data)
    try:
        vacancy_entity = usecase.execute(
            entity=entity,
            employer_id=employer_id,
        )
    except ApplicationException:
        return HttpResponseBadRequest()
    return APIResponseSchema(data=VacancyOut.from_entity(vacancy_entity))


@router.get(
    '/{id}/filter',
    response=APIResponseSchema[ListPaginatedResponse[JobSeekerProfileOut]],
)
def filter_candidates_in_vacancy(
    request: HttpRequest,
    pagination_in: Query[PaginationIn],
    id: int,
) -> APIResponseSchema[ListPaginatedResponse[JobSeekerProfileOut]]:
    usecase = container.resolve(FilterCandidatesInVacancyUseCase)
    jobseeker_service = container.resolve(BaseJobSeekerService)
    total = jobseeker_service.get_total_count(
        filters=JobSeekerFilters(vacancy_id=id)
    )
    candidates = usecase.execute(
        vacancy_id=id,
        offset=pagination_in.offset,
        limit=pagination_in.limit,
    )
    data = ListPaginatedResponse(
        items=candidates,
        pagination=PaginationOut(
            total=total,
            offset=pagination_in.offset,
            limit=pagination_in.limit,
        ),
    )
    response = APIResponseSchema(data=data)
    return response

@router.post('/{id}/apply', response=APIResponseSchema[dict], auth=django_auth)
def apply_to_vacancy(
    request: HttpRequest,
    id: int,
    cover_letter: str = '',
):
    try:
        vacancy = Vacancy.objects.get(id=id)
    except Vacancy.DoesNotExist:
        return HttpResponseBadRequest(content="Вакансия не найдена")

    # Проверяем, что пользователь — кандидат
    if not hasattr(request.user, 'jobseekerprofile'):
        return HttpResponseBadRequest(content="Только кандидаты могут откликаться")

    candidate = request.user.jobseekerprofile

    # Проверяем, что профиль существует (на случай редких багов)
    if not candidate:
        return HttpResponseBadRequest(content="У вас нет профиля кандидата")

    # Проверяем, не откликался ли уже
    if VacancyInterest.objects.filter(vacancy=vacancy, candidate=candidate).exists():
        return HttpResponseBadRequest(content="Вы уже откликались на эту вакансию")

    # Создаём отклик
    VacancyInterest.objects.get_or_create(
        vacancy=vacancy,
        candidate=candidate,
        defaults={'cover_letter': cover_letter}
    )

    return APIResponseSchema(data={
        "message": "Отклик отправлен успешно!",
        "candidate": candidate.user.email,
        "vacancy": vacancy.title
    })

@router.patch('/{id}', response=APIResponseSchema[VacancyOut], auth=django_auth)
def update_vacancy(
    request: HttpRequest,
    id: int,
    vacancy_data: VacancyIn,
):
    try:
        vacancy = Vacancy.objects.get(id=id)
    except Vacancy.DoesNotExist:
        return HttpResponseBadRequest("Вакансия не найдена")

    # Защита: только работодатель и владелец вакансии
    if not hasattr(request.user, 'employerprofile'):
        return HttpResponseBadRequest("Только работодатели могут редактировать вакансии")

    if vacancy.employer.user != request.user:
        return HttpResponseBadRequest("Это не ваша вакансия")

    # Обновляем поля
    for field, value in vacancy_data.model_dump(exclude_unset=True).items():
        setattr(vacancy, field, value)
    vacancy.save()

    return APIResponseSchema(data=VacancyOut.from_entity(vacancy.to_entity()))

@router.delete('/{id}', response=APIResponseSchema[dict], auth=django_auth)
def delete_vacancy(request: HttpRequest, id: int):
    try:
        vacancy = Vacancy.objects.get(id=id)
    except Vacancy.DoesNotExist:
        return HttpResponseBadRequest("Вакансия не найдена")

    if not hasattr(request.user, 'employerprofile'):
        return HttpResponseBadRequest("Только работодатели могут удалять вакансии")

    if vacancy.employer.user != request.user:
        return HttpResponseBadRequest("Это не ваша вакансия")

    vacancy.delete()

    return APIResponseSchema(data={"message": "Вакансия удалена"})

@router.get('/{id}/applications', response=APIResponseSchema[list], auth=django_auth)
def get_vacancy_applications(request: HttpRequest, id: int):
    try:
        vacancy = Vacancy.objects.get(id=id)
    except Vacancy.DoesNotExist:
        return HttpResponseBadRequest("Вакансия не найдена")

    if not hasattr(request.user, 'employerprofile'):
        return HttpResponseBadRequest("Только работодатели могут видеть отклики")

    if vacancy.employer.user != request.user:
        return HttpResponseBadRequest("Это не ваша вакансия")

    applications = VacancyInterest.objects.filter(vacancy=vacancy)
    return APIResponseSchema(data=[
        {
            "candidate": app.candidate.user.email,
            "status": app.status,
            "cover_letter": app.cover_letter,
            "created_at": app.created_at
        } for app in applications
    ])


@router.get('/my/applications', response=APIResponseSchema[list], auth=django_auth)
def get_my_applications(request: HttpRequest):
    if not hasattr(request.user, 'jobseekerprofile'):
        return HttpResponseBadRequest("Только кандидаты могут видеть свои отклики")

    candidate = request.user.jobseekerprofile
    applications = VacancyInterest.objects.filter(candidate=candidate)
    return APIResponseSchema(data=[
        {
            "vacancy": app.vacancy.title,
            "status": app.status,
            "cover_letter": app.cover_letter,
            "created_at": app.created_at
        } for app in applications
    ])