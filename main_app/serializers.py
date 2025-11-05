from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, WorkoutPlan, Post, Comment

class UserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password', '')
      
        user = User.objects.create_user(
            username=validated_data['username'],
            password=password
        )
        return user


class WorkoutPlanSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = WorkoutPlan
        fields = ('id', 'user', 'user_username', 'title', 'goal_type', 'equipment_needed', 
                  'duration', 'description', 'notes', 'created_at')
        read_only_fields = ('created_at', 'user_username')


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    selected_workout_plan_detail = WorkoutPlanSerializer(source='selected_workout_plan', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('id', 'user_id', 'username', 'email', 'height', 'current_weight', 'target_weight', 
                  'goal', 'activity_level', 'profile_picture', 'bio', 'followers_count', 
                  'following_count', 'selected_workout_plan', 'selected_workout_plan_detail')
        read_only_fields = ('followers_count', 'following_count', 'username', 'email', 'user_id', 'selected_workout_plan_detail')


class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'post', 'user', 'user_username', 'content', 'created_at')
        read_only_fields = ('created_at', 'user_username')


class PostSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_profile_picture = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True, max_length=None)
    
    def get_user_profile_picture(self, obj):
       
        try:
            profile = obj.user.profile
            if profile and profile.profile_picture:
                
                return profile.profile_picture.url
        except:
            pass
        return None
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    class Meta:
        model = Post
        fields = ('id', 'user', 'user_username', 'user_profile_picture', 'workout_plan', 'content', 'image', 'image_url',
                  'created_at', 'comments', 'comments_count')
        read_only_fields = ('created_at', 'user_username', 'user_profile_picture', 'image_url', 'comments_count')