from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from config.permissions import ReadOnly, ReadOnlyIfAuthenticated
from .models import *
from .serializers import *
from .mixins import RegistrationModelMixin, InvitationModelMixin, PrivateInvitationModelMixin

# ViewSets

class EventsViewSet(viewsets.ModelViewSet, RegistrationModelMixin, InvitationModelMixin):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]
    
    event_registration_serializer_class = EventRegistrationsSerializer
    event_registration_model = EventRegistrations
    

class PrivateEventsViewSet(viewsets.ModelViewSet, RegistrationModelMixin, PrivateInvitationModelMixin):
    queryset = PrivateEvents.objects.all()
    serializer_class = PrivateEventsSerializer
    permission_classes = [ReadOnlyIfAuthenticated | IsAdminUser, ]
    
    event_registration_serializer_class = PrivateEventRegistrationsSerializer
    event_registration_model = PrivateEventRegistrations
    
    
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