from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import viewsets
from config.permissions import ReadOnly, ReadOnlyIfAuthenticated
from .models import (Events, PrivateEvents, PaidEvents, EventVenues, EventTypes, 
                     EventRegistrations, PrivateEventRegistrations, PaidEventRegistrations)
from .serializers import (EventsSerializer, PrivateEventsSerializer, PaidEventsSerializer, 
                          EventVenuesSerializer, EventTypesSerializer, EventRegistrationsSerializer,
                          PrivateEventRegistrationsSerializer, PaidEventRegistrationsSerializer)
from .mixins import (RegistrationModelMixin, InvitationModelMixin, 
                     PrivateInvitationModelMixin, PaymentRegistrationModelMixin)

# ViewSets

class EventsViewSet(viewsets.ModelViewSet, RegistrationModelMixin):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]
    
    event_registration_serializer_class = EventRegistrationsSerializer
    event_registration_model = EventRegistrations
    

class PrivateEventsViewSet(viewsets.ModelViewSet, PrivateInvitationModelMixin):
    queryset = PrivateEvents.objects.all()
    serializer_class = PrivateEventsSerializer
    permission_classes = [ReadOnlyIfAuthenticated | IsAdminUser, ]
    
    event_registration_serializer_class = PrivateEventRegistrationsSerializer
    event_registration_model = PrivateEventRegistrations

class PaidEventsViewSet(viewsets.ModelViewSet, PaymentRegistrationModelMixin):
    queryset = PaidEvents.objects.all()
    serializer_class = PaidEventsSerializer
    permission_classes = [ReadOnlyIfAuthenticated | IsAdminUser, ]
    
    event_registration_serializer_class = PaidEventRegistrationsSerializer
    event_registration_model = PaidEventRegistrations
    
class EventsRegistrationsViewSet(viewsets.ModelViewSet):
    queryset = EventRegistrations.objects.all()
    serializer_class = EventRegistrationsSerializer
    permission_classes = [ReadOnly | IsAuthenticated, ]
    

class PrivateEventsRegistrationsViewSet(viewsets.ModelViewSet):
    queryset = PrivateEventRegistrations.objects.all()
    serializer_class = PrivateEventRegistrationsSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]
        

class EventVenuesViewSet(viewsets.ModelViewSet):
    queryset = EventVenues.objects.all()
    serializer_class = EventVenuesSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]


class EventTypesViewSet(viewsets.ModelViewSet):
    queryset = EventTypes.objects.all()
    serializer_class = EventTypesSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]