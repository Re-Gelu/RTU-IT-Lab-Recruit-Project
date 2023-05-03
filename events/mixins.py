from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class RegistrationModelMixin:
    """ Adds event registration functionality.
    
    Required fields: 
    1) event_registration_model
    2) event_registration_serializer_class """
    
    @action(detail=True, methods=['post'], serializer_class=None, permission_classes=[IsAuthenticated, ])
    def registration(self, request, pk=None):
        """ Зарегестрироваться на конкретное мероприятие пользователю или группе пользователей """
        current_user = request.user
        serializer = self.event_registration_serializer_class(data={"event_id": pk, "user_id": current_user.id})
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