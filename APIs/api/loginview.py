from django.contrib.auth import login

# from rest_framework import permissions
# from rest_framework.authtoken.serializers import AuthTokenSerializer
# from knox.views import LoginView as KnoxLoginView

from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from fcm_django.models import FCMDevice
from knox.models import AuthToken
from .serializers import LoginSerializer
from knox.views import LogoutView


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        # print(serializer.validated_data)
        # serializer.is_valid(raise_exception=True)

        if "username" not in request.data:
            return Response(
                {
                    "error": True,
                    "message": "Username is required.",
                    "errors": {},
                    "data": {},
                    "status": 400,
                }
            )

        if request.POST["username"] == "":
            return Response(
                {
                    "error": True,
                    "message": "Username is required.",
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

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data

            if "facebook_id" in request.data:
                facebook_id = request.POST["facebook_id"]
                user.facebook_id = facebook_id
                user.save()

            if "firebase_token" in request.data:
                user.firebase_token = request.POST["firebase_token"]
                user.save()

            if "device" in request.data:
                user.device = request.POST["device"]
                user.save()

            if "device_id" in request.data:
                user.device_id = request.POST["device_id"]
                user.save()

            try:
                device = FCMDevice.objects.filter(user=user).first()
            except FCMDevice.DoesNotExist:
                device = None

            # print("device")
            # print(device)
            if device is None:
                registration_id = request.data["firebase_token"]
                existing_device = FCMDevice.objects.filter(
                    registration_id=registration_id
                ).exists()

                if existing_device == False:
                    device = FCMDevice()
                    device.registration_id = registration_id
                    device.type = request.POST["device"]
                    device.name = "N/A"
                    device.device_id = request.POST["device_id"]

                    if "facebook_id" in request.data:
                        device.facebook_id = request.POST["facebook_id"]

                    device.user = user
                    device.save()
            else:
                registration_id = request.data["firebase_token"]
                existing_device = FCMDevice.objects.filter(
                    registration_id=registration_id
                ).exists()

                if existing_device == False:
                    device.registration_id = registration_id
                    device.type = request.POST["device"]
                    device.device_id = request.POST["device_id"]

                    if "facebook_id" in request.data:
                        device.facebook_id = request.POST["facebook_id"]

                    device.save()

            return Response(
                {
                    "error": False,
                    "message": "Logged In Successfully.",
                    "status": 200,
                    "errors": {},
                    "data": {
                        "user": LoginSerializer(
                            user, context=self.get_serializer_context()
                        ).data
                    },
                    "access_token": AuthToken.objects.create(user)[1],
                }
            )

        return Response(
            {
                "error": True,
                "message": "Email or Password is incorrect.",
                "errors": {},  # serializer.errors,
                "data": {},
                "status": 400,
            }
        )


class LogoutAPI(LogoutView):
    def post(self, request, format=None):
        # Get the response from the parent class
        response = super(LogoutAPI, self).post(request, format=None)

        # Check if the token was expired
        if response.status_code == 401:
            return Response({"detail": "Token expired."}, status=401)

        # Return the original response if the token was not expired
        # return response
        return Response({"detail": "Logout Successfully."}, status=200)


# class LoginAPI(KnoxLoginView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request, format=None):
#         serializer = AuthTokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         login(request, user)
#         return super(LoginAPI, self).post(request, format=None)
