from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, permissions

# from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from knox.models import AuthToken

from api.models import (
    FightStrategy,
    FightStrategyVideo,
    Fighters,
    Friends,
    PlayerActionsResult,
    PlayerVideos,
    Tribes,
    User,
    FighterVideos,
)
from .serializers import (
    AddTribe,
    FCMSerializer,
    FriendsList,
    JoinTribe,
    ListFriendRequestsList,
    SearchPlayer,
    TestSerializer,
    TribesList,
    UploadPlayerVideoSerializer,
    PlayerVideosSerializer,
    UserSerializer,
    CompareActionsSerializer,
    FighterUserSerializer,
    FightStrategySerializer,
    FightStrategyVideoSerializer,
    PlayerActionResultSerializer,
    AddFriend,
)  # , RegisterSerializer, LoginSerializer
from django.contrib.auth import get_user_model

# from django.contrib.auth import login
# from rest_framework import status
from django.conf import settings
import sys

sys.path.append("/usr/share/nginx/html/AlphaPose/PoseEstimation_Scoring-Your-Video/")

# from rest_framework.authtoken.serializers import AuthTokenSerializer
# from knox.views import LoginView as KnoxLoginView
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import json, random
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Signup(generics.ListCreateAPIView):
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]
    serializer_class = UserSerializer

    def post(self, request, format=None):
        #
        if "email" not in request.data:
            return Response(
                {
                    "error": True,
                    "message": "Email is required.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        if request.POST["email"] == "":
            return Response(
                {
                    "error": True,
                    "message": "Email is required.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        if "password" not in request.data:
            return Response(
                {
                    "error": True,
                    "message": "Password is required.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        if request.POST["password"] == "":
            return Response(
                {
                    "error": True,
                    "message": "Password is required.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        email = request.POST["email"]
        if get_user_model().objects.filter(email=email).exists():
            # messages.error(request, "This username is already taken")
            return Response(
                {
                    "error": True,
                    "message": "Email is already taken.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            registration_id = request.data["firebase_token"]
            existing_device = FCMDevice.objects.filter(
                registration_id=registration_id
            ).exists()

            if existing_device == False:
                device = FCMDevice()
                device.registration_id = registration_id
                device.type = request.data["device"]
                device.name = "N/A"
                device.device_id = request.data["device_id"]
                if "facebook_id" in request.data:
                    device.facebook_id = request.data["facebook_id"]

                device.user = user
                device.save()

            # return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {
                    "error": False,
                    "message": "Registration successful.",
                    "status": 200,
                    "errors": {},
                    "data": {"user": serializer.data},
                    "access_token": AuthToken.objects.create(user)[1],
                }
            )

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "error": True,
                "message": "Registration failure.",
                "errors": {},
                "data": {},
                "status": 400,
            }
        )


# FighterSignup
class FighterSignup(generics.ListCreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, format=None):
        # request.data['is_fighter'] = True
        if "email" not in request.data:
            return Response(
                {
                    "error": True,
                    "message": "Email is required.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        if request.POST["email"] == "":
            return Response(
                {
                    "error": True,
                    "message": "Email is required.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        if "password" not in request.data:
            return Response(
                {
                    "error": True,
                    "message": "Password is required.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        if request.POST["password"] == "":
            return Response(
                {
                    "error": True,
                    "message": "Password is required.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        email = request.POST["email"]
        if get_user_model().objects.filter(email=email).exists():
            # messages.error(request, "This username is already taken")
            return Response(
                {
                    "error": True,
                    "message": "Email is already taken.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        serializer = FighterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "error": False,
                    "message": "Registration successful.",
                    "status": 200,
                    "errors": {},
                    "data": {"user": serializer.data},
                    "access_token": AuthToken.objects.create(user)[1],
                }
            )

        return Response(
            {
                "error": True,
                "message": "Registration failure.",
                "errors": {},  # serializer.errors,
                "data": {},
                "status": 400,
            }
        )


# Upload file
class UploadPlayerVideo(generics.ListCreateAPIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request, format=None):
        serializer = UploadPlayerVideoSerializer(data=request.data)
        # print serializer.data

        if serializer.is_valid():
            serializer.save()
            filename = serializer.data["FileName"]
            video_id = str(serializer.data["id"])
            print(filename)

            if settings.ENVIRONMENT != "local":
                import os
                import Compare_pose as i2v

                os.system(
                    "python3 scripts/demo_inference.py --cfg configs/coco/resnet/256x192_res50_lr1e-3_1x.yaml --checkpoint pretrained_models/fast_res50_256x192.pth --video /usr/share/nginx/html/my-fight/player_videos/"
                    + filename
                    + " --save_video --outdir /usr/share/nginx/html/my-fight/player_videos/result/"
                    + video_id
                    + " --vis_fast"
                )

                os.system(
                    "/usr/share/nginx/html/my-fight/ffmpeg-5.0-amd64-static/./ffmpeg -i /usr/share/nginx/html/my-fight/player_videos/result/"
                    + video_id
                    + "/AlphaPose_"
                    + filename
                    + " /usr/share/nginx/html/my-fight/player_videos/result/"
                    + video_id
                    + "/"
                    + filename
                )

                fighter_path = FighterVideos.objects.filter(
                    id=serializer.data["fighter_video_id"]
                )
                master = Fighters.objects.filter(id=fighter_path[0].fighter_id)
                result_json = fighter_path[0].file_name.replace("mp4", "json")
                compare_path = (
                    "/usr/share/nginx/html/my-fight/player_videos/uploads/Masters/"
                    + master[0].full_name
                    + "/"
                    + fighter_path[0].belt
                    + "/Cam-1/results/"
                    + result_json
                )
                # print(compare_path)
                i2v.l2_normalize(compare_path)
                i2v.l2_normalize(
                    "/usr/share/nginx/html/my-fight/player_videos/result/"
                    + str(serializer.data["id"])
                    + "/alphapose-results.json"
                )
                compare_path_l2norm = compare_path.replace(".json", "_l2norm.json")
                Score = i2v.dtw_compare(
                    "/usr/share/nginx/html/my-fight/player_videos/result/"
                    + str(serializer.data["id"])
                    + "/alphapose-results_l2norm.json",
                    compare_path_l2norm,
                )
                # print(Score['Total_Score'])

            if settings.ENVIRONMENT != "local":
                Head = round(Score["Head"], 2)
                LShoulder = round(Score["LShoulder"], 2)
                RShoulder = round(Score["RShoulder"], 2)
                RElbow = round(Score["RElbow"], 2)
                LElbow = round(Score["LElbow"], 2)
                LWrist = round(Score["LWrist"], 2)
                RWrist = round(Score["RWrist"], 2)
                LHip = round(Score["LHip"], 2)
                RHip = round(Score["RHip"], 2)
                LKnee = round(Score["LKnee"], 2)
                Rknee = round(Score["Rknee"], 2)
                LAnkle = round(Score["LAnkle"], 2)
                RAnkle = round(Score["RAnkle"], 2)
                Total_Score = round(Score["Total_Score"], 2)

                if Head < 0:
                    Head = 0
                if LShoulder < 0:
                    LShoulder = 0
                if RShoulder < 0:
                    RShoulder = 0
                if LElbow < 0:
                    LElbow = 0
                if RElbow < 0:
                    RElbow = 0
                if LWrist < 0:
                    LWrist = 0
                if RWrist < 0:
                    RWrist = 0
                if LHip < 0:
                    LHip = 0
                if RHip < 0:
                    RHip = 0
                if LKnee < 0:
                    LKnee = 0
                if Rknee < 0:
                    Rknee = 0
                if LAnkle < 0:
                    LAnkle = 0
                if RAnkle < 0:
                    RAnkle = 0
                if Total_Score < 0:
                    Total_Score = 0

                comparison_results = {
                    "Head": Head,
                    "LShoulder": LShoulder,
                    "RShoulder": RShoulder,
                    "LElbow": LElbow,
                    "RElbow": RElbow,
                    "LWrist": LWrist,
                    "RWrist": RWrist,
                    "LHip": LHip,
                    "RHip": RHip,
                    "LKnee": LKnee,
                    "RKnee": Rknee,
                    "LAnkle": LAnkle,
                    "RAnkle": RAnkle,
                    "Total_Score": Total_Score,
                }
                total_score = Total_Score
            else:
                comparison_results = {}

            item = {}
            if settings.ENVIRONMENT == "local":
                item["result"] = random.randint(70, 99)
                item["result_details"] = json.dumps(comparison_results)
            else:
                total_score = str(total_score).replace("-Infinity", "0")
                total_score = float(str(total_score).replace("-inf", "0"))

                item["result"] = total_score
                item["result_details"] = json.dumps(comparison_results)

            item["json_file"] = (
                "/usr/share/nginx/html/my-fight/player_videos/result/"
                + video_id
                + "/alphapose-results.json"
            )
            item["fighter_video_id"] = request.data["fighter_video"]
            item["player_id"] = request.data["player"]
            item["player_video_id"] = video_id
            _serializer = PlayerActionResultSerializer(data=item)
            # print(_serializer)
            if _serializer.is_valid():
                _serializer.save()

            comparison_results = item["result_details"]
            comparison_results = comparison_results.replace("-Infinity", "0")
            comparison_results = json.loads(comparison_results)

            data = serializer.data
            data["result"] = item["result"]
            data["comparison_results"] = comparison_results
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeletePlayerVideo(generics.RetrieveUpdateDestroyAPIView):
    def delete(self, request, *args, **kwargs):
        video = PlayerVideos.objects.filter(id=request.data["player_video_id"])
        # for video in videos:
        video.delete()

        video = FightStrategyVideo.objects.filter(
            player_video_id=request.data["player_video_id"]
        )
        if video:
            video.delete()

        video = PlayerActionsResult.objects.filter(
            player_video_id=request.data["player_video_id"]
        )
        if video:
            video.delete()

        return Response({"result": "Video deleted"}, status=status.HTTP_200_OK)


class GetPlayerVideos(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]
    serializer_class = PlayerVideosSerializer

    def get_queryset(self):
        return PlayerVideos.objects.filter(player_id=self.kwargs["player_id"]).order_by(
            "-id"
        )


# CompareActions
class CompareActions(generics.ListCreateAPIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request, format=None):
        serializer = CompareActionsSerializer(data=request.data)
        # print serializer.data

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FightStrategyView(generics.ListCreateAPIView):
    def post(self, request, format=None):
        # if "player" not in request.data:
        #     return Response(
        #         {"error": True, "message": "Player ID is required.", "status": 200},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if "title" not in request.data:
        #     return Response(
        #         {"error": True, "message": "Title is required.", "status": 200},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if "combinations" not in request.data:
        #     return Response(
        #         {"error": True, "message": "Combinations are required.", "status": 200},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        if "fight_strategy" not in request.data:
            return Response(
                {
                    "error": True,
                    "message": "Fight strategy is required.",
                    "status": 200,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        fight_strategy = request.data["fight_strategy"].replace("\\", "")
        fight_strategy = json.loads(fight_strategy)
        fight_strategy_id = fight_strategy["id"]
        is_update = False

        if fight_strategy_id == "0" or fight_strategy_id == 0:
            isStrategyExists = FightStrategy.objects.filter(
                player_id=fight_strategy["playerID"]
            )
            if isStrategyExists.exists() == True:
                isStrategyExists = isStrategyExists.first()
                fight_strategy_id = isStrategyExists.id

        if fight_strategy_id != "0" and fight_strategy_id != 0:
            isExists = FightStrategy.objects.filter(id=fight_strategy_id).exists()
            if isExists == False:
                return Response(
                    {
                        "error": True,
                        "message": "Fight strategy id is invalid.",
                        "status": 200,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            fight_strategy_to_update = FightStrategy.objects.filter(
                id=fight_strategy_id
            )
            # fight_strategy_to_delete.delete()

            fight_strategy_video_to_delete = FightStrategyVideo.objects.filter(
                fight_strategy_id=fight_strategy_id
            )
            fight_strategy_video_to_delete.delete()

        request_data = {}
        request_data["title"] = fight_strategy["title"]
        request_data["player"] = fight_strategy["playerID"]
        # print(fight_strategy)
        if fight_strategy_id != "0" and fight_strategy_id != 0:
            # request_data["id"] = fight_strategy_id
            fight_strategy_to_update.update(
                title=request_data["title"], player=request_data["player"]
            )
            is_update = True
        # else:

        serializer = FightStrategySerializer(data=request_data)
        # print serializer.data

        # combinations = fight_strategy["combinations"]
        combinations = fight_strategy["strategies"]
        if serializer.is_valid():
            serializer.save()
            if fight_strategy_id == "0" or fight_strategy_id == 0:
                fight_strategy_id = serializer.data["id"]

            # print(serializer.data)
            # combinations = json.loads(request.data["combinations"])
            for combination in combinations:
                # print(serializer.data)
                combinationIndex = combination["combinationIndex"]
                actionCards = combination["actionCards"]

                for actionCard in actionCards:
                    if actionCard is not None:
                        item = {}
                        item["player"] = fight_strategy["playerID"]
                        # item["combination"] = combination["combination"]
                        item["combination"] = combinationIndex
                        # item["player_video"] = combination["ActionCardID"]
                        # item["player_video_id"] = combination["ActionCardID"]
                        item["player_video_id"] = actionCard["id"]
                        item["fight_strategy"] = fight_strategy_id
                        _serializer = FightStrategyVideoSerializer(data=item)

                        if _serializer.is_valid():
                            _serializer.save()

                # print(_serializer.data)

            data = FightStrategyVideo.objects.filter(fight_strategy=fight_strategy_id)
            # print(data)

            items = []
            combinationIndex = "0"
            sameCombination = True
            actionCards = []
            i = 0
            for item in data:
                player_video_url = ""
                FileName = sub_type = Type = Belt = "N/A"
                comparison_results = ""
                result = 0
                fighter_video_id = 0
                fighter_id = 0
                created_at = item.created_at
                video_details = PlayerVideos.objects.filter(id=item.player_video_id)
                if len(video_details) > 0:
                    fighter_video_id = video_details[0].fighter_video_id
                    created_at = video_details[0].created_at
                    FileName = str(video_details[0].file_name)
                    file_rename = str(video_details[0].file_name).replace(
                        "player_videos/", ""
                    )
                    player_video_url = (
                        settings.BASE_URL
                        + settings.PLAYER_VIDEOS_URL
                        + "result/"
                        + str(video_details[0].id)
                        + "/"
                        + file_rename
                    )

                    result = PlayerActionsResult.objects.filter(
                        player_video_id=item.player_video_id
                    )
                    result_details = result[0].result_details
                    result_details = result_details.replace("-Infinity", "0")
                    result_details = result_details.replace("-inf", "0")
                    comparison_results = json.loads(result_details)

                    total_score = result[0].result.replace("-Infinity", "0")
                    result = float(total_score.replace("-inf", "0"))

                    fighter_video_details = FighterVideos.objects.filter(
                        id=fighter_video_id
                    )
                    if len(fighter_video_details) > 0:
                        fighter_id = fighter_video_details[0].id
                        Type = belt_type = fighter_video_details[0].belt
                        if belt_type == "Black-Belt-Final":
                            belt_type = "blackbelt"
                        elif belt_type == "Blue-Belt-Black-Stripe-Final":
                            belt_type = "bluebeltblackstripe"
                        elif belt_type == "Blue-Belt-Final":
                            belt_type = "bluebelt"
                        elif belt_type == "Brown-Belt-Black-Stripe-Final":
                            belt_type = "brownbeltblackstripe"
                        elif belt_type == "Brown-Belt-Final":
                            belt_type = "brownbelt"
                        elif belt_type == "Green-Belt-Black-Stripe-Final":
                            belt_type = "greenbeltblackstripe"
                        elif belt_type == "Green-Belt-Final":
                            belt_type = "greenbelt"
                        elif belt_type == "Yellow-Belt-Black-Stripe-Final":
                            belt_type = "yellowbeltblackstripe"
                        else:
                            belt_type = "yellowbelt"

                        Belt = belt_type
                        sub_type = fighter_video_details[0].sub_type

                if int(combinationIndex) != int(item.combination):
                    sameCombination = False
                else:
                    sameCombination = True

                if sameCombination == False:
                    video = {}
                    video["combinationIndex"] = combinationIndex
                    video["actionCards"] = actionCards
                    combinationIndex = item.combination
                    if len(actionCards) > 0:
                        items.append(video)
                    actionCards = []

                actionCard = {}
                actionCard["id"] = int(str(item.player_video_id))
                actionCard["Belt"] = Belt
                actionCard["Type"] = Type
                actionCard["sub_type"] = sub_type
                actionCard["FileName"] = FileName
                actionCard["fighter_id"] = fighter_id
                actionCard["created_at"] = created_at
                actionCard["fighter_video_id"] = fighter_video_id
                actionCard["player_id"] = item.player_id
                actionCard["comparison_results"] = comparison_results
                actionCard["result"] = result
                actionCard["Path"] = str(player_video_url)
                actionCard["Path"] = actionCard["Path"].replace("//p", "/p")
                # actionCard["Path"] = actionCard["player_video_url"]
                actionCard["status"] = item.status
                actionCards.append(actionCard)

                i = i + 1
                if len(data) == i:
                    video = {}
                    video["combinationIndex"] = combinationIndex
                    video["actionCards"] = actionCards
                    combinationIndex = item.combination
                    if len(actionCards) > 0:
                        items.append(video)
                    actionCards = []
            # for item in data:
            #     if item.player_video_id != "0" and item.player_video_id != 0:
            #         video_details = PlayerVideos.objects.filter(id=item.player_video_id)
            #         file_rename = str(video_details[0].file_name).replace(
            #             "player_videos/", ""
            #         )
            #         player_video_url = (
            #             settings.PLAYER_VIDEOS_URL
            #             + "result/"
            #             + str(video_details[0].id)
            #             + "/"
            #             + file_rename
            #         )

            #         video = {}
            #         # video["id"] = item.id
            #         # video["playerID"] = item.player_id
            #         video["combination"] = item.combination
            #         video["ActionCardID"] = str(item.player_video_id)
            #         video["player_video_url"] = (str(player_video_url),)
            #         video["player_video_url"] = video["player_video_url"][0]
            #         video["status"] = item.status
            #         # video["fight_strategy"] = str(item.fight_strategy)
            #         # video["created_by"] = item.created_by
            #         # video["created_at"] = item.created_at
            #         # video["updated_by"] = item.updated_by
            #         # video["updated_at"] = item.updated_at

            #         items.append(video)
            #     else:
            #         video = {}
            #         video["combination"] = item.combination
            #         video["ActionCardID"] = 0
            #         video["player_video_url"] = ""
            #         video["status"] = item.status
            #         items.append(video)

            data = serializer.data
            old_id = data["id"]
            data["id"] = fight_strategy_id
            data["playerID"] = request_data["player"]
            data["strategies"] = items

            if is_update == True:
                fight_strategy_to_delete = FightStrategy.objects.filter(id=old_id)
                fight_strategy_to_delete.delete()

            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListFightStrategy(viewsets.ReadOnlyModelViewSet):
    serializer_class = FightStrategySerializer

    def get_queryset(self):
        # return FightStrategy.objects.filter(player_id=self.kwargs["player_id"])
        # list = FightStrategy.objects.filter(player_id=3)

        list = FightStrategy.objects.filter(player_id=self.kwargs["player_id"])
        serializer_context = {"player_id": self.kwargs["player_id"]}
        self.serializer_class.context = serializer_context

        return list


class FightStrategyVideoView(generics.ListCreateAPIView):
    def post(self, request, format=None):
        serializer = FightStrategyVideoSerializer(data=request.data)
        # print serializer.data

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListFightStrategyVideos(viewsets.ReadOnlyModelViewSet):
    serializer_class = FightStrategyVideoSerializer

    def get_queryset(self):
        return FightStrategyVideo.objects.filter(
            fight_strategy_id=self.kwargs["fight_strategy_id"]
        )


class AddTribeAPI(generics.ListCreateAPIView):
    # parser_classes = (MultiPartParser, FormParser,)
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]

    def post(self, request, format=None):
        serializer = AddTribe(data=request.data)
        # print serializer.data

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListTribes(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]

    serializer_class = TribesList

    def get_queryset(self):
        return Tribes.objects.all()


# AddStudentAPI API
class JoinTribeAPI(generics.UpdateAPIView):
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]

    User = get_user_model()
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JoinTribe


class SendNotificationsAPI(generics.GenericAPIView):
    serializer = FCMSerializer

    def post(self, request):
        if "facebook_id" not in request.POST:
            return Response(
                {"error": True, "message": "Facebook ID is required.", "status": 200},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(facebook_id="7841597741211").first()
        print(user)
        # device = FCMDevice.objects.get(user=user)
        # print(device.registration_id)
        # device.send_message(notification=Notification(title='title', body='message'))

        message = Message(
            notification=Notification(
                title="Notification",
                body="Hello user",
            ),
        )

        try:
            devices = FCMDevice.objects.get(user=user)  # FCMDevice.objects.all()
            result = devices.send_message(message)
            print(result)
        except Exception as e:
            print("Push notification failed.", e)

        # print (result)
        return Response(
            {"error": True, "message": "Login failure.", "status": 200},
            status=status.HTTP_200_OK,
        )


class AddFriendAPI(generics.ListCreateAPIView):
    # parser_classes = (MultiPartParser, FormParser,)
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        if User.objects.filter(id=request.data["user"]).exists() == False:
            return Response(
                {"success": False, "errors": "Invalid user ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(id=request.data["friend"]).exists() == False:
            return Response(
                {"success": False, "errors": "Invalid friend ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Friends.objects.filter(
            user=request.data["user"], friend=request.data["friend"]
        ).exists():
            return Response(
                {"success": False, "errors": "Friend request already sent."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Friends.objects.filter(
            user=request.data["friend"], friend=request.data["user"]
        ).exists():
            return Response(
                {"success": False, "errors": "Friend request already received."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print(request.data)
        serializer = AddFriend(data=request.data)
        # print serializer.data

        if serializer.is_valid():
            serializer.save()

            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ListFriendsAPI(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = FriendsList

    def get_queryset(self):
        user = self.request.user
        friends = Friends.objects.filter(user=user)
        # print serializer.data
        return friends


class ListFriendRequestsAPI(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = ListFriendRequestsList

    def get_queryset(self):
        user = self.request.user
        friends = Friends.objects.filter(friend=user, status=0)
        # print serializer.data
        return friends


class AcceptFriendRequestAPI(generics.ListCreateAPIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        # serializer = AddFriend(data=request.data)
        try:
            friend_request = Friends.objects.get(id=request.data["friend_request_id"])
        except Friends.DoesNotExist:
            return Response(
                {"success": False, "message": "Friend request does not exist"}
            )

        # Check if the current user is the recipient of the friend request
        # if request.user != friend_request.friend:
        #     return Response(
        #         {"error": "You are not authorized to accept this friend request"}
        #     )

        # Create a new friendship object
        try:
            friendship = Friends.objects.create(
                friend=friend_request.user, user=friend_request.friend, status=1
            )

            friend_request.status = 1
            friend_request.save()
            # friend_request = Friends.objects.get(id=friendship.id)
            # Return a success message
            return Response(
                {
                    "success": True,
                    "message": "Friend request accepted",
                    "sender_id": friend_request.user_id,
                    "receiver_id": friend_request.friend_id,
                },
                status=status.HTTP_201_CREATED,
            )
        except:
            return Response(
                {"success": False, "message": "Already added as a friend"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SearchPlayerAPI(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = SearchPlayer

    def get_queryset(self):
        User = get_user_model()
        email = self.request.GET.get("email")
        if email is None or not email:
            player_id = self.request.GET.get("player_id")
            # print("player_id")
            # print(player_id)
            if player_id is None or not player_id:
                player_id = 0

            return User.objects.filter(id=player_id)
        else:
            return User.objects.filter(email=email)


class UpdateOnlineStatusAPI(generics.ListCreateAPIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        # serializer = AddFriend(data=request.data)
        try:
            if "user_id" in request.POST:
                friends_list = Friends.objects.filter(user=request.POST["user_id"])
                user = User.objects.filter(id=request.POST["user_id"])
            else:
                friends_list = Friends.objects.filter(user=request.user)
                user = User.objects.filter(id=request.user)

        except Friends.DoesNotExist:
            return Response(
                {"success": False, "message": "User does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a new friendship object
        try:
            update_data = {
                "is_online": request.data["is_online"],
            }

            friends_list.update(**update_data)
            user.update(**update_data)
            friend_id = ""
            for item in friends_list:
                friend_id = friend_id + "," + str(item.friend_id)
            friend_id = friend_id.strip(",")
            # Return a success message
            return Response(
                {"success": True, "message": "Success", "friends_id": friend_id},
                status=status.HTTP_201_CREATED,
            )
        except:
            return Response(
                {"success": False, "message": "Failed to update"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RemoveFriendAPI(generics.ListCreateAPIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        try:
            friend = Friends.objects.filter(
                user=request.POST["friend_id"], friend=request.user
            )
            # Delete the friend
            friend.delete()

            friend = Friends.objects.filter(
                friend=request.POST["friend_id"], user=request.user
            )
            # Delete the friend
            friend.delete()

            # Return a success message
            return Response({"success": "Success"})
        except:
            return Response({"error": "Failed to update"})


class TestAPI(generics.ListCreateAPIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request, format=None):
        item = {}
        item["json_field"] = {
            "Head": 10.25,
            "LShoulder": 10.25,
            "RShoulder": 10.25,
            "LElbow": 10.25,
            "RElbow": 10.25,
            "LWrist": 10.25,
            "RWrist": 10.25,
            "LHip": 10.25,
            "RHip": 10.25,
            "LKnee": 10.25,
            "RKnee": 10.25,
            "LAnkle": 10.25,
            "RAnkle": 10.25,
        }
        _serializer = TestSerializer(data=item)
        # print(_serializer)
        if _serializer.is_valid():
            _serializer.save()

        return Response(item, status=status.HTTP_201_CREATED)


# Register API
# class RegisterAPI(generics.GenericAPIView):
#     serializer_class = RegisterSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         # serializer.is_valid(raise_exception=True)

#         if serializer.is_valid():

#             email = request.POST['email']
#             if get_user_model().objects.filter(email=email).exists():
#                 # messages.error(request, "This username is already taken")
#                 return Response({
#                     "error": True,
#                     "message": "Email is already taken.",
#                     "errors": serializer.errors,
#                     "status": 200
#                 })

#             user = serializer.save()
#             # return Response({
#             #     "user": UserSerializer(user, context=self.get_serializer_context()).data,
#             #     "token": AuthToken.objects.create(user)[1]
#             # })
#             return Response({
#                 "error": False,
#                 "message": "Registration successful.",
#                 "status": 200,
#                 "data": {"user": LoginSerializer(user, context=self.get_serializer_context()).data},
#                 "access_token": AuthToken.objects.create(user)[1]
#             })

#         return Response({
#             "error": True,
#             "message": "Registration failure.",
#             "errors": serializer.errors,
#             "status": 200
#         })
