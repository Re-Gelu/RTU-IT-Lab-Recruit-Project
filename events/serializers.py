from rest_framework import serializers
from .models import *

# Serializers

class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = '__all__'
        
        
class PrivateEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateEvents
        fields = '__all__'
        
        
class EventVenuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventVenues
        fields = '__all__'
        

class EventTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTypes
        fields = '__all__'


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistrations
        exclude = ['is_invitation_accepted', 'id']
        
        
    def validate(self, attrs):
        event = attrs["event_id"]
        if event.closing_registration_date and event.closing_registration_date <= timezone.now():
            raise serializers.ValidationError({"closing_registration_date": "Нельзя зарегестрироваться после указанного времени закрытия регистрации"})
        return attrs
    

""" class EventRegistrationSerializer(serializers.Serializer):
    ... """