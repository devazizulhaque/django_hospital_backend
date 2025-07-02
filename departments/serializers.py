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

    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Department
        fields = (
            'id', 'parent', 'parent_name', 'name', 'description', 'icon', 'children',
            'is_active', 'created_by', 'updated_by', 'created_at', 'updated_at'
        )
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'is_active': {'required': True},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        department = Department(**validated_data)
        if request and request.user.is_authenticated:
            department.created_by = request.user
            department.updated_by = request.user
        department.save()
        return department

    def update(self, instance, validated_data):
        request = self.context.get('request')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if request and request.user.is_authenticated:
            instance.updated_by = request.user
        instance.save()
        return instance

    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None

    def get_children(self, obj):
        children = obj.get_children()
        # Avoid circular recursion
        if hasattr(self, 'depth') and self.depth <= 0:
            return []
        return DepartmentSerializer(children, many=True, context=self.context).data


class DepartmentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Department
        fields = (
            'id', 'name', 'description', 'icon', 'children',
            'is_active', 'created_by', 'updated_by', 'created_at', 'updated_at'
        )

    def get_children(self, obj):
        request = self.context.get('request')
        max_depth = int(request.query_params.get('depth', 3)) if request else 3
        return self.build_tree(obj, max_depth)

    def build_tree(self, obj, depth):
        if depth <= 0:
            return []
        children = obj.get_children()
        serializer = DepartmentTreeSerializer(children, many=True, context=self.context)
        return serializer.data
