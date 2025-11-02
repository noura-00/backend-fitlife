from django.db import models
from django.contrib.auth.models import User

class WorkoutPlan(models.Model):
    GOAL_CHOICES = [
        ('cut', 'Cut (Lose Fat)'),
        ('bulk', 'Bulk (Gain Muscle)'),
        ('maintain', 'Maintain Weight'),
        ('home', 'Home Workout (No Equipment)'), 
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workout_plans", null=True, blank=True)
    title = models.CharField(max_length=100)
    goal_type = models.CharField(max_length=20, choices=GOAL_CHOICES)
    equipment_needed = models.TextField(blank=True, null=True)
    duration = models.PositiveIntegerField(default=4, help_text="Duration in weeks")
    description = models.TextField(blank=True, null=True)
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
    selected_workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_profiles")

    def __str__(self):
        return self.user.username


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    workout_plan = models.OneToOneField(WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="post")
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.user.username} - {self.created_at}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on post {self.post.id}"
