from ninja import Router, Schema
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpRequest, HttpResponseBadRequest
from typing import Optional
from ninja.security import django_auth
from src.api.schemas import APIResponseSchema

User = get_user_model()

router = Router(tags=['auth'])

class RegisterIn(Schema):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str  # 'candidate' или 'employer'

class AuthOut(Schema):
    refresh: str
    access: str
    user_id: int
    role: str

class MeResponse(Schema):
    role: str
    user: dict
    profile: dict

@router.post('/register', response=AuthOut)
def register(request, data: RegisterIn):
    if User.objects.filter(email=data.email).exists():
        return HttpResponseBadRequest("Email уже используется")
    
    user = User.objects.create(
        username=data.email,
        email=data.email,
        password=make_password(data.password),
        first_name=data.first_name or '',
        last_name=data.last_name or '',
    )
    
    if data.role == 'candidate':
        from src.apps.profiles.models.jobseekers import JobSeekerProfile
        JobSeekerProfile.objects.create(user=user)
    elif data.role == 'employer':
        from src.apps.profiles.models.employers import EmployerProfile
        EmployerProfile.objects.create(user=user)
    else:
        return HttpResponseBadRequest("Неверная роль")
    
    refresh = RefreshToken.for_user(user)
    return AuthOut(
        refresh=str(refresh),
        access=str(refresh.access_token),
        user_id=user.id,
        role=data.role,
    )

@router.post('/login', response=AuthOut)
def login(request, email: str, password: str):
    from django.contrib.auth import authenticate
    
    user = authenticate(email=email, password=password)
    if not user:
        return HttpResponseBadRequest("Неверный email или пароль")
    
    refresh = RefreshToken.for_user(user)
    role = 'candidate' if hasattr(user, 'jobseekerprofile') else 'employer' if hasattr(user, 'employerprofile') else 'unknown'
    
    return AuthOut(
        refresh=str(refresh),
        access=str(refresh.access_token),
        user_id=user.id,
        role=role,
    )

@router.get('/me/', response=APIResponseSchema[MeResponse], auth=django_auth)
def get_me(request: HttpRequest):
    user = request.user
    
    base_data = {
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    }
    
    if hasattr(user, 'jobseekerprofile'):
        profile = user.jobseekerprofile
        if not profile:
            return HttpResponseBadRequest("Профиль кандидата не создан")
        
        return APIResponseSchema(data={
            **base_data,
            "role": "candidate",
            "profile": {
                "id": profile.id,
                "phone": profile.phone,
                "birth_date": str(profile.birth_date) if profile.birth_date else None,
                "age": profile.age,
                "about_me": profile.about_me,
                "experience": profile.experience,
                "skills": profile.skills,
                "location": profile.location,
                "allow_notifications": profile.allow_notifications,
                "resume_url": profile.resume.url if profile.resume else None,
                "created_at": str(profile.created_at),
                "updated_at": str(profile.updated_at),
            }
        })
    
    elif hasattr(user, 'employerprofile'):
        profile = user.employerprofile
        if not profile:
            return HttpResponseBadRequest("Профиль работодателя не создан")
        
        return APIResponseSchema(data={
            **base_data,
            "role": "employer",
            "profile": {
                "id": profile.id,
                "created_at": str(profile.created_at),
                "updated_at": str(profile.updated_at),
                # Добавь поля работодателя
            }
        })
    
    return HttpResponseBadRequest("Профиль не найден")