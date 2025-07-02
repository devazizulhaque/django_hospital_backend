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
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password',
            'first_name', 'last_name',
            'dob', 'phone_number', 'address', 'profile_picture',
            'is_doctor', 'is_patient', 'is_staff', 'is_active',
            'date_joined', 'last_login',
            'created_by', 'updated_by', 'created_at', 'updated_at',
            'groups',
        )
        extra_kwargs = {
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True},
            'created_by': {'read_only': True},
            'updated_by': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        groups = validated_data.pop('groups', [])
        request = self.context.get('request')

        user = User(**validated_data)
        user.set_password(password)
        user.is_active = validated_data.get('is_active', False)

        if request and request.user.is_authenticated:
            user.created_by = request.user
            user.updated_by = request.user

        user.save()
        if groups:
            user.groups.set(groups)

        return user

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.updated_by = request.user if request and request.user.is_authenticated else None

        groups = validated_data.pop('groups', None)

        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)

        instance.save()
        if groups is not None:
            instance.groups.set(groups)

        return instance
    
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name',]

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

    def save(self):
        user = self.validated_data['user']
        permissions = self.validated_data['permissions']
        user.user_permissions.set(permissions)
        return user