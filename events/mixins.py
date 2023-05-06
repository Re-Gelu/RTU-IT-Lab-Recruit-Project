from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import EventInvitationsSerializer
from .models import EventRegistrations, PrivateEventRegistrations

class RegistrationModelMixin:
    """ Adds event registration functionality.
    
    Required fields in ViewSet: 
    1) event_registration_model
    2) event_registration_serializer_class """
    
    event_registration_serializer_class = None
    event_registration_model = None
    
    @action(detail=True, methods=['post'], serializer_class=None, permission_classes=[IsAuthenticated, ])
    def registration(self, request, pk=None):
        """ Зарегестрироваться на конкретное мероприятие пользователю или группе пользователей """
        current_user = request.user
        serializer = self.event_registration_serializer_class(data={
            "event_id": pk, 
            "user_id": current_user.id,
            "is_invitation_accepted": True,
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @registration.mapping.delete
    def delete_registration(self, request, pk=None):
        """ Удалить регистрацию на конкретное мероприятие пользователю или группе пользователей """
        current_user = request.user
        event_registration = get_object_or_404(self.event_registration_model, event_id=pk, user_id=current_user.id)
        event_registration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class InvitationModelMixin:
    """ Adds event invitation functionality.
    
    Required fields in ViewSet: 
    1) event_registration_model
    2) event_registration_serializer_class """
    
    event_registration_serializer_class = None
    event_registration_model = None
    
    permission_classes=[IsAuthenticated, ]
    
    @action(detail=True, methods=['post'], serializer_class=EventInvitationsSerializer, permission_classes=permission_classes)
    def invitation(self, request, pk=None):
        """ Отправить приглашение на конкретное мероприятие пользователю или группе пользователей """
        current_user = request.user
        serializer = self.event_registration_serializer_class(data={
            "event_id": pk,
            "user_id": request.data.get("user_id"),
            "is_invitation_accepted": False,
            "inviting_user_id": current_user.id
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @invitation.mapping.delete
    def delete_invitation(self, request, pk=None):
        """ Удалить приглашение на конкретное мероприятие пользователю или группе пользователей (Если он еще не принял приглашение) """
        current_user = request.user
        event_registration = get_object_or_404(
            self.event_registration_model, 
            event_id=pk, 
            user_id=current_user.id,
            is_invitation_accepted=False,
        )
        event_registration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], serializer_class=None, permission_classes=[IsAuthenticated, ])
    def confrim_invitation(self, request, pk=None):
        """ Принять приглашение на конкретное мероприятие пользователю или группе пользователей """
        current_user = request.user
        instance = get_object_or_404(
            self.event_registration_model, 
            event_id=pk, 
            user_id=current_user.id,
            is_invitation_accepted=False,
        )
        serializer = self.event_registration_serializer_class(
            instance,
            data={ "is_invitation_accepted": True },
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=permission_classes)
    def guestlist(self, request, pk=None):
        """ Получить список пользователей, принявших приглашение на конкретное мероприятие """
        self.queryset = self.event_registration_model.objects.filter(event_id=pk, is_invitation_accepted=True)
        self.serializer_class = self.event_registration_serializer_class
        return self.list(self, request)
    

class PrivateInvitationModelMixin(InvitationModelMixin):
    """ Adds private event invitation functionality.
    
    Required fields in ViewSet: 
    1) event_registration_model
    2) event_registration_serializer_class """
    
    permission_classes=[IsAdminUser, ]