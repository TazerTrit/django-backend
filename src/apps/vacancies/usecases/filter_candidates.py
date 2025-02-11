from dataclasses import dataclass

from src.core.exceptions import VacancyDoesNotExist
from src.apps.profiles.entities.jobseekers import JobSeekerEntity
from src.apps.vacancies.entities import VacancyEntity
from src.apps.vacancies.services.base import BaseVacancyService
from src.apps.vacancies.services.score import ScoreCalculator


@dataclass(eq=False, repr=False, slots=True)
class FilterCandidatesInVacancyUseCase:
    vacancy_service: BaseVacancyService
    score_calculator: ScoreCalculator

    def _filter(
        self,
        interested_candidates: list[JobSeekerEntity],
        vacancy: VacancyEntity,
    ) -> list[JobSeekerEntity]:
        candidates: list[tuple[float, JobSeekerEntity]] = []
        for candidate in interested_candidates:
            score = self.score_calculator.get_candidate_rating(
                candidate=candidate, vacancy=vacancy
            )
            candidates.append((score, candidate))
        sorted_candidates_with_scores = self._sort_by_scores(candidates)
        sorted_candidates = list(
            map(lambda x: x[1], sorted_candidates_with_scores)
        )
        return sorted_candidates

    def _sort_by_scores(
        self,
        candidates: list[tuple[float, JobSeekerEntity]],
    ) -> list[tuple[float, JobSeekerEntity]]:
        sorted_candidates_with_scores = sorted(
            candidates,
            key=lambda x: x[0],
            reverse=True,
        )
        return sorted_candidates_with_scores

    def execute(
        self,
        vacancy_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> list[JobSeekerEntity]:
        vacancy: VacancyEntity | None = self.vacancy_service.get(id=vacancy_id)
        if not vacancy:
            raise VacancyDoesNotExist(vacancy_id)
        interested_candidates = self.vacancy_service.get_list_candidates(
            vacancy_id=vacancy_id,
            offset=offset,
            limit=limit,
        )
        candidates = self._filter(
            interested_candidates=interested_candidates,
            vacancy=vacancy,
        )
        return candidates
