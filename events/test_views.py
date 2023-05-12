from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from .models import Events, PaidEvents, PrivateEvents
from .serializers import (EventInvitationsSerializer, EventsSerializer,
                          PaidEventsSerializer, PrivateEventsSerializer)


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
        self.not_exsisting_events_detail_url = reverse('events-detail', args=[100])
        
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
        
        # Test not exsisting objects
        client_response = self.client.get(self.not_exsisting_events_detail_url)
        admin_response = self.admin_client.get(self.not_exsisting_events_detail_url)
        anonymus_client_response = self.anonymus_client.get(self.not_exsisting_events_detail_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_404_NOT_FOUND)
        

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
        
        # Test not exsisting objects
        client_response = self.client.put(self.not_exsisting_events_detail_url, data)
        admin_response = self.admin_client.put(self.not_exsisting_events_detail_url, data)
        anonymus_client_response = self.anonymus_client.put(self.not_exsisting_events_detail_url, data)
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_event(self):
        client_response = self.client.delete(self.events_detail_url)
        admin_response = self.admin_client.delete(self.events_detail_url)
        anonymus_client_response = self.anonymus_client.delete(self.events_detail_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(admin_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Test not exsisting objects
        client_response = self.client.delete(self.not_exsisting_events_detail_url)
        admin_response = self.admin_client.delete(self.not_exsisting_events_detail_url)
        anonymus_client_response = self.anonymus_client.delete(self.not_exsisting_events_detail_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateEventsViewSetTestCase(APITestCase):
    
    events_model = PrivateEvents
    events_serializer = PrivateEventsSerializer
    
    events_list_url = reverse('privateevents-list')
    events_detail_url = reverse('privateevents-detail', args=[1])
    not_exsisting_events_detail_url = reverse('privateevents-detail', args=[100])
    
        
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
        self.private_event1 = self.events_model.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        self.private_event2 = self.events_model.objects.create(
            name='Test event 2',
            start_datetime=timezone.now() + timedelta(days=2),
            closing_registration_date=timezone.now() + timedelta(hours=2)
        )
        
    def tearDown(self):
        self.user.delete()
        self.admin_user.delete()

    def test_get_all_events(self):
        client_response = self.client.get(self.events_list_url)
        admin_response = self.admin_client.get(self.events_list_url)
        anonymus_client_response = self.anonymus_client.get(self.events_list_url)
        
        private_events = self.events_model.objects.all()
        serializer = self.events_serializer(private_events, many=True)
        
        self.assertEqual(client_response.data.get("count"), len(serializer.data))
        self.assertEqual(admin_response.data.get("count"), len(serializer.data))
        
        self.assertEqual(client_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_events_detail_view(self):
        client_response = self.client.get(self.events_detail_url)
        admin_response = self.admin_client.get(self.events_detail_url)
        anonymus_client_response = self.anonymus_client.get(self.events_detail_url)
        
        self.assertEqual(client_response.data.get("id"), self.private_event1.id)
        self.assertEqual(client_response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(admin_response.data.get("id"), self.private_event1.id)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test not exsisting objects
        client_response = self.client.get(self.not_exsisting_events_detail_url)
        admin_response = self.admin_client.get(self.not_exsisting_events_detail_url)
        anonymus_client_response = self.anonymus_client.get(self.not_exsisting_events_detail_url)
        
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(client_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)

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
        event = self.events_model.objects.get(name='Test event')
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
        
        # Test not exsisting objects
        client_response = self.client.put(self.not_exsisting_events_detail_url, data)
        admin_response = self.admin_client.put(self.not_exsisting_events_detail_url, data)
        anonymus_client_response = self.anonymus_client.put(self.not_exsisting_events_detail_url, data)
        
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_event(self):
        client_response = self.client.delete(self.events_detail_url)
        admin_response = self.admin_client.delete(self.events_detail_url)
        anonymus_client_response = self.anonymus_client.delete(self.events_detail_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(admin_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Test not exsisting objects
        client_response = self.client.delete(self.not_exsisting_events_detail_url)
        admin_response = self.admin_client.delete(self.not_exsisting_events_detail_url)
        anonymus_client_response = self.anonymus_client.delete(self.not_exsisting_events_detail_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)



class PaidEventsViewSetTestCase(PrivateEventsViewSetTestCase):
    events_model = PaidEvents
    events_serializer = PaidEventsSerializer
    
    events_list_url = reverse('paidevents-list')
    events_detail_url = reverse('paidevents-detail', args=[1])
    not_exsisting_events_detail_url = reverse('paidevents-detail', args=[100])


class EventsRegistrationModelMixinTestCase(APITestCase):
    
    events_model = Events

    events_detail_url = reverse('events-detail', args=[1])
    event_registration_url = reverse('events-registration', args=[1])
    not_exsisting_event_registration_url = reverse('events-registration', args=[100])
    
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
    
    def tearDown(self):
        self.user.delete()
        self.admin_user.delete()
            
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
        
        # Test not exsisting objects
        client_response = self.client.post(self.not_exsisting_event_registration_url)
        admin_response = self.admin_client.post(self.not_exsisting_event_registration_url)
        anonymus_client_response = self.anonymus_client.post(self.not_exsisting_event_registration_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(admin_response.status_code, status.HTTP_400_BAD_REQUEST)
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
        
        # Test not exsisting objects
        client_response = self.client.delete(self.not_exsisting_event_registration_url)
        admin_response = self.admin_client.delete(self.not_exsisting_event_registration_url)
        anonymus_client_response = self.anonymus_client.delete(self.not_exsisting_event_registration_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        

class EventsInvitationModelMixinTestCase(APITestCase):
    
    events_model = PrivateEvents
    events_serializer = PrivateEventsSerializer
    
    events_detail_url = reverse('privateevents-detail', args=[1])
    event_invitation_url = reverse('privateevents-invitation', args=[1])
    event_invitation_code_url = reverse('privateevents-invitation-code', args=[1])
    event_confrim_invitation_url = reverse('privateevents-confrim-invitation', args=[1])
    
    not_exsisting_event_invitation_url = reverse('privateevents-invitation', args=[100])
    not_exsisting_event_invitation_code_url = reverse('privateevents-invitation-code', args=[100])
    not_exsisting_event_confrim_invitation_url = reverse('privateevents-confrim-invitation', args=[100])
    
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
    
    def tearDown(self):
        self.user.delete()
        self.admin_user.delete()
        
    def test_create_event_invitation_view(self):
        # Create invitations and confirmations
        admin_data = { 'user_id': self.user.id, }
        user_data = { 'user_id': self.admin_user.id, }
        
        anonymus_client_response = self.anonymus_client.post(self.event_invitation_url, user_data)
        client_response = self.client.post(self.event_invitation_url, user_data)
        admin_response = self.admin_client.post(self.event_invitation_url, admin_data)
        
        self.assertEqual(admin_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(admin_response.data.get("event_id"), self.event1.id)
        self.assertEqual(admin_response.data.get("user_id"), self.user.id)
        self.assertEqual(admin_response.data.get("is_invitation_accepted"), False)
        
        self.assertEqual(client_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(client_response.data.get("event_id"), self.event1.id)
        self.assertEqual(client_response.data.get("user_id"), self.admin_user.id)
        self.assertEqual(client_response.data.get("is_invitation_accepted"), False)
        
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test sending an invitation twice
        client_response = self.client.post(self.event_invitation_url, user_data)
        admin_response = self.admin_client.post(self.event_invitation_url, admin_data)
        
        self.assertEqual(client_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(admin_response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test not exsisting objects
        anonymus_client_response = self.anonymus_client.post(self.not_exsisting_event_invitation_url, user_data)
        client_response = self.client.post(self.not_exsisting_event_invitation_url, user_data)
        admin_response = self.admin_client.post(self.not_exsisting_event_invitation_url, user_data)
        
        self.assertEqual(admin_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(client_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_confrim_event_invitation_view(self):
        # Create invitations and confirmations
        admin_data = { 'user_id': self.user.id, }
        user_data = { 'user_id': self.admin_user.id, }
        
        self.client.post(self.event_invitation_url, user_data)
        self.admin_client.post(self.event_invitation_url, admin_data)
        
        client_response = self.client.post(self.event_confrim_invitation_url)
        admin_response = self.admin_client.post(self.event_confrim_invitation_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_200_OK)
        self.assertEqual(client_response.data.get("event_id"), self.event1.id)
        self.assertEqual(client_response.data.get("user_id"), self.user.id)
        self.assertEqual(client_response.data.get("is_invitation_accepted"), True)
        
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data.get("event_id"), self.event1.id)
        self.assertEqual(admin_response.data.get("user_id"), self.admin_user.id)
        self.assertEqual(admin_response.data.get("is_invitation_accepted"), True)
        
        # Test confrim an invitation twice
        client_response = self.client.post(self.event_confrim_invitation_url)
        admin_response = self.admin_client.post(self.event_confrim_invitation_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(client_response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_confrim_not_exsisting_event_invitation_view(self):
        admin_data = { 'user_id': self.user.id, }
        user_data = { 'user_id': self.admin_user.id, }
        
        # Test not exsisting objects
        client_response = self.client.post(self.not_exsisting_event_confrim_invitation_url, user_data)
        admin_response = self.admin_client.post(self.not_exsisting_event_confrim_invitation_url, admin_data)
        anonymus_client_response = self.anonymus_client.post(self.not_exsisting_event_confrim_invitation_url, user_data)
        
        self.assertEqual(client_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_event_invitation_view(self):
        # Create invitations and confirmations
        admin_data = { 'user_id': self.user.id, }
        user_data = { 'user_id': self.admin_user.id, }
        
        self.client.post(self.event_invitation_url, user_data)
        self.admin_client.post(self.event_invitation_url, admin_data)

        admin_response = self.admin_client.delete(self.event_invitation_url)
        client_response = self.client.delete(self.event_invitation_url)
        anonymus_client_response = self.anonymus_client.delete(self.event_invitation_url)
        
        self.assertEqual(admin_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(client_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test confrim deleted invitations
        client_response = self.client.post(self.event_confrim_invitation_url)
        admin_response = self.admin_client.post(self.event_confrim_invitation_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(client_response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test not exsisting objects
        client_response = self.client.delete(self.not_exsisting_event_invitation_url)
        admin_response = self.admin_client.delete(self.not_exsisting_event_invitation_url)
        anonymus_client_response = self.anonymus_client.delete(self.not_exsisting_event_invitation_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_invitation_code(self):
        anonymus_client_response = self.anonymus_client.get(self.event_invitation_code_url)
        client_response = self.client.get(self.event_invitation_code_url)
        admin_response = self.admin_client.get(self.event_invitation_code_url)
        
        private_event = self.events_model.objects.get(id=1)
        
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(admin_response.data.get("invitation_code"), private_event.invitation_code)
        
        # Test not exsisting objects
        client_response = self.client.get(self.not_exsisting_event_invitation_code_url)
        admin_response = self.admin_client.get(self.not_exsisting_event_invitation_code_url)
        anonymus_client_response = self.anonymus_client.get(self.not_exsisting_event_invitation_code_url)
        
        self.assertEqual(client_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(admin_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anonymus_client_response.status_code, status.HTTP_401_UNAUTHORIZED)
        