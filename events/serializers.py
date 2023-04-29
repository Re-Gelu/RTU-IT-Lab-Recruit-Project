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

class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsRegistrations
        fields = '__all__'
