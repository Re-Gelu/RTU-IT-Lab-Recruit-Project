from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import (Events, PrivateEvents, EventVenues, EventTypes, 
                     EventRegistrations, PrivateEventRegistrations)


class EventsModelsTest(TestCase):
    
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
        self.private_event = Events.objects.create(
            name='Test private Event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=12),
            venue_id=venue,
            category_id=event_type,
            max_visitors=10,
        )
        
        EventRegistrations.objects.create(
            user_id=get_user_model().objects.create(
                username='user@test.com',
                email='user@test.com',
                password='testpass123'
            ),
            event_id=self.event
        )
        
        
    def test_str_method(self):
        self.assertEqual(str(self.event), 'Test Event')
        self.assertEqual(str(self.private_event), 'Test private Event')
        
    def test_end_datetime(self):
        expected_end_datetime = self.event.start_datetime + self.event.duration
        self.assertEqual(self.event.end_datetime(), expected_end_datetime)
        
        expected_end_datetime = self.private_event.start_datetime + self.private_event.duration
        self.assertEqual(self.private_event.end_datetime(), expected_end_datetime)
        
    def test_was_published_recently(self):
        self.assertTrue(self.event.was_publiched_recently())
        self.event.created = timezone.now() - timedelta(days=8)
        self.assertFalse(self.event.was_publiched_recently())
        
        self.assertTrue(self.private_event.was_publiched_recently())
        self.private_event.created = timezone.now() - timedelta(days=8)
        self.assertFalse(self.private_event.was_publiched_recently())
    
    def test_visitors_len(self):
        self.assertEqual(self.event.visitors_len(), 1)
        
    def test_save_method(self):
        self.event.closing_registration_date = timezone.now() - timedelta(hours=12)
        self.event.save()
        self.assertLessEqual(self.event.closing_registration_date, self.event.start_datetime)
        
        self.private_event.closing_registration_date = timezone.now() - timedelta(hours=12)
        self.private_event.save()
        self.assertLessEqual(self.private_event.closing_registration_date, self.private_event.start_datetime)
        
        self.event.max_visitors = 5
        self.event.save()
        self.assertEqual(self.event.max_visitors, 5)
        
        self.private_event.max_visitors = 5
        self.private_event.save()
        self.assertEqual(self.private_event.max_visitors, 5)
        
        self.event.image = None
        self.event.save()
        self.assertIsNotNone(self.event.image)
        
        self.private_event.image = None
        self.private_event.save()
        self.assertIsNotNone(self.private_event.image)
        

class EventVenuesTest(TestCase):
    def setUp(self):
        self.event_venue = EventVenues.objects.create(
            name='Test Venue', address='Test Address', latitude=Decimal('45.523064'),
            longitude=Decimal('-122.676483'), created=timezone.now()
        )

    def test_event_venue_creation(self):
        self.assertTrue(isinstance(self.event_venue, EventVenues))
        self.assertEqual(self.event_venue.__str__(), self.event_venue.name)
        self.assertEqual(self.event_venue.name, 'Test Venue')
        self.assertEqual(self.event_venue.address, 'Test Address')
        self.assertEqual(self.event_venue.latitude, Decimal('45.523064'))
        self.assertEqual(self.event_venue.longitude, Decimal('-122.676483'))
        self.assertIsInstance(self.event_venue.created, timezone.datetime)
        self.assertIsInstance(self.event_venue.updated, timezone.datetime)

    def test_event_venue_save(self):
        self.event_venue.name = 'New Test Venue'
        self.event_venue.save()
        self.assertEqual(self.event_venue.name, 'New Test Venue')
        self.assertIsInstance(self.event_venue.updated, timezone.datetime)
        
    def test_created_and_updated_fields(self):
        self.assertIsNotNone(self.event_venue.created)
        self.assertIsNotNone(self.event_venue.updated)
        self.assertIsInstance(self.event_venue.created, timezone.datetime)
        self.assertIsInstance(self.event_venue.updated, timezone.datetime)
        
    def test_longitude_decimal_places(self):
        event_venue = EventVenues.objects.get(id=1)
        field_decimal_places = event_venue._meta.get_field('longitude').decimal_places
        self.assertEqual(field_decimal_places, 6)
        
    def test_event_venues_str_method(self):
        venue = EventVenues.objects.get(name='Test Venue')
        self.assertEqual(str(venue), 'Test Venue')
        

class EventTypesTest(TestCase):
    def setUp(self):
        self.event_type = EventTypes.objects.create(name='Test Type', created=timezone.now())

    def test_event_type_creation(self):
        self.assertTrue(isinstance(self.event_type, EventTypes))
        self.assertEqual(self.event_type.__str__(), self.event_type.name)
        self.assertEqual(self.event_type.name, 'Test Type')
        self.assertIsInstance(self.event_type.created, timezone.datetime)
        self.assertIsInstance(self.event_type.updated, timezone.datetime)

    def test_event_type_save(self):
        self.event_type.name = 'New Test Type'
        self.event_type.save()
        self.assertEqual(self.event_type.name, 'New Test Type')
        self.assertIsInstance(self.event_type.updated, timezone.datetime)
        
    def test_event_types_str_method(self):
        event_type = EventTypes.objects.get(name='Test Type')
        self.assertEqual(str(event_type), 'Test Type')


class EventRegistrationsTest(TestCase):
    
    def setUp(self):
        self.user = self.user = get_user_model().objects.create(
            username='user@test.com',
            email='user@test.com',
            password='testpass123'
        )
        self.event = Events.objects.create(
            name='test event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        self.private_event = PrivateEvents.objects.create(
            name='test private event',
            start_datetime=timezone.now() + timedelta(days=1),
            closing_registration_date=timezone.now() + timedelta(hours=1)
        )
        
    def test_event_registration_creation(self):
        event_registration = EventRegistrations.objects.create(
            event_id=self.event,
            user_id=self.user
        )
        self.assertEqual(event_registration.__str__(), f"Запись на мероприятие №{event_registration.shortuuid}, ID мероприятия - {self.event}, ID мользователя - {self.user}")
        self.assertEqual(event_registration.inviting_user_id, self.user)
        self.assertFalse(event_registration.is_invitation_accepted)
        
    def test_private_event_registration_creation(self):
        private_event_registration = PrivateEventRegistrations.objects.create(
            event_id=self.private_event,
            user_id=self.user
        )
        self.assertEqual(private_event_registration.__str__(), f"Запись на приватное мероприятие №{private_event_registration.shortuuid}, ID мероприятия - {self.private_event}, ID мользователя - {self.user}")
        self.assertEqual(private_event_registration.inviting_user_id, self.user)
        self.assertFalse(private_event_registration.is_invitation_accepted)
        
    def test_event_registration_unique_constraint(self):
        EventRegistrations.objects.create(
            event_id=self.event,
            user_id=self.user
        )
        with self.assertRaises(Exception):
            EventRegistrations.objects.create(
                event_id=self.event,
                user_id=self.user
            )
        
    def test_private_event_registration_unique_constraint(self):
        PrivateEventRegistrations.objects.create(
            event_id=self.private_event,
            user_id=self.user
        )
        with self.assertRaises(Exception):
            PrivateEventRegistrations.objects.create(
                event_id=self.private_event,
                user_id=self.user
            )
            
    def test_save_method(self):
        # Создание записи без inviting_user_id
        event_reg = EventRegistrations.objects.create(
            event_id=self.event, user_id=self.user
        )
        self.assertEqual(event_reg.inviting_user_id, self.user)
        
        event_reg.delete()
        
        # Создание записи с inviting_user_id
        inviting_user = get_user_model().objects.create_user(
            username='invitinguser',
            password='password'
        )
        event_reg = EventRegistrations.objects.create(
            event_id=self.event, user_id=self.user, inviting_user_id=inviting_user
        )
        self.assertEqual(event_reg.inviting_user_id, inviting_user)