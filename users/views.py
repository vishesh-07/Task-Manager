from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    HTTP_401_UNAUTHORIZED,
)
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from rest_framework.throttling import UserRateThrottle

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
)


# Route - /auth/
class UserAuthViewSet(GenericViewSet):
    queryset = User.objects.all()
    registration_serializer = RegisterSerializer
    login_serializer = LoginSerializer
    user_profile_serializer = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @action(
        methods=["post"],
        detail=False,
        url_path="register",
        permission_classes=[AllowAny],
    )
    def register(self, request):
        try:
            serializer = self.registration_serializer(data=request.data)

            if not serializer.is_valid():
                return Response(
                    {"message": "Validation failed", "errors": serializer.errors},
                    status=HTTP_400_BAD_REQUEST
                )
            
            validated_data = serializer.validated_data
            name = validated_data.get("name")
            email = validated_data.get("email")
            password = validated_data.get("password")

            if User.objects.filter(email=email).exists():
                return Response(
                    {"message": "User already exists"}, status=HTTP_409_CONFLICT
                )

            user = User.objects.create_user(email=email, name=name, password=password)

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "User created successfully",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "data": self.registration_serializer(user).data,
                },
                status=HTTP_200_OK,
            )

        except Exception as error:
            return Response(
                {"message": "error", "error": str(error)}, status=HTTP_400_BAD_REQUEST
            )

    @action(methods=["post"], detail=False, url_path="login")
    def login(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password").strip()

            if not email or not password:
                return Response(
                    {"message": "Email and password are required"},
                    status=HTTP_400_BAD_REQUEST,
                )

            user = User.objects.filter(email=email).first()
            if not user:
                return Response(
                    {"message": "User not found"}, status=HTTP_400_BAD_REQUEST
                )

            authenticated_user = authenticate(email=email, password=password)
            if authenticated_user is None:
                return Response(
                    {"message": "Invalid credentials"}, status=HTTP_401_UNAUTHORIZED
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Login successful",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                },
                status=HTTP_200_OK,
            )
        except Exception as error:
            return Response(
                {"message": "Unable to Login", "error": str(error)},
                status=HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=False, url_path="logout")
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"message": "Refresh token is required"},
                    status=HTTP_400_BAD_REQUEST,
                )

            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"message": "Logout successful"}, status=HTTP_200_OK)
            except Exception:
                return Response(
                    {"message": "Invalid token or already logged out"},
                    status=HTTP_400_BAD_REQUEST,
                )

        except Exception as error:
            return Response(
                {"message": "Unable to Logout", "error": str(error)},
                status=HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["post"],
        detail=False,
        url_path="refresh-token",
        permission_classes=[AllowAny],
    )
    def refresh_token(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"message": "Refresh token required"}, status=HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            return Response(
                {
                    "access_token": str(token.access_token),
                },
                status=HTTP_200_OK,
            )
        except Exception as error:
            return Response(
                {"message": "Invalid or expired refresh token", "error": str(error)},
                status=HTTP_400_BAD_REQUEST,
            )


# Route - /detail/
class UserDetailViewSet(GenericViewSet):
    queryset = User.objects.all()
    user_profile_serializer = UserProfileSerializer
    user_profile_update_serializer = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=["get"], detail=False, url_path="profile")
    def profile(self, request):
        try:
            serializer = self.user_profile_serializer(request.user)
            return Response(
                {"message": "Profile retrieved", "data": serializer.data},
                status=HTTP_200_OK,
            )
        except Exception as error:
            return Response(
                {"message": "Unable to retrieve profile", "error": str(error)},
                status=HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["put"],
        detail=False,
        url_path="update-profile"
    )
    def update_profile(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            if "password" in serializer.validated_data:
                serializer.validated_data["password"] = make_password(
                    serializer.validated_data["password"]
                )
            serializer.save()
            return Response(
                {"message": "Profile updated", "data": serializer.data},
                status=HTTP_200_OK,
            )
        return Response(
            {"message": "Invalid data", "errors": serializer.errors},
            status=HTTP_400_BAD_REQUEST,
        )
