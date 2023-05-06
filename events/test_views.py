from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Events, EventVenues, EventTypes
from .serializers import EventsSerializer

events_model = Events
events_serializer = EventsSerializer

class EventsViewSetTestCase(APITestCase):
    def setUp(self):
        self.admin_client = APIClient()
        self.client = APIClient()
        
        # Admin user | JWT Authorization
        self.admin_user = get_user_model().objects.create_superuser(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_token = AccessToken.for_user(self.admin_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        # Default user | JWT Authorization
        self.user = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        self.user_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        
        # Creating events
        self.events_model = events_model
        self.events_serializer = events_serializer
        self.event1 = self.events_model.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        self.event2 = self.events_model.objects.create(
            name='Test event 2',
            start_datetime=timezone.now() + timedelta(days=2),
            closing_registration_date=timezone.now() + timedelta(hours=2)
        )
        
        self.events_list_url = reverse('events-list')
        self.events_detail_url = reverse('events-detail', args=[self.event1.id])
        
    def tearDown(self):
        self.user.delete()
        self.admin_user.delete()

    def test_get_all_events(self):
        response = self.client.get(self.events_list_url)
        admin_response = self.admin_client.get(self.events_list_url)
        events = self.events_model.objects.all()
        serializer = self.events_serializer(events, many=True)
        self.assertEqual(response.data.get("count"), len(serializer.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data.get("count"), len(serializer.data))
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        
    def test_events_detail_view(self):
        response = self.client.get(self.events_detail_url)
        admin_response = self.admin_client.get(self.events_detail_url)
        self.assertEqual(response.data.get("id"), self.event1.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data.get("id"), self.event1.id)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)

    def test_create_new_event(self):
        data = {
            'name': 'New test event',
            'start_datetime': timezone.now() + timedelta(days=3),
            'closing_registration_date': timezone.now() + timedelta(hours=3)
        }
        response = self.client.post(self.events_list_url, data)
        admin_response = self.admin_client.post(self.events_list_url, data)
        self.assertEqual(admin_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(admin_response.data.get("name"), "New test event")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_event(self):
        event = self.events_model.objects.get(name='Test event')
        data = {
            'name': 'Updated test event',
            'start_datetime': event.start_datetime,
            'closing_registration_date': event.closing_registration_date
        }
        response = self.client.put(self.events_detail_url, data)
        admin_response = self.admin_client.put(self.events_detail_url, data)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data.get("name"), "Updated test event")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event(self):
        response = self.client.delete(self.events_detail_url)
        admin_response = self.admin_client.delete(self.events_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(admin_response.status_code, status.HTTP_204_NO_CONTENT)
