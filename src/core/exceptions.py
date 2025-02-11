class ApplicationException(Exception): ...


class NotFound(ApplicationException): ...


class VacancyDoesNotExist(NotFound):
    def __init__(self, vacancy_id: int) -> None:
        self.vacancy_id = vacancy_id
        self.message = f'Vacancy with id "{vacancy_id}" does not exist'


class CandidateDoesNotExist(NotFound):
    def __init__(self, candidate_id: int) -> None:
        self.candidate_id = candidate_id
        self.message = f'Candidate with id "{candidate_id}" does not exist'
