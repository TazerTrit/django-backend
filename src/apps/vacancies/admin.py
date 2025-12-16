from django.contrib import admin

from .models import Vacancy

from .models import VacancyInterest


class VacancyInterestInline(admin.TabularInline):
    model = VacancyInterest
    extra = 0
    fields = ('candidate', 'status', 'created_at')
    readonly_fields = ('candidate','created_at',)
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

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    inlines = [VacancyInterestInline]
    list_display = [
        'id',
        'title',
        'company_name',
        'open',
        'required_experience',
        'required_skills',
        'created_at',
    ]

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
    raw_id_fields = ('candidate', 'vacancy') # поиск по ID, быстрее чем dropdown

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