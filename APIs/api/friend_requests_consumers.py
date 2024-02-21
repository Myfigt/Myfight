# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.forms import ValidationError
from api.models import User
import requests
from django.core.exceptions import ValidationError
from myfight.settings import API_URL
from asgiref.sync import sync_to_async


class FriendRequestsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # these 2 values come from the routing URL param
        param_user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        # chat_room = "chat_room_" + str(first_id) + "_" + str(second_id)
        chat_room = "chat_room_" + str(param_user_id)

        self.room_name = chat_room  # self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = chat_room  # "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        await self.send(
            json.dumps(
                {"success": True, "message": "You are now connected to the WebSocket."}
            )
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            error_message = "Invalid JSON object received"
            await self.send(text_data=json.dumps({"error": error_message}))
            return

        # message = data.get("sender_message")
        action = data.get("action")
        token = data.get("token")
        payload_param = data.get("payload")
        # print()
        if isinstance(data.get("payload"), dict):
            payload = data.get("payload")
        else:
            payload = json.loads(data.get("payload"))
        # print(payload)

        try:
            if not token:
                await self.send(
                    json.dumps(
                        {"success": False, "sender_message": "Token is required"}
                    )
                )
                return

            if not payload:
                await self.send(
                    json.dumps(
                        {"success": False, "sender_message": "Payload data is missing"}
                    )
                )
                return

            if action == "add_friend":
                user_id = payload["user_id"]
                friend_id = payload["friend_id"]

                if not user_id:
                    await self.send(
                        json.dumps(
                            {"success": False, "sender_message": "User ID is required"}
                        )
                    )
                    return

                if not friend_id:
                    await self.send(
                        json.dumps(
                            {
                                "success": False,
                                "sender_message": "Friend ID is required",
                            }
                        )
                    )

                url = API_URL + "api/add_friend"
                # print(token)
                payload = {"user": user_id, "friend": friend_id}
                headers = {
                    "Accept": "application/json",
                    "Authorization": token,
                }
                # print(payload)
                response = requests.request(
                    "POST", url, headers=headers, data=payload, files=[], timeout=2
                )
                content = response.json()
                # print(content)
                status_code = response.status_code
                # print(content, status_code)
                userInfo = await self.get_user_by_id(user_id)
                if userInfo == None:
                    sender_name = ""
                else:
                    sender_name = userInfo.name
                # print(userInfo.name)
                if status_code == 401:
                    await self.send(
                        json.dumps(
                            {"success": False, "sender_message": content["detail"]}
                        )
                    )
                    return

                elif status_code == 400:
                    await self.send(
                        json.dumps(
                            {"success": False, "sender_message": content["errors"]}
                        )
                    )
                    return

                elif status_code == 201:
                    # Send message to room group
                    # if content["detail"] == True:
                    data = {}
                    data["payload"] = payload_param
                    data["sender"] = user_id
                    data["receiver_message"] = (
                        "You have received a friend request from " + sender_name
                    )
                    data["receiver"] = friend_id
                    data["friend_request_id"] = content["data"]["id"]
                    # print(data)
                    self.room_group_name = "chat_room_" + str(friend_id)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "send_response",
                            "action": action,
                            "data": data,
                        },
                    )

                    await self.send(
                        json.dumps(
                            {
                                "success": True,
                                "sender_message": "Request sent successfully.",
                            }
                        )
                    )
                else:
                    await self.send(
                        json.dumps(
                            {"success": False, "sender_message": "Invalid request"}
                        )
                    )
                    return
            elif action == "accept_friend_request":
                friend_request_id = payload["friend_request_id"]
                if not friend_request_id:
                    await self.send(
                        json.dumps(
                            {
                                "success": False,
                                "sender_message": "Friend Request ID is required",
                            }
                        )
                    )

                url = API_URL + "api/accept_friend_request"
                # print(token)
                payload = {"friend_request_id": friend_request_id}
                headers = {
                    "Accept": "application/json",
                    "Authorization": token,
                }

                response = requests.request(
                    "POST", url, headers=headers, data=payload, files=[], timeout=2
                )
                # print(response.text)
                content = response.json()
                status_code = response.status_code
                # print(content)
                if status_code == 401:
                    await self.send(
                        json.dumps(
                            {"success": False, "sender_message": content["detail"]}
                        )
                    )
                    return

                elif status_code == 201:
                    # Send message to room group
                    data = {}
                    data["receiver"] = content["sender_id"]
                    data["sender"] = content["receiver_id"]
                    data["receiver_message"] = "Your friend request has been accepted"
                    data["payload"] = payload_param

                    self.room_group_name = "chat_room_" + str(data["receiver"])
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "send_response",
                            "data": data,
                            "action": action,
                        },
                    )

                    await self.send(
                        json.dumps(
                            {
                                "success": True,
                                "sender_message": "Request accepted successfully.",
                            }
                        )
                    )

                else:
                    await self.send(
                        json.dumps(
                            {
                                "success": False,
                                "sender_message": content["message"],
                                # "errors": content["errors"],
                            }
                        )
                    )
                    return
            elif action == "make_user_online_offline":
                is_online = payload["is_online"]
                user_id = payload["user_id"]
                if not is_online:
                    await self.send(
                        json.dumps(
                            {
                                "success": False,
                                "sender_message": "Param (is_online) is required",
                            }
                        )
                    )
                    return

                url = API_URL + "api/" + action
                # print(token)
                payload = {"is_online": is_online, "user_id": user_id}
                headers = {
                    "Accept": "application/json",
                    "Authorization": token,
                }

                response = requests.request(
                    "POST", url, headers=headers, data=payload, files=[], timeout=2
                )
                content = response.json()
                status_code = response.status_code
                # print(content, status_code)
                # friends_id=content["friends_id"].split(",")
                if status_code == 401:
                    await self.send(
                        json.dumps(
                            {"success": False, "sender_messagess": content["detail"]}
                        )
                    )
                    return

                elif status_code == 201:
                    # Send message to room group
                    friends_id = content["friends_id"].split(",")
                    # print(friends_id)
                    for friend_id in friends_id:
                        self.room_group_name = "chat_room_" + str(friend_id)

                        data = {}
                        data["sender"] = user_id
                        data["receiver"] = friend_id
                        data["is_online"] = is_online
                        data["sender_message"] = "Request sent successfully"
                        data["receiver_message"] = "User is online"
                        data["payload"] = payload_param

                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "send_response",
                                "action": action,
                                "data": data,
                            },
                        )

                    await self.send(
                        json.dumps(
                            {
                                "success": True,
                                "sender_message": "Request sent successfully.",
                            }
                        )
                    )

                else:
                    await self.send(
                        json.dumps(
                            {
                                "success": False,
                                "sender_message": content["message"],
                                # "errors": content["errors"],
                            }
                        )
                    )
                    return
            elif action == "join_room":
                room_id = payload["room_id"]
                friend_id = payload["friend_id"]
                user_id = payload["user_id"]
                # data = payload["data"]

                if not room_id:
                    await self.send(
                        json.dumps(
                            {
                                "success": False,
                                "sender_message": "Param (room_id) is required",
                            }
                        )
                    )
                    return

                if not friend_id:
                    await self.send(
                        json.dumps(
                            {
                                "success": False,
                                "sender_message": "Param (friend_id) is required",
                            }
                        )
                    )
                    return

                if not data:
                    await self.send(
                        json.dumps(
                            {
                                "success": False,
                                "sender_message": "Param (data) is required",
                            }
                        )
                    )
                    return

                data = {}
                data["sender"] = user_id
                data["receiver"] = friend_id
                data["sender_message"] = "Request sent successfully"
                data["receiver_message"] = "User Data"
                data["payload"] = payload_param

                self.room_group_name = "chat_room_" + str(friend_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_response",
                        "action": action,
                        "data": data,
                    },
                )

                await self.send(
                    json.dumps(
                        {
                            "success": True,
                            "sender_message": "Request sent successfully.",
                        }
                    )
                )

            else:
                await self.send(
                    json.dumps(
                        {
                            "success": False,
                            "sender_message": "Invalid request, action type is missing",
                        }
                    )
                )

        except ValidationError as e:
            error_message = str(e)

    async def add_friend(self, event):
        # sender_message = event["sender_message"]
        action = event["action"]
        data = event["data"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    # "sender_message": sender_message,
                    "payload": data,
                    "action": action,
                }
            )
        )

    async def accept_friend_request(self, event):
        data = event["data"]
        action = event["action"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "payload": data,
                    "action": action,
                }
            )
        )

    async def make_user_online_offline(self, event):
        data = event["data"]
        action = event["action"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "payload": data,
                    "action": action,
                }
            )
        )

    async def join_room(self, event):
        data = event["data"]
        action = event["action"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "payload": data,
                    "action": action,
                }
            )
        )

    async def send_response(self, event):
        data = event["data"]
        action = event["action"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "payload": data,
                    "action": action,
                }
            )
        )

    def validate_token(token):
        # Retrieve the user from the token
        try:
            user = User.objects.get(auth_token=token)
            # You can perform additional checks or validations here
            return user
        except User.DoesNotExist:
            return None

    async def get_user_by_id(self, user_id):
        try:
            user = await sync_to_async(User.objects.get)(id=user_id)
            return user
        except User.DoesNotExist:
            return None
