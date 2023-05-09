from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import viewsets
from config.permissions import ReadOnly, ReadOnlyIfAuthenticated
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers
from django.conf import settings
from .models import (Events, PrivateEvents, PaidEvents, EventVenues, EventTypes, 
                     EventRegistrations, PrivateEventRegistrations, PaidEventRegistrations)
from .serializers import (EventsSerializer, PrivateEventsSerializer, PaidEventsSerializer, 
                          EventVenuesSerializer, EventTypesSerializer, EventRegistrationsSerializer,
                          PrivateEventRegistrationsSerializer, PaidEventRegistrationsSerializer)
from .mixins import (RegistrationModelMixin, PrivateInvitationModelMixin, PaymentRegistrationModelMixin)

# Кэшируются только GET и HEAD ответы со статусом 200
CACHING_TIME = getattr(settings, 'CACHING_TIME', 60)
default_decorators = (cache_page(CACHING_TIME), vary_on_headers("Authorization",))


# ViewSets


@method_decorator(default_decorators, name="dispatch")
class EventsViewSet(viewsets.ModelViewSet, RegistrationModelMixin):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]
    
    event_registration_serializer_class = EventRegistrationsSerializer
    event_registration_model = EventRegistrations
    

@method_decorator(default_decorators, name="dispatch")
class PrivateEventsViewSet(viewsets.ModelViewSet, PrivateInvitationModelMixin):
    queryset = PrivateEvents.objects.all()
    serializer_class = PrivateEventsSerializer
    permission_classes = [ReadOnlyIfAuthenticated | IsAdminUser, ]
    
    event_registration_serializer_class = PrivateEventRegistrationsSerializer
    event_registration_model = PrivateEventRegistrations


@method_decorator(default_decorators, name="dispatch")
class PaidEventsViewSet(viewsets.ModelViewSet, PaymentRegistrationModelMixin):
    queryset = PaidEvents.objects.all()
    serializer_class = PaidEventsSerializer
    permission_classes = [ReadOnlyIfAuthenticated | IsAdminUser, ]
    
    event_registration_serializer_class = PaidEventRegistrationsSerializer
    event_registration_model = PaidEventRegistrations
    

@method_decorator(default_decorators, name="dispatch")
class EventVenuesViewSet(viewsets.ModelViewSet):
    queryset = EventVenues.objects.all()
    serializer_class = EventVenuesSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]


@method_decorator(default_decorators, name="dispatch")
class EventTypesViewSet(viewsets.ModelViewSet):
    queryset = EventTypes.objects.all()
    serializer_class = EventTypesSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]
    
    
class EventsRegistrationsViewSet(viewsets.ModelViewSet):
    queryset = EventRegistrations.objects.all()
    serializer_class = EventRegistrationsSerializer
    permission_classes = [ReadOnly | IsAuthenticated, ]
    

class PrivateEventsRegistrationsViewSet(viewsets.ModelViewSet):
    queryset = PrivateEventRegistrations.objects.all()
    serializer_class = PrivateEventRegistrationsSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]
