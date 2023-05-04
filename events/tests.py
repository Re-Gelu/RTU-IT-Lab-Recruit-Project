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
import datetime

class EventsViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # User | Authorization
        self.admin_user = get_user_model().objects.create_superuser(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_token = AccessToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
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

    def test_get_all_events(self):
        response = self.client.get(reverse('events-list'))
        events = Events.objects.all()
        serializer = EventsSerializer(events, many=True)
        self.assertEqual(response.data.get("count"), len(serializer.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_new_event(self):
        data = {
            'name': 'New test event',
            'start_datetime': timezone.now() + timedelta(days=3),
            'closing_registration_date': timezone.now() + timedelta(hours=3)
        }
        response = self.client.post(reverse('events-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_event(self):
        event = Events.objects.get(name='Test event')
        data = {
            'name': 'Updated test event',
            'start_datetime': event.start_datetime,
            'closing_registration_date': event.closing_registration_date
        }
        response = self.client.put(reverse('events-detail', args=[event.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_event(self):
        event = Events.objects.get(name='Test event')
        response = self.client.delete(reverse('events-detail', args=[event.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class EventsSerializerTestCase(TestCase):
    def setUp(self):
        self.event = Events.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )

    def test_event_serializer(self):
        serializer = EventsSerializer(self.event)
        data = serializer.data
        self.assertEqual(data['name'], self.event.name)
        self.assertEqual(datetime.datetime.fromisoformat(data['start_datetime']), timezone.localtime(self.event.start_datetime))
        self.assertEqual(datetime.datetime.fromisoformat(data['closing_registration_date']), timezone.localtime(self.event.closing_registration_date))
        
        
class EventsModelTest(TestCase):
    
    def setUp(self):
        venue = EventVenues.objects.create(name='Test Venue')
        event_type = EventTypes.objects.create(name='Test Event Type')
        self.event = Events.objects.create(
            name='Test Event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=12),
            venue_id=venue,
            category_id=event_type,
            max_visitors=10,
        )
        
    def test_str_method(self):
        self.assertEqual(str(self.event), 'Test Event')
        
    def test_end_datetime(self):
        expected_end_datetime = self.event.start_datetime + self.event.duration
        self.assertEqual(self.event.end_datetime(), expected_end_datetime)
        
    def test_was_published_recently(self):
        self.assertTrue(self.event.was_publiched_recently())
        self.event.created = timezone.now() - timedelta(days=8)
        self.assertFalse(self.event.was_publiched_recently())
        
    def test_save_method(self):
        self.event.closing_registration_date = timezone.now() - timedelta(hours=12)
        self.event.save()
        self.assertLessEqual(self.event.closing_registration_date, self.event.start_datetime)
        
        self.event.max_visitors = 5
        self.event.save()
        self.assertEqual(self.event.max_visitors, 5)
        
        self.event.image = None
        self.event.save()
        self.assertIsNotNone(self.event.image)