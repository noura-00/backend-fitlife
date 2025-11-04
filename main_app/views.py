from django.contrib.auth import authenticate
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer, UserProfileSerializer, WorkoutPlanSerializer,
    PostSerializer, CommentSerializer
)
from .models import UserProfile, WorkoutPlan, Post, Comment
from rest_framework.permissions import AllowAny


class HomeView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        content = {"message": "Welcome to the FitLife api home route!"}
        return Response(content)


class CreateUserView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if not serializer.is_valid():
                errors = serializer.errors
                error_message = "Data validation error"
                if 'username' in errors:
                    if 'unique' in str(errors['username']):
                        error_message = "Username already taken"
                    else:
                        error_message = f"Username error: {errors['username'][0]}"
                elif 'password' in errors:
                    error_message = f"Password error: {errors['password'][0]}"
                else:
                    error_message = str(errors)
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
            
            user = serializer.save()
            
            # Create user profile if it doesn't exist
            try:
                UserProfile.objects.get_or_create(user=user)
            except Exception as profile_err:
                print(f"Profile creation error: {profile_err}")
                # Continue anyway - profile is optional for signup
            
            refresh = RefreshToken.for_user(user)

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as err:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Signup error: {str(err)}")
            print(f"Traceback: {error_trace}")
            error_message = str(err)
            if 'already exists' in error_message.lower() or 'unique' in error_message.lower():
                error_message = "Username already taken"
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(username=username, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                content = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }
                return Response(content, status=status.HTTP_200_OK)

            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as err:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Login error: {str(err)}")
            print(f"Traceback: {error_trace}")
            return Response({'error': f'Server error: {str(err)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            
            if 'profile_picture' in request.data and request.data['profile_picture'] == '':
                
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.profile_picture = None
                profile.save()
                
                if 'bio' in request.data:
                    profile.bio = request.data['bio']
                profile.save()
                serializer = UserProfileSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            
            if 'selected_workout_plan' in request.data:
                plan_id = request.data.get('selected_workout_plan')
                if plan_id and plan_id != '':
                    try:
                        workout_plan = WorkoutPlan.objects.get(id=plan_id)
                        profile.selected_workout_plan = workout_plan
                        profile.save()
                    except WorkoutPlan.DoesNotExist:
                        return Response({'error': 'Workout plan not found'}, status=status.HTTP_404_NOT_FOUND)
                elif plan_id == '' or plan_id is None:
                   
                    profile.selected_workout_plan = None
                    profile.save()
            
            data = request.data.copy()
            if request.FILES:
                data.update(request.FILES)
            serializer = UserProfileSerializer(profile, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            error_message = "Data validation error"
            if serializer.errors:
                first_error = list(serializer.errors.values())[0]
                if isinstance(first_error, list) and len(first_error) > 0:
                    error_message = str(first_error[0])
                else:
                    error_message = str(first_error)
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            profile = request.user.profile
            profile.delete()
            return Response({'message': 'Profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkoutPlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            workout_plans = WorkoutPlan.objects.filter(
                models.Q(user=request.user) | models.Q(user=None)
            ).order_by('-created_at')
            
            goal_type = request.query_params.get('goal_type', None)
            if goal_type:
                workout_plans = workout_plans.filter(goal_type=goal_type)
            
            serializer = WorkoutPlanSerializer(workout_plans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        
        try:
            data = request.data.copy()
            data['user'] = request.user.id
            serializer = WorkoutPlanSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkoutPlanDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
     
        try:
            workout_plan = WorkoutPlan.objects.get(pk=pk)
            serializer = WorkoutPlanSerializer(workout_plan)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except WorkoutPlan.DoesNotExist:
            return Response({'error': 'Workout plan not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        
        try:
            workout_plan = WorkoutPlan.objects.get(pk=pk)
            serializer = WorkoutPlanSerializer(workout_plan, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except WorkoutPlan.DoesNotExist:
            return Response({'error': 'Workout plan not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
       
        try:
            workout_plan = WorkoutPlan.objects.get(pk=pk)
       
            if workout_plan.user != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            workout_plan.delete()
            return Response({'message': 'Workout plan deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except WorkoutPlan.DoesNotExist:
            return Response({'error': 'Workout plan not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            posts = Post.objects.select_related('user', 'user__profile').all()
            serializer = PostSerializer(posts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
       
        try:
            data = request.data.copy() if request.data else {}
            
            if request.FILES:
                data.update(request.FILES)
            
            data['user'] = request.user.id
            
            if 'content' not in data or not data.get('content', '').strip():
                return Response({'error': 'Post content is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                if image_file.size > 10 * 1024 * 1024:
                    return Response({'error': 'Image file too large. Maximum size is 10MB.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'workout_plan' in data:
                workout_plan_value = data['workout_plan']
                if workout_plan_value:
                    try:
                        workout_plan_id = int(workout_plan_value)
                        if workout_plan_id > 0:
                            from .models import WorkoutPlan
                            try:
                                workout_plan = WorkoutPlan.objects.get(id=workout_plan_id)
                                if workout_plan.user is None or workout_plan.user == request.user:
                                    data['workout_plan'] = workout_plan_id
                                else:
                                    data.pop('workout_plan', None)
                            except WorkoutPlan.DoesNotExist:
                                data.pop('workout_plan', None)
                        else:
                            data.pop('workout_plan', None)
                    except (ValueError, TypeError):
                        data.pop('workout_plan', None)
                else:
                    data.pop('workout_plan', None)
            
            serializer = PostSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                post = serializer.save()
                return Response(PostSerializer(post, context={'request': request}).data, status=status.HTTP_201_CREATED)
            
            error_message = "Validation error"
            if serializer.errors:
                error_list = []
                for field, errors in serializer.errors.items():
                    if isinstance(errors, list):
                        error_list.extend([f"{field}: {error}" for error in errors])
                    else:
                        error_list.append(f"{field}: {errors}")
                error_message = "; ".join(error_list) if error_list else str(serializer.errors)
            
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': f'Server error: {str(err)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        
        try:
            post = Post.objects.select_related('user', 'user__profile').get(pk=pk)
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
       
        try:
            post = Post.objects.select_related('user', 'user__profile').get(pk=pk)
            
            if post.user != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            data = request.data.copy()
            if request.FILES:
                data.update(request.FILES)
            serializer = PostSerializer(post, data=data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(PostSerializer(post, context={'request': request}).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        
        try:
            post = Post.objects.get(pk=pk)
            
            if post.user != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            post.delete()
            return Response({'message': 'Post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        
        try:
            comments = Comment.objects.filter(post_id=post_id)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, post_id):
       
        try:
            data = request.data.copy()
            data['post'] = post_id
            data['user'] = request.user.id
            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
       
        try:
            comment = Comment.objects.get(pk=pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
      
        try:
            comment = Comment.objects.get(pk=pk)
            
            if comment.user != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        
        try:
            comment = Comment.objects.select_related('post', 'user').get(pk=pk)
            
            is_comment_owner = comment.user == request.user
            is_post_owner = comment.post.user == request.user
            
            if not (is_comment_owner or is_post_owner):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            comment.delete()
            return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

