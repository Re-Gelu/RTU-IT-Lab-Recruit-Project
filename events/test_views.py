from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Events, PrivateEvents
from .serializers import EventsSerializer, PrivateEventsSerializer


class EventsViewSetTestCase(APITestCase):
    def setUp(self):
        self.admin_client = APIClient()
        self.client = APIClient()
        self.anonymus_client = APIClient()
        
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
        self.event1 = Events.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        self.event2 = Events.objects.create(
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
        client_response = self.client.get(self.events_list_url)
        admin_response = self.admin_client.get(self.events_list_url)
        anonymus_client_response = self.anonymus_client.get(self.events_list_url)
        
        events = Events.objects.all()
        serializer = EventsSerializer(events, many=True)
        
        self.assertEqual(client_response.data.get("count"), len(serializer.data))
        self.assertEqual(admin_response.data.get("count"), len(serializer.data))
        self.assertEqual(anonymus_client_response.data.get("count"), len(serializer.data))
        
        self.assertEqual(client_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_200_OK)
        
    def test_events_detail_view(self):
        client_response = self.client.get(self.events_detail_url)
        admin_response = self.admin_client.get(self.events_detail_url)
        anonymus_client_response = self.anonymus_client.get(self.events_detail_url)
        
        self.assertEqual(client_response.data.get("id"), self.event1.id)
        self.assertEqual(client_response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(admin_response.data.get("id"), self.event1.id)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(anonymus_client_response.data.get("id"), self.event1.id)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_200_OK)

    def test_create_new_event(self):
        data = {
            'name': 'New test event',
            'start_datetime': timezone.now() + timedelta(days=3),
            'closing_registration_date': timezone.now() + timedelta(hours=3)
        }
        
        client_response = self.client.post(self.events_list_url, data)
        admin_response = self.admin_client.post(self.events_list_url, data)
        anonymus_client_response = self.anonymus_client.post(self.events_list_url, data)
        
        self.assertEqual(admin_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(admin_response.data.get("name"), "New test event")
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_event(self):
        event = Events.objects.get(name='Test event')
        data = {
            'name': 'Updated test event',
            'start_datetime': event.start_datetime,
            'closing_registration_date': event.closing_registration_date
        }
        
        client_response = self.client.put(self.events_detail_url, data)
        admin_response = self.admin_client.put(self.events_detail_url, data)
        anonymus_client_response = self.anonymus_client.put(self.events_detail_url, data)
        
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data.get("name"), "Updated test event")
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_event(self):
        client_response = self.client.delete(self.events_detail_url)
        admin_response = self.admin_client.delete(self.events_detail_url)
        anonymus_client_response = self.anonymus_client.delete(self.events_detail_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(admin_response.status_code, status.HTTP_204_NO_CONTENT)


class PrivateEventsViewSetTestCase(APITestCase):
    def setUp(self):
        self.admin_client = APIClient()
        self.client = APIClient()
        self.anonymus_client = APIClient()
        
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
        self.private_event1 = PrivateEvents.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        self.private_event2 = PrivateEvents.objects.create(
            name='Test event 2',
            start_datetime=timezone.now() + timedelta(days=2),
            closing_registration_date=timezone.now() + timedelta(hours=2)
        )
        
        self.private_events_list_url = reverse('privateevents-list')
        self.private_events_detail_url = reverse('privateevents-detail', args=[self.private_event1.id])
        
    def tearDown(self):
        self.user.delete()
        self.admin_user.delete()

    def test_get_all_events(self):
        client_response = self.client.get(self.private_events_list_url)
        admin_response = self.admin_client.get(self.private_events_list_url)
        anonymus_client_response = self.anonymus_client.get(self.private_events_list_url)
        
        private_events = PrivateEvents.objects.all()
        serializer = PrivateEventsSerializer(private_events, many=True)
        
        self.assertEqual(client_response.data.get("count"), len(serializer.data))
        self.assertEqual(admin_response.data.get("count"), len(serializer.data))
        
        self.assertEqual(client_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_events_detail_view(self):
        client_response = self.client.get(self.private_events_detail_url)
        admin_response = self.admin_client.get(self.private_events_detail_url)
        anonymus_client_response = self.anonymus_client.get(self.private_events_detail_url)
        
        self.assertEqual(client_response.data.get("id"), self.private_event1.id)
        self.assertEqual(client_response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(admin_response.data.get("id"), self.private_event1.id)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_new_event(self):
        data = {
            'name': 'New test event',
            'start_datetime': timezone.now() + timedelta(days=3),
            'closing_registration_date': timezone.now() + timedelta(hours=3)
        }
        
        client_response = self.client.post(self.private_events_list_url, data)
        admin_response = self.admin_client.post(self.private_events_list_url, data)
        anonymus_client_response = self.anonymus_client.post(self.private_events_list_url, data)
        
        self.assertEqual(admin_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(admin_response.data.get("name"), "New test event")
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_event(self):
        event = PrivateEvents.objects.get(name='Test event')
        data = {
            'name': 'Updated test event',
            'start_datetime': event.start_datetime,
            'closing_registration_date': event.closing_registration_date
        }
        
        client_response = self.client.put(self.private_events_detail_url, data)
        admin_response = self.admin_client.put(self.private_events_detail_url, data)
        anonymus_client_response = self.anonymus_client.put(self.private_events_detail_url, data)
        
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data.get("name"), "Updated test event")
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_event(self):
        client_response = self.client.delete(self.private_events_detail_url)
        admin_response = self.admin_client.delete(self.private_events_detail_url)
        anonymus_client_response = self.anonymus_client.delete(self.private_events_detail_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(admin_response.status_code, status.HTTP_204_NO_CONTENT)
        

class EventsRegistrationModelMixinTestCase(APITestCase):
    def setUp(self):
        self.admin_client = APIClient()
        self.client = APIClient()
        self.anonymus_client = APIClient()
        
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
        self.event1 = Events.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        self.event2 = Events.objects.create(
            name='Test event 2',
            start_datetime=timezone.now() + timedelta(days=2),
            closing_registration_date=timezone.now() + timedelta(hours=2)
        )
        
        self.events_list_url = reverse('events-list')
        self.events_detail_url = reverse('events-detail', args=[self.event1.id])
        self.event_registration_url = reverse('events-registration', args=[self.event1.id])
            
    def test_event_registration_view(self):
        client_response = self.client.post(self.event_registration_url)
        admin_response = self.admin_client.post(self.event_registration_url)
        anonymus_client_response = self.anonymus_client.post(self.event_registration_url)
        
        self.assertEqual(admin_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(admin_response.data.get("event_id"), self.event1.id)
        self.assertEqual(admin_response.data.get("is_invitation_accepted"), True)
        
        self.assertEqual(client_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(client_response.data.get("event_id"), self.event1.id)
        self.assertEqual(client_response.data.get("is_invitation_accepted"), True)
        
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_event_registration_view(self):
        self.client.post(self.event_registration_url)
        self.admin_client.post(self.event_registration_url)
        self.anonymus_client.post(self.event_registration_url)
        
        client_response = self.client.delete(self.event_registration_url)
        admin_response = self.admin_client.delete(self.event_registration_url)
        anonymus_client_response = self.anonymus_client.delete(self.event_registration_url)
        
        self.assertEqual(admin_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(client_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)