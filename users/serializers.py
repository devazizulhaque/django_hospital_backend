from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    profile_picture = serializers.ImageField(required=False)
    is_active = serializers.BooleanField(required=False, default=False)

    # ✅ Accept dd-mm-yyyy format for date of birth
    dob = serializers.DateField(input_formats=['%d-%m-%Y'], required=False)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password',
            'first_name', 'last_name',
            'dob', 'phone_number', 'address', 'profile_picture',
            'is_doctor', 'is_patient', 'is_staff', 'is_active',
            'date_joined', 'last_login'
        )
        extra_kwargs = {
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        is_active = validated_data.pop('is_active', False)
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = is_active
        user.save()
        return user
    
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name']

class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        group = Group.objects.create(**validated_data)
        group.permissions.set(permissions)
        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if permissions is not None:
            instance.permissions.set(permissions)

        return instance

User = get_user_model()

class UserPermissionAssignSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate(self, data):
        user_id = data.get('user_id')
        permission_ids = data.get('permission_ids')

        try:
            user = User.objects.get(id=user_id)
            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        permissions = Permission.objects.filter(id__in=permission_ids)
        if permissions.count() != len(permission_ids):
            raise serializers.ValidationError("Some permissions not found.")
        data['permissions'] = permissions

        return data
