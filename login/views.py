from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Group
from rest_framework import viewsets
from config.permissions import ReadOnly
from .models import *
from .serializers import GroupSerializer

# ViewSets

class GroupsViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [ReadOnly | IsAdminUser, ]