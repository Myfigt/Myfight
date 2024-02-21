from django.contrib.auth import login

from rest_framework import generics, permissions #, mixins,serializers
# from rest_framework.response import Response
# from knox.models import AuthToken
from .serializers import UserSerializer,UpdateUserSerializer, ChangePasswordSerializer
from django.contrib.auth import get_user_model
# from rest_framework.settings import api_settings
# from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser


class GetProfile(generics.RetrieveAPIView):
  permission_classes = [
      permissions.IsAuthenticated
  ]
  serializer_class = UserSerializer

  def get_object(self):
    return self.request.user

class UpdateProfile(generics.UpdateAPIView):
    parser_classes = (MultiPartParser, FormParser,)
    
    User = get_user_model()
    queryset = User.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    
    serializer_class = UpdateUserSerializer

      
class ChangePassword(generics.UpdateAPIView):
      User = get_user_model()
      queryset = User.objects.all()
      permission_classes = [
          permissions.IsAuthenticated
      ]
      serializer_class = ChangePasswordSerializer


