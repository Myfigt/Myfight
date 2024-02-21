"""myfight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import routing

# from api.views import RegisterAPI
from api.views import (
    AcceptFriendRequestAPI,
    AddFriendAPI,
    AddTribeAPI,
    JoinTribeAPI,
    ListFriendRequestsAPI,
    ListFriendsAPI,
    ListTribes,
    RemoveFriendAPI,
    SearchPlayerAPI,
    SendNotificationsAPI,
    Signup,
    TestAPI,
    UpdateOnlineStatusAPI,
    UploadPlayerVideo,
    FighterSignup,
)
from django.urls import path
from knox import views as knox_views
from api.loginview import LoginAPI, LogoutAPI
from api.profile import GetProfile, UpdateProfile, ChangePassword
from api.fighters import GetFighters, GetFighterVideos, GetActionCards
from django.contrib import admin
from django.urls import path, include
from api.views import (
    UploadPlayerVideo,
    GetPlayerVideos,
    CompareActions,
    FightStrategyView,
    ListFightStrategy,
    DeletePlayerVideo,
)

# from api.views import FightStrategyVideoView, ListFightStrategyVideos
from api.pages_view import privacy_policy, terms_conditions

from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = "MyFight CMS"
admin.site.site_title = "MyFight CMS"

# we have 3 users in the system: admin, player, fighter/master

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/signup", Signup.as_view(), name="register"),  # player signup
    path("api/login", LoginAPI.as_view(), name="login"),  # player signin
    path("api/user_profile", GetProfile.as_view()),
    path("api/profile/<int:pk>", UpdateProfile.as_view(), name="profile"),
    path("api/test_api", TestAPI.as_view()),
    path("api/upload_video", UploadPlayerVideo.as_view()),
    path("api/player_videos/<int:player_id>", GetPlayerVideos.as_view({"get": "list"})),
    path("api/delete_player_video", DeletePlayerVideo.as_view()),
    # fighter/master
    path("api/fighter-signup", FighterSignup.as_view(), name="fighter-register"),
    path("api/fighter-login", LoginAPI.as_view(), name="fighter-login"),
    path("api/get_fighters", GetFighters.as_view({"get": "list"})),
    path(
        "api/fighter_videos/<int:fighter_id>/<str:belt_type>",
        GetFighterVideos.as_view({"get": "list"}),
    ),
    path(
        "api/action_cards_list/<int:fighter_id>",
        GetActionCards.as_view({"get": "list"}),
    ),
    path("api/create_fight_strategy", FightStrategyView.as_view()),
    path(
        "api/list_fight_strategy/<int:player_id>",
        ListFightStrategy.as_view({"get": "list"}),
    ),
    # path('api/add_fight_strategy_video', FightStrategyVideoView.as_view()),
    # path('api/list_fight_strategy_videos/<int:fight_strategy_id>', ListFightStrategyVideos.as_view({'get': 'list'})),
    path("api/add_tribe", AddTribeAPI.as_view()),
    path("api/list_tribes", ListTribes.as_view({"get": "list"})),
    path("api/join_leave_tribe/<int:pk>", JoinTribeAPI.as_view(), name="join_tribe"),
    path("api/send_fcm", SendNotificationsAPI.as_view()),
    #     friends api list
    path("api/add_friend", AddFriendAPI.as_view(), name="add_friend"),
    path("api/list_friends", ListFriendsAPI.as_view()),
    path("api/list_friend_requests", ListFriendRequestsAPI.as_view()),
    path("api/accept_friend_request", AcceptFriendRequestAPI.as_view()),
    path("api/search_player", SearchPlayerAPI.as_view()),
    path("api/make_user_online_offline", UpdateOnlineStatusAPI.as_view()),
    path("api/remove_friend", RemoveFriendAPI.as_view()),
    # optimize
    # path('api/logout', knox_views.LogoutView.as_view(), name='logout'),
    path("api/logout", LogoutAPI.as_view(), name="knox_logout"),
    path("api/logoutall", knox_views.LogoutAllView.as_view(), name="logoutall"),
    path(
        "api/change_password/<int:pk>", ChangePassword.as_view(), name="change_password"
    ),
    # path('api/forgot_password', ForgotPassword.as_view(), name='forgot_password'),
    path(
        "api/password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("api/compare_actions", CompareActions.as_view()),
    # website
    path("privacy-policy", privacy_policy, name="privacy-policy"),
    path("terms-conditions", terms_conditions, name="terms-conditions"),
    # path("ws/", include(routing.websocket_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
