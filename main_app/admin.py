from django.contrib import admin
from .models import WorkoutPlan, Post, Comment, UserProfile

admin.site.register(WorkoutPlan)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserProfile)