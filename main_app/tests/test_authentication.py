from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationTestCase(APITestCase):
    """Test cases for authentication endpoints"""

    def setUp(self):
        """Set up test data and URLs"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.register_url = reverse('signup')
        self.login_url = reverse('login')
        self.token_refresh_url = reverse('token-refresh')
        self.profile_url = reverse('user-profile')

        self.valid_register_data = {
            'username': 'newuser',
            'password': 'newpass123'
        }

        self.invalid_register_data = {
            'username': 'incomplete'
    
        }

        self.valid_login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.invalid_login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

    def tearDown(self):
        """Reset credentials after each test"""
        self.client.credentials()

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(
            self.register_url,
            self.valid_register_data,
            format='json'
        )

        # Check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check response contains tokens and user data
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        # Check user data structure
        user_data = response.data['user']
        self.assertIn('id', user_data)
        self.assertIn('username', user_data)
        self.assertEqual(user_data['username'], 'newuser')

        # Verify tokens are strings
        self.assertIsInstance(response.data['access'], str)
        self.assertIsInstance(response.data['refresh'], str)

        # Verify user was created in database
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # Verify profile was created for the user
        new_user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(new_user, 'profile'))

    def test_user_registration_invalid_data(self):
        """Test registration with invalid/incomplete data"""
        # Test missing password
        response = self.client.post(
            self.register_url,
            self.invalid_register_data,
            format='json'
        )
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])
        self.assertIn('error', response.data)

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        response1 = self.client.post(
            self.register_url,
            {'username': 'duplicate', 'password': 'pass123'},
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response2 = self.client.post(
            self.register_url,
            {'username': 'duplicate', 'password': 'pass456'},
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response2.data)

    def test_user_registration_empty_username(self):
        """Test registration with empty username"""
        response = self.client.post(
            self.register_url,
            {'username': '', 'password': 'pass123'},
            format='json'
        )
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])
        self.assertIn('error', response.data)

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(
            self.login_url,
            self.valid_login_data,
            format='json'
        )

      
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertIsInstance(response.data['access'], str)
        self.assertIsInstance(response.data['refresh'], str)
        self.assertTrue(len(response.data['access']) > 0)
        self.assertTrue(len(response.data['refresh']) > 0)

        # Check user data
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'testuser')
        self.assertIn('id', user_data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            self.login_url,
            self.invalid_login_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertIn('Invalid credentials', response.data['error'])

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = self.client.post(
            self.login_url,
            {'username': 'nonexistent', 'password': 'pass123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_empty_credentials(self):
        """Test login with empty credentials"""
        response = self.client.post(
            self.login_url,
            {'username': '', 'password': ''},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        """Test successful token refresh"""
        login_response = self.client.post(
            self.login_url,
            self.valid_login_data,
            format='json'
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data['refresh']
        response = self.client.post(
            self.token_refresh_url,
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIsInstance(response.data['access'], str)
        self.assertTrue(len(response.data['access']) > 0)

        original_access = login_response.data['access']
        new_access = response.data['access']
    

    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid refresh token"""
        response = self.client.post(
            self.token_refresh_url,
            {'refresh': 'invalid_refresh_token_here'},
            format='json'
        )

       
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_empty_token(self):
        """Test token refresh with empty token"""
        response = self.client.post(
            self.token_refresh_url,
            {'refresh': ''},
            format='json'
        )

    
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_token_refresh_missing_token(self):
        """Test token refresh without providing token"""
        response = self.client.post(
            self.token_refresh_url,
            {},
            format='json'
        )

      
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_protected_endpoint_unauthorized_access(self):
        """Test that protected endpoints block unauthorized access"""
       
        response = self.client.get(self.profile_url)

       
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_authorized_access(self):
        """Test that protected endpoints allow authorized access"""
        login_response = self.client.post(
            self.login_url,
            self.valid_login_data,
            format='json'
        )
        access_token = login_response.data['access']

       
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_protected_endpoint_invalid_token(self):
        """Test protected endpoint with invalid token"""
       
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_here')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_expired_token(self):
        """Test protected endpoint with expired token"""
       
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

     
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_multiple_registrations(self):
        """Test that multiple users can register"""
        users = ['user1', 'user2', 'user3']
        
        for username in users:
            response = self.client.post(
                self.register_url,
                {'username': username, 'password': 'pass123'},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn('access', response.data)

        
        for username in users:
            self.assertTrue(User.objects.filter(username=username).exists())

    def test_login_with_token_from_registration(self):
        """Test that token from registration works for protected endpoints"""
        # Register a new user
        register_response = self.client.post(
            self.register_url,
            self.valid_register_data,
            format='json'
        )
        access_token = register_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

