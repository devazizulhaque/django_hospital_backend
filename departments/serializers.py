from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        validators=[
            UniqueValidator(
                queryset=Department.objects.all(),
                message="This department name already exists."
            )
        ]
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
        help_text="Select a parent department (optional)."
    )

    parent_name = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Department
        fields = (
            'id', 'parent', 'parent_name', 'name', 'description', 'icon',
            'is_active', 'created_at', 'updated_at', 'children'
        )
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'is_active': {'required': True},
        }

    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None

    def get_children(self, obj):
        children = obj.get_children()
        return DepartmentSerializer(children, many=True, context=self.context).data

class DepartmentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = (
            'id', 'name', 'description', 'icon',
            'is_active', 'created_at', 'updated_at', 'children'
        )

    def get_children(self, obj):
        # Recursively fetch all children
        children = obj.get_children()
        return DepartmentTreeSerializer(children, many=True).data