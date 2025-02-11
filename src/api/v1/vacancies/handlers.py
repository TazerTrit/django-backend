from django.http import HttpRequest, HttpResponseBadRequest
from ninja import Query, Router

from core.exceptions import ApplicationException
from src.api.schemas import APIResponseSchema, ListPaginatedResponse
from src.api.v1.profiles.jobseekers.schemas import JobSeekerProfileOut
from src.apps.profiles.filters import JobSeekerFilters
from src.apps.profiles.services.base import BaseJobSeekerService
from src.apps.vacancies.entities import VacancyEntity
from src.apps.vacancies.filters import VacancyFilters
from apps.vacancies.services.vacancy import BaseVacancyService
from src.apps.vacancies.usecases.create_vacancy import CreateVacancyUseCase
from src.apps.vacancies.usecases.filter_candidates import (
    FilterCandidatesInVacancyUseCase,
)

from src.common.container import container
from src.common.filters.pagination import PaginationIn, PaginationOut

from .schemas import VacancyIn, VacancyOut

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
    usecase = container.resolve(CreateVacancyUseCase)
    data = vacancy_data.model_dump()
    employer_id = data.pop('employer_id')
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
    vacancy_id: int,
) -> APIResponseSchema[ListPaginatedResponse[JobSeekerProfileOut]]:
    usecase = container.resolve(FilterCandidatesInVacancyUseCase)
    jobseeker_service = container.resolve(BaseJobSeekerService)
    total = jobseeker_service.get_total_count(
        filters=JobSeekerFilters(vacancy_id=vacancy_id)
    )
    candidates = usecase.execute(
        vacancy_id=vacancy_id,
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
