from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from config.permissions import ReadOnly, ReadOnlyIfAuthenticated

from .mixins import (PaymentRegistrationModelMixin,
                     PrivateInvitationModelMixin, RegistrationModelMixin)
from .models import (EventRegistrations, Events, EventTypes, EventVenues,
                     PaidEventRegistrations, PaidEvents,
                     PrivateEventRegistrations, PrivateEvents)
from .serializers import (EventRegistrationsSerializer, EventsSerializer,
                          EventTypesSerializer, EventVenuesSerializer,
                          PaidEventRegistrationsSerializer,
                          PaidEventsSerializer,
                          PrivateEventRegistrationsSerializer,
                          PrivateEventsSerializer)

# Кэшируются только GET и HEAD ответы со статусом 200
default_decorators = (cache_page(getattr(settings, 'CACHING_TIME', 60)), vary_on_headers("Authorization",))


# ViewSets


@method_decorator(default_decorators, name="dispatch")
class EventsViewSet(viewsets.ModelViewSet, RegistrationModelMixin):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]
    
    filterset_fields = {
        'name': ['iexact', 'icontains'],
        'venue': ['exact'],
        'category': ['exact'],
        'start_datetime': ['gte', 'lte'],
        'duration': ['gte', 'lte'],
        'closing_registration_date': ['gte', 'lte'],
    }

    event_registration_serializer_class = EventRegistrationsSerializer
    event_registration_model = EventRegistrations


@method_decorator(default_decorators, name="dispatch")
class PrivateEventsViewSet(viewsets.ModelViewSet, PrivateInvitationModelMixin):
    queryset = PrivateEvents.objects.all()
    serializer_class = PrivateEventsSerializer
    permission_classes = [ReadOnlyIfAuthenticated | IsAdminUser, ]
    
    filterset_fields = EventsViewSet.filterset_fields.copy()

    event_registration_serializer_class = PrivateEventRegistrationsSerializer
    event_registration_model = PrivateEventRegistrations


@method_decorator(default_decorators, name="dispatch")
class PaidEventsViewSet(viewsets.ModelViewSet, PaymentRegistrationModelMixin, PrivateInvitationModelMixin):
    queryset = PaidEvents.objects.all()
    serializer_class = PaidEventsSerializer
    permission_classes = [ReadOnlyIfAuthenticated | IsAdminUser, ]

    filterset_fields = PrivateEventsViewSet.filterset_fields.copy()
    filterset_fields.update({'price': ['exact', 'gte', 'lte']})

    event_registration_serializer_class = PaidEventRegistrationsSerializer
    event_registration_model = PaidEventRegistrations


@method_decorator(default_decorators, name="dispatch")
class EventVenuesViewSet(viewsets.ModelViewSet):
    queryset = EventVenues.objects.all()
    serializer_class = EventVenuesSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]

    filterset_fields = {
        'name': ['iexact', 'icontains'],
        'address': ['iexact', 'icontains'],
        'latitude': ['gte', 'lte'],
        'longitude': ['gte', 'lte'],
    }


@method_decorator(default_decorators, name="dispatch")
class EventTypesViewSet(viewsets.ModelViewSet):
    queryset = EventTypes.objects.all()
    serializer_class = EventTypesSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]

    filterset_fields = {
        'name': ['iexact', 'icontains'],
    }


class EventsRegistrationsViewSet(viewsets.ModelViewSet):
    queryset = EventRegistrations.objects.all()
    serializer_class = EventRegistrationsSerializer
    permission_classes = [ReadOnly | IsAuthenticated, ]


class PrivateEventsRegistrationsViewSet(viewsets.ModelViewSet):
    queryset = PrivateEventRegistrations.objects.all()
    serializer_class = PrivateEventRegistrationsSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]
