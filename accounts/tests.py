from django.test import TestCase, Client
from accounts.models import CustomUser
from django.urls import reverse

class AuthFlowTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_customer_registration_and_login(self):
        # 1. Register a customer
        data = {
            'username': 'test_customer',
            'email': 'test_customer@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'user_type': 'customer',
            'phone_number': '1234567890',
            'address': '123 Customer St'
        }
        response = self.client.post(reverse('register'), data)
        
        # Customer registration should redirect to home upon success
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        
        # Verify user is created and approved
        user = CustomUser.objects.get(username='test_customer')
        self.assertTrue(user.is_customer())
        self.assertTrue(user.is_approved)
        
        # Verify customer is automatically logged in
        # We can check session or just try to access a protected page
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_seller_registration_and_login(self):
        # 1. Register a seller
        data = {
            'username': 'test_seller',
            'email': 'test_seller@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'user_type': 'seller',
            'phone_number': '0987654321',
            'address': '456 Seller Blvd'
        }
        response = self.client.post(reverse('register'), data)
        
        # Seller registration should redirect to login upon success
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        
        # Verify user is created but NOT approved
        user = CustomUser.objects.get(username='test_seller')
        self.assertTrue(user.is_seller())
        self.assertFalse(user.is_approved)
        
        # Verify seller is NOT logged in automatically
        self.assertFalse('_auth_user_id' in self.client.session)
        
        # 2. Admin approves the seller manually
        user.is_approved = True
        user.save()
        
        # 3. Seller logs in
        login_response = self.client.post(reverse('login'), {
            'username': 'test_seller',
            'password': 'StrongPass123!'
        })
        
        # Should redirect to home upon successful login
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.url, reverse('home'))
        
        # Verify seller is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
