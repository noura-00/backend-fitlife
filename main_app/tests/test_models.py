from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from ..models import UserProfile, WorkoutPlan, Post, Comment


class ModelTestCase(TestCase):
    """Base test case with setUp for sample data"""

    def setUp(self):
        """Create sample data for all tests"""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create a user profile linked to the user
        self.profile = UserProfile.objects.create(
            user=self.user,
            height=175.0,
            current_weight=70.0,
            target_weight=65.0,
            goal='Lose weight',
            activity_level='Moderate',
            bio='Test bio',
            followers_count=10,
            following_count=5
        )

        # Create workout plans
        self.workout_plan1 = WorkoutPlan.objects.create(
            user=self.user,
            title='Beginner Workout',
            goal_type='cut',
            equipment_needed='Dumbbells, Bench',
            duration=4,
            description='A beginner-friendly workout plan',
            notes='Start slow'
        )

        self.workout_plan2 = WorkoutPlan.objects.create(
            user=self.user,
            title='Advanced Workout',
            goal_type='bulk',
            equipment_needed='Full gym',
            duration=8,
            description='An advanced workout plan',
            notes='Push your limits'
        )

        self.workout_plan3 = WorkoutPlan.objects.create(
            title='Home Workout',
            goal_type='home',
            equipment_needed='None',
            duration=6,
            description='No equipment needed'
        )

        # Link profile to a workout plan
        self.profile.selected_workout_plan = self.workout_plan1
        self.profile.save()

        # Create posts
        self.post1 = Post.objects.create(
            user=self.user,
            workout_plan=self.workout_plan1,
            content='My first workout post!'
        )

        self.post2 = Post.objects.create(
            user=self.user,
            content='Another post without workout plan'
        )

        # Create comments
        self.comment1 = Comment.objects.create(
            post=self.post1,
            user=self.user,
            content='Great workout!'
        )

        self.comment2 = Comment.objects.create(
            post=self.post1,
            user=self.user,
            content='Keep it up!'
        )

        self.comment3 = Comment.objects.create(
            post=self.post2,
            user=self.user,
            content='Nice post!'
        )


class ModelStrTestCase(ModelTestCase):
    """Test __str__ methods for all models"""

    def test_user_str(self):
        """Test User __str__ method"""
        self.assertEqual(str(self.user), 'testuser')

    def test_userprofile_str(self):
        """Test UserProfile __str__ method"""
        self.assertEqual(str(self.profile), 'testuser')

    def test_workout_plan_str(self):
        """Test WorkoutPlan __str__ method"""
        self.assertEqual(str(self.workout_plan1), 'Beginner Workout')
        self.assertEqual(str(self.workout_plan2), 'Advanced Workout')

    def test_post_str(self):
        """Test Post __str__ method"""
        post_str = str(self.post1)
        self.assertIn('Post by testuser', post_str)
        self.assertIn(str(self.post1.created_at.date()), post_str)

    def test_comment_str(self):
        """Test Comment __str__ method"""
        comment_str = str(self.comment1)
        self.assertIn('Comment by testuser', comment_str)
        self.assertIn('on post', comment_str)
        self.assertIn(str(self.post1.id), comment_str)


class ModelRelationshipsTestCase(ModelTestCase):
    """Test model relationships"""

    def test_user_to_userprofile_one_to_one(self):
        """Test User ↔ UserProfile one-to-one relationship"""
        # User should have a profile
        self.assertEqual(self.user.profile, self.profile)
        
        # Profile should have the user
        self.assertEqual(self.profile.user, self.user)
        
        # Accessing profile through user
        self.assertEqual(self.user.profile.height, 175.0)
        
        # Accessing user through profile
        self.assertEqual(self.profile.user.username, 'testuser')

    def test_user_to_post_foreign_key(self):
        """Test User ↔ Post foreign key relationship (one-to-many)"""
        # User should have multiple posts
        user_posts = self.user.posts.all()
        self.assertEqual(user_posts.count(), 2)
        self.assertIn(self.post1, user_posts)
        self.assertIn(self.post2, user_posts)
        
        # Post should have the user
        self.assertEqual(self.post1.user, self.user)
        self.assertEqual(self.post2.user, self.user)

    def test_post_to_comment_foreign_key(self):
        """Test Post ↔ Comment foreign key relationship (one-to-many)"""
        # Post1 should have multiple comments
        post1_comments = self.post1.comments.all()
        self.assertEqual(post1_comments.count(), 2)
        self.assertIn(self.comment1, post1_comments)
        self.assertIn(self.comment2, post1_comments)
        
        # Post2 should have comments
        post2_comments = self.post2.comments.all()
        self.assertEqual(post2_comments.count(), 1)
        self.assertIn(self.comment3, post2_comments)
        
        # Comment should have the post
        self.assertEqual(self.comment1.post, self.post1)
        self.assertEqual(self.comment2.post, self.post1)
        self.assertEqual(self.comment3.post, self.post2)

    def test_userprofile_to_workout_plan_foreign_key(self):
        """Test UserProfile ↔ WorkoutPlan foreign key relationship"""
        # Profile should have selected workout plan
        self.assertEqual(self.profile.selected_workout_plan, self.workout_plan1)
        
        # Workout plan can be accessed through profile
        self.assertEqual(self.profile.selected_workout_plan.title, 'Beginner Workout')
        
        # WorkoutPlan should have related user_profiles (reverse relation)
        related_profiles = self.workout_plan1.user_profiles.all()
        self.assertEqual(related_profiles.count(), 1)
        self.assertIn(self.profile, related_profiles)

    def test_user_to_workout_plan_foreign_key(self):
        """Test User ↔ WorkoutPlan foreign key relationship"""
        # User should have workout plans
        user_workout_plans = self.user.workout_plans.all()
        self.assertEqual(user_workout_plans.count(), 2)
        self.assertIn(self.workout_plan1, user_workout_plans)
        self.assertIn(self.workout_plan2, user_workout_plans)
        
        # WorkoutPlan should have the user (or can be null)
        self.assertEqual(self.workout_plan1.user, self.user)
        self.assertEqual(self.workout_plan2.user, self.user)
        self.assertIsNone(self.workout_plan3.user)

    def test_post_to_workout_plan_one_to_one(self):
        """Test Post ↔ WorkoutPlan one-to-one relationship"""
        # Post can have a workout plan
        self.assertEqual(self.post1.workout_plan, self.workout_plan1)
        
        # Post can have no workout plan
        self.assertIsNone(self.post2.workout_plan)
        
        # WorkoutPlan can have a post
        self.assertEqual(self.workout_plan1.post, self.post1)


class ModelOrderingTestCase(ModelTestCase):
    """Test model ordering from Meta class"""

    def test_post_ordering(self):
        """Test Post ordering (should be ordered by -created_at)"""
        # Create a new post with a later timestamp
        later_post = Post.objects.create(
            user=self.user,
            content='Latest post'
        )
        
        # Get all posts ordered
        posts = Post.objects.all()
        
        # The latest post should be first
        self.assertEqual(posts[0], later_post)
        self.assertEqual(posts[1], self.post2)
        self.assertEqual(posts[2], self.post1)
        
        # Verify ordering is descending by created_at
        for i in range(len(posts) - 1):
            self.assertGreaterEqual(posts[i].created_at, posts[i + 1].created_at)

    def test_comment_ordering(self):
        """Test Comment ordering (should be ordered by created_at ascending)"""
        # Create a new comment
        later_comment = Comment.objects.create(
            post=self.post1,
            user=self.user,
            content='Latest comment'
        )
        
        # Get all comments for post1 ordered
        comments = self.post1.comments.all()
        
        # Comments should be in ascending order by created_at
        self.assertEqual(comments[0], self.comment1)
        self.assertEqual(comments[1], self.comment2)
        self.assertEqual(comments[2], later_comment)
        
        # Verify ordering is ascending by created_at
        for i in range(len(comments) - 1):
            self.assertLessEqual(comments[i].created_at, comments[i + 1].created_at)


class CascadeDeletionTestCase(TestCase):
    """Test cascade deletion behavior"""

    def setUp(self):
        """Create test data for cascade deletion tests"""
        self.user = User.objects.create_user(
            username='cascadeuser',
            email='cascade@example.com',
            password='testpass123'
        )

        self.profile = UserProfile.objects.create(
            user=self.user,
            height=180.0,
            current_weight=75.0
        )

        self.workout_plan = WorkoutPlan.objects.create(
            user=self.user,
            title='Test Workout',
            goal_type='cut',
            duration=4
        )

        self.profile.selected_workout_plan = self.workout_plan
        self.profile.save()

        self.post = Post.objects.create(
            user=self.user,
            workout_plan=self.workout_plan,
            content='Test post'
        )

        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content='Test comment'
        )

    def test_user_deletion_cascades_to_profile(self):
        """Test that deleting a user also deletes the profile"""
        profile_id = self.profile.id
        user_id = self.user.id
        
        # Delete the user
        self.user.delete()
        
        # Profile should also be deleted
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_user_deletion_cascades_to_posts(self):
        """Test that deleting a user also deletes related posts"""
        post_id = self.post.id
        
        # Delete the user
        self.user.delete()
        
        # Post should also be deleted
        self.assertFalse(Post.objects.filter(id=post_id).exists())

    def test_user_deletion_cascades_to_comments(self):
        """Test that deleting a user also deletes related comments"""
        comment_id = self.comment.id
        
        # Delete the user
        self.user.delete()
        
        # Comment should also be deleted
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())

    def test_user_deletion_cascades_to_workout_plans(self):
        """Test that deleting a user also deletes related workout plans"""
        workout_plan_id = self.workout_plan.id
        
        # Delete the user
        self.user.delete()
        
        # Workout plan should also be deleted (CASCADE)
        self.assertFalse(WorkoutPlan.objects.filter(id=workout_plan_id).exists())

    def test_post_deletion_cascades_to_comments(self):
        """Test that deleting a post also deletes related comments"""
        comment_id = self.comment.id
        
        # Delete the post
        self.post.delete()
        
        # Comment should also be deleted
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())
        
        # User and profile should still exist
        self.assertTrue(User.objects.filter(id=self.user.id).exists())
        self.assertTrue(UserProfile.objects.filter(id=self.profile.id).exists())

    def test_workout_plan_deletion_sets_null_on_userprofile(self):
        """Test that deleting a workout plan sets selected_workout_plan to NULL (SET_NULL)"""
        # Profile has selected_workout_plan
        self.assertEqual(self.profile.selected_workout_plan, self.workout_plan)
        
        # Delete the workout plan
        self.workout_plan.delete()
        
        # Profile should still exist but selected_workout_plan should be None
        self.profile.refresh_from_db()
        self.assertIsNone(self.profile.selected_workout_plan)
        
        # User should still exist
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_workout_plan_deletion_sets_null_on_post(self):
        """Test that deleting a workout plan sets post.workout_plan to NULL (SET_NULL)"""
        # Post has workout_plan
        self.assertEqual(self.post.workout_plan, self.workout_plan)
        
        # Delete the workout plan
        self.workout_plan.delete()
        
        # Post should still exist but workout_plan should be None
        self.post.refresh_from_db()
        self.assertIsNone(self.post.workout_plan)
        
        # Comment should still exist
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())


class ModelValidationTestCase(ModelTestCase):
    """Test model field validations and constraints"""

    def test_workout_plan_goal_type_choices(self):
        """Test WorkoutPlan goal_type choices"""
        valid_choices = ['cut', 'bulk', 'maintain', 'home']
        
        for choice in valid_choices:
            workout = WorkoutPlan.objects.create(
                title=f'Test {choice}',
                goal_type=choice,
                duration=4
            )
            self.assertEqual(workout.goal_type, choice)

    def test_userprofile_default_values(self):
        """Test UserProfile default values"""
        new_user = User.objects.create_user(username='newuser', password='pass')
        new_profile = UserProfile.objects.create(user=new_user)
        
        self.assertEqual(new_profile.followers_count, 0)
        self.assertEqual(new_profile.following_count, 0)
        self.assertEqual(new_profile.bio, '')
        self.assertIsNone(new_profile.selected_workout_plan)

    def test_workout_plan_default_duration(self):
        """Test WorkoutPlan default duration"""
        workout = WorkoutPlan.objects.create(
            title='Default Duration Test',
            goal_type='cut'
        )
        
        self.assertEqual(workout.duration, 4)





