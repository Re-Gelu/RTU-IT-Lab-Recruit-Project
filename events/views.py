from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from config.permissions import ReadOnly, ReadOnlyIfAuthenticated
from .models import *
from .serializers import *

# ViewSets

class EventsViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """ Отправить приглашение на конкретное мероприятие пользователю или группе пользователей """
        return Response({})
    
    @action(detail=True, methods=['get'])
    def invitations(self, request, pk=None):
        """ Получить список приглашений на конкретное мероприятие """
        return Response({})
        
    @action(detail=True, methods=['get'])
    def guestlist(self, request, pk=None):
        """ Получить список пользователей, принявших приглашение на конкретное мероприятие """
        event = self.get_object()
        return Response(event.visitors_list, status=status.HTTP_200_OK)
    

class PrivateEventsViewSet(EventsViewSet):
    queryset = PrivateEvents.objects.all()
    serializer_class = PrivateEventsSerializer
    permission_classes = [ReadOnlyIfAuthenticated | IsAdminUser, ]
    
    
class EventsRegistrationsView(viewsets.ModelViewSet):
    queryset = EventsRegistrations.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [ReadOnlyIfAuthenticated | IsAdminUser, ]
    
    """ def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        user = request.user
        
        registration = EventRegistration.objects.create(event=event, user=user)
        serializer = EventRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED) """
