from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Role, Question, AuditLog


class RoleModelTest(TestCase):
    def test_create_role(self):
        """Test creating a role."""
        role = Role.objects.create(name=Role.ADMIN, description='Admin role')
        self.assertEqual(role.name, Role.ADMIN)
        self.assertEqual(str(role), 'Admin')


class UserModelTest(TestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.standard_role = Role.objects.create(name=Role.STANDARD)
    
    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=self.standard_role
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_standard)
        self.assertFalse(user.is_admin)
    
    def test_admin_role(self):
        """Test user with admin role."""
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role=self.admin_role
        )
        self.assertTrue(user.is_admin)
        self.assertFalse(user.is_standard)


class QuestionModelTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name=Role.ADMIN)
        self.user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='pass123',
            role=self.role
        )
    
    def test_create_question(self):
        """Test creating a question."""
        question = Question.objects.create(
            title='Test Question',
            content='What is 2 + 2?',
            option_a='3',
            option_b='4',
            option_c='5',
            option_d='6',
            correct_answer='B',
            difficulty='easy',
            category='Math',
            created_by=self.user
        )
        self.assertEqual(question.title, 'Test Question')
        self.assertEqual(question.correct_answer, 'B')
        self.assertTrue(question.is_active)


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.standard_role = Role.objects.create(name=Role.STANDARD)
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role=self.admin_role
        )
        
        self.standard_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123',
            role=self.standard_role
        )
    
    def test_home_page(self):
        """Test home page loads."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QuizQuest')
    
    def test_login_page(self):
        """Test login page loads."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_page(self):
        """Test register page loads."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'adminpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_admin_dashboard_requires_admin(self):
        """Test admin dashboard requires admin role."""
        # Not logged in
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Standard user
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Admin user
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_question_list_requires_login(self):
        """Test question list requires login."""
        response = self.client.get(reverse('question_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)
