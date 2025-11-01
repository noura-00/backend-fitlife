from django.db import models
from django.contrib.auth.models import User

class WorkoutPlan(models.Model):
    GOAL_CHOICES = [
        ('cut', 'Cut (Lose Fat)'),
        ('bulk', 'Bulk (Gain Muscle)'),
        ('maintain', 'Maintain Weight'),
        ('home', 'Home Workout (No Equipment)'), 
    ]
    title = models.CharField(max_length=100)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    duration_weeks = models.PositiveIntegerField(default=4)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    height = models.FloatField(null=True, blank=True)
    current_weight = models.FloatField(null=True, blank=True)
    target_weight = models.FloatField(null=True, blank=True)
    goal = models.CharField(max_length=100, blank=True)  
    activity_level = models.CharField(max_length=100, blank=True) 
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    bio = models.TextField(blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username
