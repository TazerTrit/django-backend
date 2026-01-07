from django.urls import path
from ninja import NinjaAPI

from src.api.v1.vacancies.handlers import router as vacancy_router
from src.api.v1.profiles.employers.handlers import router as employer_profiler_router
from src.api.v1.profiles.jobseekers.handlers import router as jobseeker_profiler_router
from src.api.v1.auth.handlers import router as auth_router

api = NinjaAPI(
    title="HR Platform API",
    version="1.0.0",
    description="API для поиска вакансий, откликов, профилей и авторизации",
)

api.add_router('/auth', auth_router)
api.add_router('/v1/vacancies', vacancy_router)
api.add_router('/v1/jobseekers', jobseeker_profiler_router)
api.add_router('/v1/employers', employer_profiler_router)


urlpatterns = [
    path('', api.urls),
]
