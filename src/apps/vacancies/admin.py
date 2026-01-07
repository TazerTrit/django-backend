from django.contrib import admin
from .models import Vacancy, VacancyInterest
from src.apps.profiles.models.jobseekers import JobSeekerProfile

# Inline для откликов на странице вакансии
class VacancyInterestInline(admin.TabularInline):
    model = VacancyInterest
    extra = 0
    fields = ('candidate', 'status', 'created_at')
    readonly_fields = ('candidate', 'created_at')
    actions = ['mark_viewed', 'mark_invited', 'mark_rejected']

    def mark_viewed(self, request, queryset):
        queryset.update(status='viewed')
    mark_viewed.short_description = "Отметить как просмотренные"

    def mark_invited(self, request, queryset):
        queryset.update(status='invited')
    mark_invited.short_description = "Пригласить на собеседование"

    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_rejected.short_description = "Отклонить"

# Админка для вакансий
@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    inlines = [VacancyInterestInline]
    list_display = [
        'id',
        'title',
        'company_name',
        'open',
        'required_experience',
        'hard_skills_short',   # ← короткий список hard
        'soft_skills_short',   # ← короткий список soft
        'created_at',
    ]
    search_fields = ('title', 'company_name')
    list_filter = ('open', 'is_remote', 'relocation')

    def hard_skills_short(self, obj):
        return ", ".join(obj.hard_skills[:5]) + ("..." if len(obj.hard_skills) > 5 else "")
    hard_skills_short.short_description = "Hard skills"

    def soft_skills_short(self, obj):
        return ", ".join(obj.soft_skills[:5]) + ("..." if len(obj.soft_skills) > 5 else "")
    soft_skills_short.short_description = "Soft skills"

# Админка для откликов (полный список)
@admin.register(VacancyInterest)
class VacancyInterestAdmin(admin.ModelAdmin):
    list_display = (
        'candidate',
        'vacancy',
        'status',
        'get_status_display',
        'created_at',
        'candidate_email',
    )
    list_filter = ('status', 'vacancy__company_name', 'vacancy__title')
    search_fields = ('candidate__user__email', 'vacancy__title')
    actions = ['mark_viewed', 'mark_invited', 'mark_rejected']
    raw_id_fields = ('candidate', 'vacancy')

    def candidate_email(self, obj):
        return obj.candidate.user.email
    candidate_email.short_description = "Email кандидата"

    def mark_viewed(self, request, queryset):
        queryset.update(status='viewed')
    mark_viewed.short_description = "Отметить как просмотренные"

    def mark_invited(self, request, queryset):
        queryset.update(status='invited')
    mark_invited.short_description = "Пригласить на собеседование"

    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_rejected.short_description = "Отклонить"

# Админка для профилей кандидатов (с годом рождения)
@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'first_name',
        'last_name',
        'email',
        'birth_date',
        'age',  # ← свойство age
        'phone',
        'has_resume',
        'created_at',  # ← если created_at в BaseProfile — оставь, иначе убери
    )
    search_fields = ('user__email', 'first_name', 'last_name')
    list_filter = ()
    readonly_fields = ('created_at', 'updated_at')  # ← если поля есть в BaseProfile — оставь, иначе убери
    ordering = ('-created_at',)  # ← если created_at в BaseProfile — возможно нужно ('id',)

    def has_resume(self, obj):
        return bool(obj.resume) if hasattr(obj, 'resume') else False
    has_resume.boolean = True
    has_resume.short_description = "Резюме загружено"