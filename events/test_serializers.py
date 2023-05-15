import datetime
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .models import Events
from .serializers import EventsSerializer

events_serializer = EventsSerializer

class EventsSerializerTestCase(TestCase):
    def setUp(self):
        self.events_serializer = events_serializer
        self.event =  Events.objects.create(
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


""" from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .serializers import (
    EventsSerializer, 
    PrivateEventsSerializer, 
    EventVenuesSerializer, 
    EventTypesSerializer, 
    EventRegistrationsSerializer, 
    PrivateEventRegistrationsSerializer,
    EventInvitationsSerializer,
)
from .models import (
    Events,
    PrivateEvents,
    EventVenues,
    EventTypes,
    EventRegistrations,
    PrivateEventRegistrations,
)
import datetime


class EventsSerializerTest(TestCase):

    def setUp(self):
        self.event_data = {
            'name': 'Event 1',
            'start_datetime': timezone.now(),
            'category_id': 1,
            'venue_id': 1
        }
    
    def test_create_event(self):
        serializer = EventsSerializer(data=self.event_data)
        self.assertTrue(serializer.is_valid())
        event = serializer.save()
        self.assertEqual(event.name, self.event_data['name'])
        self.assertEqual(event.category_id, self.event_data['category_id'])
        
    def test_update_event(self):
        event = Events.objects.create(**self.event_data)
        event_data_updated = {
            'name': 'Updated event name',
            'start_date': timezone.now(),
            'end_date': timezone.now(),
            'category_id': 2,
            'venue_id': 2
        }
        serializer = EventsSerializer(event, data=event_data_updated)
        self.assertTrue(serializer.is_valid())
        updated_event = serializer.save()
        self.assertEqual(updated_event.name, event_data_updated['name'])
        self.assertEqual(updated_event.category_id, event_data_updated['category_id'])
        

class EventRegistrationsSerializerTest(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create(username='test_user')
        self.event = Events.objects.create(
            name='Test event',
            start_date=timezone.now(),
            end_date=timezone.now(),
            category_id=1,
            venue_id=1
        )
        self.event_registration_data = {
            'user': self.user.id,
            'event': self.event.id
        }
    
    def test_create_event_registration(self):
        serializer = EventRegistrationsSerializer(data=self.event_registration_data)
        self.assertTrue(serializer.is_valid())
        event_registration = serializer.save()
        self.assertEqual(event_registration.user, self.user)
        self.assertEqual(event_registration.event, self.event)
        
    def test_update_event_registration(self):
        event_registration = EventRegistrations.objects.create(
            user=self.user,
            event=self.event
        )
        event_registration_data_updated = {
            'is_invitation_accepted': True
        }
        serializer = EventRegistrationsSerializer(event_registration, data=event_registration_data_updated)
        self.assertTrue(serializer.is_valid())
        updated_event_registration = serializer.save()
        self.assertEqual(updated_event_registration.is_invitation_accepted, event_registration_data_updated['is_invitation_accepted'])
        
    def test_event_registration_validation(self):
        event_with_closing_date = Events.objects.create(
            name='Test event with closing date',
            start_date=timezone.now(),
            end_date=timezone.now(),
            category_id=1,
            venue_id=1,
            closing_registration_date=timezone.now() - timezone.timedelta(hours=1)
        )
        event_registration_data = {
            'user': self.user.id,
            'event': event_with_closing_date.id
        }
        serializer = EventRegistrationsSerializer(data=event_registration_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('closing_registration_date', serializer.errors) """