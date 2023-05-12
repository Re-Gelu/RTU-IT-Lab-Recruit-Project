from rest_framework import serializers
from django.utils import timezone
from .models import (Events, PrivateEvents, PaidEvents, EventVenues, EventTypes, 
                     EventRegistrations, PrivateEventRegistrations, PaidEventRegistrations)

# Serializers

class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = '__all__'
        
        
class PrivateEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateEvents
        exclude = ('invitation_code', )
        
        
class PaidEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaidEvents
        exclude = ('invitation_code', )
        
        
class EventVenuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventVenues
        fields = '__all__'
        

class EventTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTypes
        fields = '__all__'


class EventRegistrationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistrations
        fields = '__all__'
        read_only_fields = ('shortuuid', )
        
        
    def validate(self, attrs):
        event = attrs.get("event_id")
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
            fields = ('user_id', )
            extra_kwargs = {'invitation_code': {'read_only': False}}
            

class PrivateEventsCodeInvitationsSerializer(serializers.Serializer):
    invitation_code = serializers.CharField(label='UUID для приглашения на мероприятие', max_length=10, required=True)
            
    def validate_invitation_code(self, value):
        pk = self.context.get("pk")
        event = PrivateEvents.objects.filter(pk=pk).first()
        
        if pk and event and not event.invitation_code == value:
            raise serializers.ValidationError("Неправильный код приглашения")
            
        return value