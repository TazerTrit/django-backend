from src.apps.profiles.entities.jobseekers import JobSeekerEntity
from src.apps.vacancies.entities import VacancyEntity


class ScoreCalculator:
    def __init__(
        self,
        required_experience_score: float = 7.0,
        incr_score_if_experience_higher: bool = True,
        skill_matched_score: float = 2.0,
        skill_didnt_match_score: float = 2.0,
    ) -> None:
        self.required_experience_score: float = required_experience_score
        self.incr_score_if_experience_higher: bool = (
            incr_score_if_experience_higher
        )
        self.skill_matched_score: float = skill_matched_score
        self.skill_didnt_match_score: float = skill_didnt_match_score

    def calculate_score_from_experience(
        self,
        candidate_experience: int,
        vacancy_required_experience: int,
    ) -> float:
        score = 0
        if candidate_experience >= vacancy_required_experience:
            score = self.required_experience_score
            if self.incr_score_if_experience_higher:
                score += candidate_experience - vacancy_required_experience
        return score

    def calculate_score_from_skills(
        self,
        candidate_skills: list[str],
        vacancy_required_skills: list[str],
    ) -> float:
        score = 0
        for skill in candidate_skills:
            if skill in vacancy_required_skills:
                score += self.skill_matched_score
            else:
                score += self.skill_didnt_match_score
        return score

    def get_candidate_rating(
        self,
        candidate: JobSeekerEntity,
        vacancy: VacancyEntity,
    ) -> float:
        rating = 0
        rating += self.calculate_score_from_skills(
            candidate_skills=candidate.skills,
            vacancy_required_skills=vacancy.required_skills,
        )
        rating += self.calculate_score_from_experience(
            candidate_experience=candidate.experience
            if candidate.experience
            else 0,
            vacancy_required_experience=vacancy.required_experience,
        )
        return rating
