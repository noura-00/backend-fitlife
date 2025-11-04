# IMPORTS
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    HomeView, CreateUserView, LoginView, UserProfileDetailView,
    WorkoutPlanListView, WorkoutPlanDetailView,
    PostListView, PostDetailView,
    CommentListView, CommentDetailView
)

# URL PATTERNS
urlpatterns = [
    # home/root
    path('', HomeView.as_view(), name='home'),
    
    # user signup
    path('users/signup/', CreateUserView.as_view(), name='signup'),

    # user login
    path('users/login/', LoginView.as_view(), name='login'),

    # token refresh
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # user profile (get, update, delete)
    path('users/profile/', UserProfileDetailView.as_view(), name='user-profile'),

    # workout plans (list, create)
    path('workouts/', WorkoutPlanListView.as_view(), name='workout-plan-list'),

    # workout plan detail (get, update, delete)
    path('workouts/<int:pk>/', WorkoutPlanDetailView.as_view(), name='workout-plan-detail'),

    # posts (list, create)
    path('posts/', PostListView.as_view(), name='post-list'),

    # post detail (get, update, delete)
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    # comments for a post (list, create)
    path('posts/<int:post_id>/comments/', CommentListView.as_view(), name='comment-list'),

    # comment detail (get, update, delete)
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
