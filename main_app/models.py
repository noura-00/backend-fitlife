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
    height = models.IntegerField(null=True, blank=True, help_text="Height in cm")
    age = models.IntegerField(null=True, blank=True)
    current_weight = models.FloatField(null=True, blank=True)
    target_weight = models.FloatField(null=True, blank=True)
    goal = models.CharField(max_length=100, blank=True)  
    activity_level = models.CharField(max_length=100, blank=True) 
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    bio = models.TextField(blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    selected_workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_profiles")
    show_age_public = models.BooleanField(default=False)
    show_height_public = models.BooleanField(default=False)
    show_fitness_info_public = models.BooleanField(default=False)

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


class Follow(models.Model):
    """Model to track user follows (like Instagram)"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
    def save(self, *args, **kwargs):
        """Update follower/following counts when follow is created"""
        super().save(*args, **kwargs)
        self._update_counts()
    
    def delete(self, *args, **kwargs):
        """Update follower/following counts when follow is deleted"""
        super().delete(*args, **kwargs)
        self._update_counts()
    
    def _update_counts(self):
        """Update follower and following counts for both users"""
        # Update following count for follower
        follower_profile, _ = UserProfile.objects.get_or_create(user=self.follower)
        follower_profile.following_count = Follow.objects.filter(follower=self.follower).count()
        follower_profile.save()
        
        # Update followers count for following
        following_profile, _ = UserProfile.objects.get_or_create(user=self.following)
        following_profile.followers_count = Follow.objects.filter(following=self.following).count()
        following_profile.save()
