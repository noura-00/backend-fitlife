from django.contrib import admin
from .models import WorkoutPlan

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'goal', 'duration_weeks', 'created_at')
    list_filter = ('goal',)
    search_fields = ('title', 'notes')
