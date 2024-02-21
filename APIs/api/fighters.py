from rest_framework import generics, permissions, viewsets
from .serializers import (
    FighterSerializer,
    FighterVideosSerializer,
    ActionCardsSerializer,
    UserSerializer,
)
from api.models import Fighters, FighterVideos, User


class GetFighters(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]
    queryset = User.objects.filter(is_fighter=1)
    serializer_class = FighterSerializer


class GetFighterVideos(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]
    serializer_class = FighterVideosSerializer

    def get_queryset(self):
        belt_type = self.kwargs["belt_type"]

        if belt_type == "blackbelt":
            belt_type = "black-belt"
        elif belt_type == "bluebeltblackstripe":
            belt_type = "blue-belt-black-stripe"
        elif belt_type == "bluebelt":
            belt_type = "blue-belt"
        elif belt_type == "brownbeltblackstripe":
            belt_type = "brown-belt-black-stripe"
        elif belt_type == "brownbelt":
            belt_type = "brown-belt"
        elif belt_type == "greenbeltblackstripe":
            belt_type = "green-belt-black-stripe"
        elif belt_type == "greenbelt":
            belt_type = "green-belt"
        elif belt_type == "yellowbeltblackstripe":
            belt_type = "yellow-belt-black-stripe"
        elif belt_type == "yellowbelt":
            belt_type = "yellow-belt"

        belt_type = belt_type.title() + "-Final"
        return FighterVideos.objects.filter(
            fighter_id=self.kwargs["fighter_id"], belt=belt_type
        )  # , type='Cam-1'


class GetActionCards(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActionCardsSerializer

    def get_queryset(self):
        return FighterVideos.objects.filter(fighter_id=self.kwargs["fighter_id"])
