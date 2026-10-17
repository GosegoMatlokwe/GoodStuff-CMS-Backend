# Import Django's testing tools
from django.test import TestCase
from django.urls import reverse

# Create a test class for your API endpoints
class APIAuthTests(TestCase):
    
    # Test that the API blocks requests without a Firebase Token
    def test_api_blocks_unauthorized_users(self):
        # We use Django's test client to simulate a request
        # We call the 'get_bookings' endpoint without sending an Authorization header
        response = self.client.get('/api/bookings/')
        
        # Assert that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, 401)
        
    # Test that the Menu API is public (if you want it to be)
    def test_menu_api_is_public(self):
        response = self.client.get('/api/menu/')
        # Assert that the response is 200 OK
        self.assertEqual(response.status_code, 200)