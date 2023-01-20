from django.contrib.auth import get_user_model
from djoser.conf import settings as djo
from djoser.serializers import TokenSerializer, UserSerializer
from rest_framework import serializers

User = get_user_model()


class CurrentUserSerializer(UserSerializer):
    organization = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            djo.USER_ID_FIELD,
            djo.LOGIN_FIELD,
        ) + ('first_name', 'last_name', 'is_staff', 'organization')
        read_only_fields = (djo.LOGIN_FIELD,)


class CustomTokenSerializer(TokenSerializer):
    user = CurrentUserSerializer()

    class Meta:
        model = djo.TOKEN_MODEL
        fields = ("auth_token", "user")
