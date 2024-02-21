import json
import os
import random
from re import U
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from api.models import (
    FightStrategyVideo,
    Fighters,
    FighterVideos,
    PlayerVideos,
    PlayerActionsResult,
    FightStrategy,
    Test,
    Tribes,
    Friends,
)
from django.contrib.auth import get_user_model
from django.db import models

# from api.models import UserProfile
from django.db.models import fields
from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from fcm_django.models import FCMDevice
from django.conf import settings
from datetime import datetime

User = get_user_model()


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'  # To fetch For All Fields
        fields = ["name", "photo", "device", "device_id", "firebase_token"]

        extra_kwargs = {
            "password": {"write_only": True},
        }

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, obj):
        tribe_name = ""

        if obj.tribe_id != 0:
            tribe = Tribes.objects.filter(id=obj.tribe_id)
            if tribe is None:
                tribe_name = ""
            else:
                tribe_name = tribe[0].name

        return {
            "error": "false",
            "message": "Profile Details.",
            "status": 200,
            "data": {
                "user": {
                    "id": obj.id,
                    "name": obj.name,
                    "email": obj.email,
                    "belt_type": obj.belt_type,
                    "photo": settings.MEDIA_URL + str(obj.photo),
                    "facebook_id": obj.facebook_id,
                    "device": obj.device,
                    "device_id": obj.device_id,
                    "tribe_id": obj.tribe_id,
                    "tribe_name": tribe_name,
                    "firebase_token": obj.firebase_token,
                    "created_at": obj.created,
                }
            },
        }


class UserSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer(required=True)
    class Meta:
        model = User
        fields = "__all__"  # ('email', 'password','name','username')
        extra_kwargs = {
            "name": {"required": False},
            "gender": {"required": False},
            "username": {"required": False},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        facebook_id = 0
        full_name = "MyFight User"
        if "facebook_id" in validated_data:
            facebook_id = validated_data["facebook_id"]

        if "name" in validated_data:
            full_name = validated_data["name"]

        # create user
        user = User.objects.create(
            name=full_name,
            password=validated_data["password"],
            username=validated_data["email"],
            email=validated_data["email"],
            device=validated_data["device"],
            device_id=validated_data["device_id"],
            firebase_token=validated_data["firebase_token"],
            facebook_id=facebook_id,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def to_representation(self, obj):
        tribe_name = ""

        if obj.tribe_id != 0:
            tribe = Tribes.objects.filter(id=obj.tribe_id)
            if tribe is None:
                tribe_name = ""
            else:
                tribe_name = tribe[0].name

        return {
            "error": "false",
            "message": "Profile Details.",
            "status": 200,
            "data": {
                "user": {
                    "id": obj.id,
                    "name": obj.name,
                    "email": obj.email,
                    "belt_type": obj.belt_type,
                    "photo": settings.MEDIA_URL + str(obj.photo),
                    "facebook_id": obj.facebook_id,
                    "device": obj.device,
                    "device_id": obj.device_id,
                    "tribe_id": obj.tribe_id,
                    "tribe_name": tribe_name,
                    "firebase_token": obj.firebase_token,
                    "created_at": obj.created,
                }
            },
        }


class FighterUserSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer(required=True)
    class Meta:
        model = User
        fields = "__all__"  # ('email', 'password','name','username')
        extra_kwargs = {
            "name": {"required": False},
            "gender": {"required": False},
            "username": {"required": False},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        # create user
        user = User.objects.create(
            name=validated_data["name"],
            password=validated_data["password"],
            username=validated_data["email"],
            email=validated_data["email"],
            is_fighter=True,
            device="--",  # validated_data['device'],
            device_id="--",  # validated_data['device_id'],
            firebase_token="--",  # validated_data['firebase_token']
        )

        user.set_password(validated_data["password"])
        user.save()
        return user

    def to_representation(self, obj):
        return {
            "error": "false",
            "message": "Profile Details.",
            "status": 200,
            "data": {
                "user": {
                    "id": obj.id,
                    "name": obj.name,
                    "email": obj.email,
                    "photo": settings.MEDIA_URL + str(obj.photo),
                    "device": obj.device,
                    "device_id": obj.device_id,
                    "firebase_token": obj.firebase_token,
                    "created_at": obj.created,
                }
            },
        }


class FighterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id": obj.id,
            "Name": obj.name,
            "Status": obj.status,
            "Photo": settings.MEDIA_URL + str(obj.photo),
            "created_at": obj.created,
        }


class FighterVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FighterVideos
        fields = "__all__"

    def to_representation(self, obj):
        # data = User.objects.filter(id=obj.fighter_id)

        cam_2 = ""  # obj.file_name.replace('cam_1','cam_1')
        cam_3 = ""  # obj.file_name.replace('cam_1','cam_1')
        belt_path = settings.MASTER_VIDEOS_URL + str(obj.fighter_id) + "/" + obj.belt

        cam_1 = belt_path + "/Cam-1/results/AlphaPose_" + obj.cam_angle_1

        if obj.cam_angle_2 != "":
            cam_2 = belt_path + "/Cam-3/results/AlphaPose_" + obj.cam_angle_2

        if obj.cam_angle_3 != "":
            cam_3 = belt_path + "/Cam-3/results/AlphaPose_" + obj.cam_angle_3

        belt_type = obj.belt
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

        representation = {
            "id": obj.id,
            "Belt": obj.belt,
            "belt_type": belt_type,
            "Type": belt_type,
            "sub_type": obj.title,
            "FileName": obj.cam_angle_1,
            "Path": cam_1,
            "Cam-1": cam_1,
            "Cam-2": cam_2,
            "Cam-3": cam_3,
            # "photo": settings.PLAYER_VIDEOS_URL+data[0].full_name+".jpg",
            "created_at": obj.created_at,
            "player_id": 0,
            "fighter_video_id": 0,
        }
        return representation


class ActionCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FighterVideos
        fields = "__all__"

    def to_representation(self, obj):
        data = User.objects.filter(id=obj.fighter_id)

        cam_2 = ""  # obj.file_name.replace('cam_1','cam_1')
        cam_3 = ""  # obj.file_name.replace('cam_1','cam_1')
        belt_path = settings.PLAYER_VIDEOS_URL + data[0].name + "/" + obj.belt

        cam_1 = belt_path + "/Cam-1/results/AlphaPose_" + obj.cam_angle_1

        if obj.cam_angle_2 != "":
            cam_2 = belt_path + "/Cam-3/results/AlphaPose_" + obj.cam_angle_2

        if obj.cam_angle_3 != "":
            cam_3 = belt_path + "/Cam-3/results/AlphaPose_" + obj.cam_angle_3

        representation = {
            "id": obj.id,
            "Belt": obj.belt,
            "Type": obj.type,
            "title": obj.title,
            "Cam-1": cam_1,
            "Cam-2": cam_2,
            "Cam-3": cam_3,
            "created_at": obj.created_at,
        }
        return representation


class LoginSerializer(serializers.Serializer):
    # User = get_user_model()
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    username = serializers.CharField()
    password = serializers.CharField()

    def to_representation(self, obj):
        tribe_name = ""
        if obj.tribe_id != 0:
            tribe = Tribes.objects.filter(id=obj.tribe_id)

            if tribe is None:
                tribe_name = ""
            else:
                tribe_name = tribe[0].name

        return {
            "id": obj.id,
            "name": obj.name,
            "email": obj.email,
            "belt_type": obj.belt_type,
            "photo": settings.MEDIA_URL + str(obj.photo),
            "facebook_id": obj.facebook_id,
            "device": obj.device,
            "device_id": obj.device_id,
            "tribe_id": obj.tribe_id,
            "tribe_name": tribe_name,
            "firebase_token": obj.firebase_token,
            "created_at": obj.created,
        }

    def validate(self, data):
        user = authenticate(**data)
        # print(data)
        # print(user)
        # if user and user.is_active:
        #     return user
        #
        if user:
            return user

        raise serializers.ValidationError({"error": True})


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        # fields = '__all__'  # To fetch For All Fields
        fields = ("old_password", "password", "confirm_password")

        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return value

    def update(self, instance, validated_data):
        user = self.context["request"].user

        if user.pk != instance.pk:
            raise serializers.ValidationError(
                {"authorize": "You dont have permission for this user."}
            )

        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)

        instance.save()
        return instance

    def to_representation(self, obj):
        return {
            "error": "false",
            "message": "Password updated successfully.",
            "status": 200,
            "data": {
                "user": {
                    "id": obj.id,
                    "name": obj.name,
                    "email": obj.email,
                    "device": obj.device,
                    "device_id": obj.device_id,
                    "firebase_token": obj.firebase_token,
                    "created_at": obj.created,
                }
            },
        }


# file upload
class UploadPlayerVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerVideos
        fields = (
            "player",
            "id",
            "fighter_video",
            "title",
            "file_name",
            "status",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        )

    def to_representation(self, obj):
        fighter_video = FighterVideos.objects.filter(id=obj.fighter_video_id)
        master = Fighters.objects.filter(id=fighter_video[0].fighter_id)
        # obj = json.JSONEncoder(obj)
        file_extension = str(obj.file_name).split(".")[-1]
        master_name = master[0].full_name.replace(" ", "")
        belt = fighter_video[0].belt.replace(" ", "")
        action_card_id = str(obj.id)
        new_file_name = (
            action_card_id + "-" + master_name + "-" + belt + "." + file_extension
        )
        # print(new_file_name)
        import os

        os.rename(
            settings.MEDIA_ROOT + "/" + str(obj.file_name),
            settings.MEDIA_ROOT + "/" + new_file_name,
        )

        obj.file_name = new_file_name
        obj.save()

        if file_extension != "mp4":
            new_name = (
                str(obj.file_name)
                # + "__"
                # + str(datetime.now().strftime("%Y%m%d%H%M%S"))
                + ".mp4"
            )
            new_name = new_name.replace("." + file_extension, "")
            os.rename(
                settings.MEDIA_ROOT + "/" + str(obj.file_name),
                settings.MEDIA_ROOT + "/" + new_name,
            )

            obj.file_name = new_name
            obj.save()

        file_rename = str(obj.file_name).replace("player_videos/", "")
        video_url = (
            settings.PLAYER_VIDEOS_URL + "result/" + str(obj.id) + "/" + file_rename
        )
        representation = {
            "id": obj.id,
            "title": obj.title,
            "Belt": "N/A",
            "belt_type": "N/A",
            "Type": "Cam-1",
            "sub_type": obj.title,
            "FileName": str(obj.file_name),
            "Path": video_url,
            "Cam-1": video_url,
            "Cam-2": video_url,
            "Cam-3": video_url,
            "created_at": obj.created_at,
            "player_id": obj.player_id,
            "fighter_video_id": obj.fighter_video_id,
            "result": random.randint(70, 99),
        }
        return representation


class PlayerVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerVideos
        fields = "__all__"

    def to_representation(self, obj):
        # data = Fighters.objects.filter(id=obj.fighter_id)
        # obj = json.JSONEncoder(obj)
        player_video_url = settings.PLAYER_VIDEOS_URL + "result/"

        file_rename = str(obj.file_name).replace("player_videos/", "")
        video_url = player_video_url + str(obj.id) + "/" + file_rename

        result = PlayerActionsResult.objects.filter(player_video_id=obj.id)
        result_details = result[0].result_details
        result_details = result_details.replace("-Infinity", "0")
        result_details = result_details.replace("-inf", "0")

        total_score = result[0].result.replace("-Infinity", "0")
        total_score = total_score.replace("-inf", "0")

        representation = {
            "id": obj.id,
            "title": obj.title,
            "Belt": "N/A",
            "belt_type": "N/A",
            "Type": "Cam-1",
            "sub_type": obj.title,
            "FileName": str(obj.file_name),
            "Path": video_url,
            "Cam-1": video_url,
            "Cam-2": video_url,
            "Cam-3": video_url,
            # "file_name": obj.file_name,
            # "Path": settings.PLAYER_VIDEOS_URL+"Masters/"+data[0].full_name+"/"+obj.belt + "/" + obj.type+"/results/AlphaPose_"+obj.file_name,
            "created_at": obj.created_at,
            "player_id": obj.player_id,
            "fighter_video_id": obj.fighter_video_id,
            "result": float(total_score),
            "comparison_results": json.loads(result_details),
        }
        return representation


class CompareActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerActionsResult
        fields = (
            "player",
            "fighter_video",
            "player_video",
            "json_file",
            "status",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        )


class FightStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = FightStrategy
        fields = (
            "player",
            "title",
            "status",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        )

    def to_representation(self, obj):
        player_id = obj.player_id  # self.context.get("player_id")
        # data = PlayerVideos.objects.filter(id=obj.player_video)
        data = FightStrategyVideo.objects.filter(fight_strategy_id=obj.id)
        player_name = "MyFight User"
        player_details = User.objects.filter(id=player_id)
        player_name = player_details[0].name
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

            # video["id"] = item.id
            # video["combination"] = item.combination
            # # video["player"] = item.player_id
            # # video["player_name"] = player_name
            # video["combination"] = item.combination
            # video["ActionCardID"] = str(item.player_video_id)
            # video["player_video_url"] = (str(player_video_url),)
            # video["player_video_url"] = video["player_video_url"][0].replace(
            #     "//p", "/p"
            # )
            # video["status"] = item.status
            # # video["fight_strategy"] = str(item.fight_strategy)
            # # video["created_by"] = item.created_by
            # # video["created_at"] = item.created_at
            # # video["updated_by"] = item.updated_by
            # # video["updated_at"] = item.updated_at

        representation = {
            "id": obj.id,
            "player_name": player_name,
            "playerID": obj.player_id,
            "title": obj.title,
            "created_at": obj.created_at,
            "strategies": items,
        }

        return representation


class FightStrategyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FightStrategyVideo
        fields = (
            "player",
            # "player_video",
            "player_video_id",
            "combination",
            "fight_strategy",
            "status",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        )
        # fields = '__all__'

        def to_representation(self, obj):
            if obj.player_video_id == "0" or obj.player_video_id == 0:
                representation = {
                    "id": obj.id,
                    # "player_video": 0,
                    "player_video_id": 0,
                    "player": obj.player,
                    "fight_strategy": obj.fight_strategy,
                    "combination": obj.combination,
                    "created_at": obj.created_at,
                }
                return representation
            else:
                data = PlayerVideos.objects.filter(id=obj.player_video_id)

                representation = {
                    "id": obj.id,
                    # "player_video": settings.PLAYER_VIDEOS_URL + data[0].file_name,
                    "player_video_id": settings.PLAYER_VIDEOS_URL + data[0].file_name,
                    "player": obj.player,
                    "fight_strategy": obj.fight_strategy,
                    "combination": obj.combination,
                    "created_at": obj.created_at,
                }
                return representation


class PlayerActionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerActionsResult
        fields = (
            "result",
            "json_file",
            "result_details",
            "fighter_video_id",
            "player_id",
            "player_video_id",
            "status",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        )
        # fields = '__all__'

        def to_representation(self, obj):
            representation = {"id": obj.id, "created_at": obj.created_at}
            return representation


class AddTribe(serializers.ModelSerializer):
    class Meta:
        model = Tribes
        fields = "__all__"


class TribesList(serializers.ModelSerializer):
    class Meta:
        model = Tribes
        fields = "__all__"

    def to_representation(self, obj):
        representation = {
            "id": obj.id,
            "name": obj.name,
            # "user_id": str(obj.user_id),
            "created_at": obj.created_at,
        }
        return representation


class JoinTribe(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["tribe_id"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, obj):
        return {
            "error": "false",
            "message": "Profile Details.",
            "status": 200,
            "data": {
                "user": {
                    "id": obj.id,
                    "name": obj.name,
                    "belt_type": obj.belt_type,
                    "email": obj.email,
                    "device": obj.device,
                    "device_id": obj.device_id,
                    "tribe_id": obj.tribe_id,
                    "firebase_token": obj.firebase_token,
                    "created_at": obj.created,
                }
            },
        }


class FCMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = "__all__"


class AddFriend(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = "__all__"


class FriendsList(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = "__all__"

    def to_representation(self, obj):
        data = User.objects.filter(email=obj.friend)
        if data:
            if hasattr(data[0], "is_online"):
                is_online = data[0].is_online
            else:
                is_online = 0

            name = (data[0].name,)
            email = (data[0].email,)
            player_id = data[0].id

        else:
            name = [""]
            email = [""]
            player_id = [""]
            is_online = 0

        representation = {
            "Friends_request_id": obj.id,
            "created_at": obj.created_at,
            "Friends_name": name[0],
            "Friends_email": email[0],
            "Friends_is_online": is_online,
            "Friend_id": player_id,
        }

        return representation


class ListFriendRequestsList(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = "__all__"

    def to_representation(self, obj):
        data = User.objects.filter(email=obj.user)
        if data:
            if hasattr(data[0], "is_online"):
                is_online = data[0].is_online
            else:
                is_online = 0

            name = (data[0].name,)
            email = (data[0].email,)
            player_id = data[0].id

        else:
            name = [""]
            email = [""]
            player_id = [""]
            is_online = 0

        representation = {
            "Friends_request_id": obj.id,
            "created_at": obj.created_at,
            "Friends_name": name[0],
            "Friends_email": email[0],
            "Friends_is_online": is_online,
            "Friend_id": player_id,
        }

        return representation


class SearchPlayer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def to_representation(self, obj):
        loggedin_user = self.context["request"].user.id
        # print(loggedin_user)
        # seach for friends request where logged in user has sent it
        data = Friends.objects.filter(friend=obj.id, user=loggedin_user)
        details = ""
        if data:
            if data[0].status == 1:
                is_friend = 1
            else:
                is_friend = 2

            details = "loggedin-user-to-player"
        else:
            # seach for friends request where a player has sent request to logged in user
            data = Friends.objects.filter(user=obj.id, friend=loggedin_user)
            if data:
                if data[0].status == 1:
                    is_friend = 1
                else:
                    is_friend = 2
                details = "player-to-loggedin-user"
            else:
                is_friend = 0

        return {
            "id": obj.id,
            "Email": obj.email,
            "Name": obj.name,
            "Status": obj.status,
            "Photo": settings.MEDIA_URL + str(obj.photo),
            "is_friend": is_friend,
            "details": details,
            "created_at": obj.created,
        }


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = "json_field"
        fields = "__all__"

        def to_representation(self, obj):
            representation = {"json_field": obj.json_field}
            return representation
