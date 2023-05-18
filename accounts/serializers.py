from django.contrib.auth.models import Group, User
from djoser import serializers as djoser_serializers
from djoser.conf import settings
from rest_framework import serializers

from events.models import (EventRegistrations, Events, EventTypes, EventVenues,
                     PaidEventRegistrations, PaidEvents,
                     PrivateEventRegistrations, PrivateEvents)

from events.serializers import (EventRegistrationsSerializer, PrivateEventRegistrationsSerializer,
                                PaidEventRegistrationsSerializer)


class CustomUserSerializer(djoser_serializers.UserSerializer):
    event_registrations = serializers.SerializerMethodField()
    private_event_registrations = serializers.SerializerMethodField()
    paid_event_registrations = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
        ) + (
            'groups', 'is_staff', 
            'is_superuser', 'is_active',
            'first_name', 'last_name',
            'event_registrations', 'private_event_registrations',
            'paid_event_registrations'
		)
        read_only_fields = (settings.LOGIN_FIELD,'event_registrations', 
                            'private_events_registrations', 'paid_events_registrations')
    
    def get_event_registrations(self, obj):
        queryset = EventRegistrations.objects.filter(
            user=obj.id
        ).order_by('-id')
        serializer = EventRegistrationsSerializer(queryset, many=True)
        return serializer.data
    
    def get_private_event_registrations(self, obj):
        queryset = PrivateEventRegistrations.objects.filter(
            user=obj.id
        ).order_by('-id')
        serializer = PrivateEventRegistrationsSerializer(queryset, many=True)
        return serializer.data
    
    def get_paid_event_registrations(self, obj):
        queryset = PaidEventRegistrations.objects.filter(
            user=obj.id
        ).order_by('-id')
        serializer = PaidEventRegistrationsSerializer(queryset, many=True)
        return serializer.data
        

class CustomUserCreateSerializer(djoser_serializers.UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            "password",
        ) + (
            'first_name', 'last_name'
		)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']