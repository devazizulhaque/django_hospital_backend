# users/views.py

from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer, UserPermissionAssignSerializer
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

# ✅ Register view
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# ✅ Profile view (requires JWT token)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "profile_picture": request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None
        })

# ✅ User list view (requires JWT token)
class UserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
# ✅ User detail view (requires JWT token)
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
# ✅ User update view (requires JWT token)
class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
# ✅ User update self view (requires JWT token)
class UserUpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
# ✅ User delete view (requires JWT token)
class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({"message": "User deleted successfully"}, status=204)
    
# ✅ User delete self view (requires JWT token)
class UserDeleteSelfView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({"message": "User deleted successfully"}, status=204)
    
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]  # Only admin can manage roles

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]

User = get_user_model()

class AssignRoleToUserView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        group_id = request.data.get('group_id')

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            user.groups.add(group)
            return Response({"detail": "Role assigned successfully."})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)


class UserRolesView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
            roles = user.groups.values('id', 'name')
            return Response({"user": user.username, "roles": list(roles)})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
class AssignUserPermissionsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = UserPermissionAssignSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            permissions = serializer.validated_data['permissions']

            # Add permissions to the user (does not remove existing)
            for perm in permissions:
                user.user_permissions.add(perm)

            return Response({"detail": "Permissions assigned to user."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RemoveUserPermissionsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = UserPermissionAssignSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            permissions = serializer.validated_data['permissions']

            for perm in permissions:
                user.user_permissions.remove(perm)

            return Response({"detail": "Permissions removed from user."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)