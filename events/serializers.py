from django.utils import timezone
from rest_framework import serializers

from .models import (EventRegistrations, Events, EventTypes, EventVenues,
                     PaidEventRegistrations, PaidEvents,
                     PrivateEventRegistrations, PrivateEvents)

# Serializers


# Event Registrations serializers

class EventRegistrationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistrations
        fields = '__all__'
        read_only_fields = ('shortuuid', )


    def validate(self, attrs):
        event = attrs.get("event")
        if event and event.closing_registration_date and event.closing_registration_date <= timezone.now():
            raise serializers.ValidationError({"closing_registration_date": "Нельзя зарегестрироваться после указанного времени закрытия регистрации"})
        return attrs


class PrivateEventRegistrationsSerializer(EventRegistrationsSerializer):
    class Meta:
        model = PrivateEventRegistrations
        fields = '__all__'
        read_only_fields = ('shortuuid', )



class PaidEventRegistrationsSerializer(EventRegistrationsSerializer):
    class Meta:
        model = PaidEventRegistrations
        fields = '__all__'
        read_only_fields = ('shortuuid', 'payment_status', 'payment_link')


class EventInvitationsSerializer(EventRegistrationsSerializer):
    class Meta:
        model = EventRegistrations
        fields = ('user', )
        extra_kwargs = {'invitation_code': {'read_only': False}}


class PrivateEventsCodeInvitationsSerializer(serializers.Serializer):
    invitation_code = serializers.CharField(label='UUID для приглашения на мероприятие', max_length=10, required=True)

    def validate_invitation_code(self, value):
        pk = self.context.get("pk")
        event = PrivateEvents.objects.filter(pk=pk).first()

        if pk and event and not event.invitation_code == value:
            raise serializers.ValidationError("Неправильный код приглашения")

        return value


# Events serializers

class EventsSerializer(serializers.ModelSerializer):
    visitors = serializers.SerializerMethodField()

    class Meta:
        model = Events
        fields = '__all__'
        depth = 1

    def get_visitors(self, obj):
        queryset = EventRegistrations.objects.filter(
            is_invitation_accepted=True,
            event=obj.id
        ).order_by('-id')
        serializer = EventRegistrationsSerializer(queryset, many=True)
        return serializer.data


class PrivateEventsSerializer(serializers.ModelSerializer):
    visitors = serializers.SerializerMethodField()
    
    class Meta:
        model = PrivateEvents
        exclude = ('invitation_code', )
        
    def get_visitors(self, obj):
        queryset = PrivateEventRegistrations.objects.filter(
            is_invitation_accepted=True,
            event=obj.id
        ).order_by('-id')
        serializer = PrivateEventRegistrationsSerializer(queryset, many=True)
        return serializer.data


class PaidEventsSerializer(serializers.ModelSerializer):
    visitors = serializers.SerializerMethodField()
    
    class Meta:
        model = PaidEvents
        exclude = ('invitation_code', )
        
    def get_visitors(self, obj):
        queryset = PaidEventRegistrations.objects.filter(
            is_invitation_accepted=True,
            event=obj.id,
            payment_status=PaidEventRegistrations.PaymentStatuses.PAID
        ).order_by('-id')
        serializer = PaidEventRegistrationsSerializer(queryset, many=True)
        return serializer.data


# Other events serializers

class EventVenuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventVenues
        fields = '__all__'


class EventTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTypes
        fields = '__all__'
        