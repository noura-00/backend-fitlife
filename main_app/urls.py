# IMPORTS
from django.urls import path
from .views import CreateUserView, LoginView, UserProfileDetailView

# URL PATTERNS
urlpatterns = [
    # user signup
    path('users/signup/', CreateUserView.as_view(), name='signup'),

    # user login
    path('users/login/', LoginView.as_view(), name='login'),

    # user profile (get, update, delete)
    path('users/profile/', UserProfileDetailView.as_view(), name='user-profile'),
]
