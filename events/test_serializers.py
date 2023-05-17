import datetime
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import (EventRegistrations, Events, PaidEventRegistrations,
                     PaidEvents, PrivateEventRegistrations, PrivateEvents)
from .serializers import (EventsSerializer, PrivateEventsSerializer, PaidEventsSerializer, 
                          EventRegistrationsSerializer, PaidEventRegistrationsSerializer, 
                          EventInvitationsSerializer, PrivateEventsCodeInvitationsSerializer, 
                          PrivateEventRegistrationsSerializer)

class EventsSerializerTest(TestCase):
    def setUp(self):
        self.event =  Events.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        self.user1 = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        self.user2 = get_user_model().objects.create(
            username='user2@test.com',
            email='user2@test.com',
            password='testpass123'
        )
        self.user3 = get_user_model().objects.create(
            username='user3@test.com',
            email='user3@test.com',
            password='testpass123'
        )
        
    def test_get_visitors(self):
        EventRegistrations.objects.create(
            event=self.event,
            user=self.user1,
            is_invitation_accepted=True
        )
        EventRegistrations.objects.create(
            event=self.event,
            user=self.user2,
            is_invitation_accepted=True
        )
        EventRegistrations.objects.create(
            event=self.event,
            user=self.user3,
            is_invitation_accepted=False
        )
        serializer = EventsSerializer(self.event)
        self.assertEqual(len(serializer.data['visitors']), 2)

class PrivateEventsSerializerTest(TestCase):
    def setUp(self):
        self.event =  PrivateEvents.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        self.user1 = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        self.user2 = get_user_model().objects.create(
            username='user2@test.com',
            email='user2@test.com',
            password='testpass123'
        )
        self.user3 = get_user_model().objects.create(
            username='user3@test.com',
            email='user3@test.com',
            password='testpass123'
        )
        
    def test_get_visitors(self):
        PrivateEventRegistrations.objects.create(
            event=self.event,
            user=self.user1,
            is_invitation_accepted=True
        )
        PrivateEventRegistrations.objects.create(
            event=self.event, 
            user=self.user2,
            is_invitation_accepted=True
        )
        PrivateEventRegistrations.objects.create(
            event=self.event,
            user=self.user3, 
            is_invitation_accepted=False
        )
        serializer = PrivateEventsSerializer(self.event)
        self.assertEqual(len(serializer.data['visitors']), 2)

class PaidEventsSerializerTest(TestCase):
    def setUp(self):
        self.event =  PaidEvents.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        self.user1 = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        self.user2 = get_user_model().objects.create(
            username='user2@test.com',
            email='user2@test.com',
            password='testpass123'
        )
        self.user3 = get_user_model().objects.create(
            username='user3@test.com',
            email='user3@test.com',
            password='testpass123'
        )
        
    def test_get_visitors(self):
        PaidEventRegistrations.objects.create(
            event=self.event,
            user=self.user1,
            is_invitation_accepted=True,
            payment_status='PAID'
        )
        PaidEventRegistrations.objects.create(
            event=self.event, 
            user=self.user2,
            is_invitation_accepted=True,
            payment_status='PAID'
        )
        PaidEventRegistrations.objects.create(
            event=self.event, 
            user=self.user3,
            is_invitation_accepted=True
        )
        serializer = PaidEventsSerializer(self.event)
        self.assertEqual(len(serializer.data['visitors']), 2)
        

class EventRegistrationsSerializerTest(TestCase):
    def setUp(self):  
        self.user = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        
    def test_validate_closing_registration_date(self):
        event = Events.objects.create(
            name='Test Event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() - timezone.timedelta(days=1)
        )
        data = {
            'event': event.pk,
            'user': self.user.pk
        }
        serializer = EventRegistrationsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('closing_registration_date', serializer.errors)

    def test_valid_data(self):
        event = Events.objects.create(
            name='Test Event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        data = {
            'event': event.pk,
            'user': self.user.pk
        }
        serializer = EventRegistrationsSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class PrivateEventRegistrationsSerializerTest(TestCase):
    def setUp(self):  
        self.user = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        self.event = PrivateEvents.objects.create(
            name='Test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        
    def test_valid_data(self):
        data = {
            'event': self.event.id,
            'user': self.user.id
        }
        serializer = PrivateEventRegistrationsSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class PaidEventRegistrationsSerializerTest(TestCase):
    def setUp(self):  
        self.user = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        self.event = PaidEvents.objects.create(
            name='Test Event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        
    def test_valid_data(self):
        data = {
            'event': self.event.id,
            'user': self.user.id,
            'payment_status': 'PAID',
            'payment_link': 'http://example.com/payment'
        }
        serializer = PaidEventRegistrationsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        

class EventInvitationsSerializerTest(TestCase):
    def setUp(self):  
        self.user = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        self.event = Events.objects.create(
            name='Test Event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        
    def test_valid_data(self):
        data = {
            'event': self.event.id,
            'user': self.user.id
        }
        serializer = EventInvitationsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        

class PrivateEventsCodeInvitationsSerializerTest(TestCase):
    def setUp(self):  
        self.user = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        self.event = PrivateEvents.objects.create(
            name='Test Event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        
    def test_valid_invitation_code(self):
        data = {
            'invitation_code': self.event.invitation_code
        }
        context = {'pk': self.event.pk}
        serializer = PrivateEventsCodeInvitationsSerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid())

    def test_invalid_invitation_code(self):
        data = {
            'invitation_code': '123456'
        }
        context = {'pk': self.event.pk}
        serializer = PrivateEventsCodeInvitationsSerializer(data=data, context=context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('invitation_code', serializer.errors)