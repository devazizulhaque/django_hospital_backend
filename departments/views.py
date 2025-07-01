from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Department
from .serializers import DepartmentSerializer, DepartmentTreeSerializer

# List all departments
class DepartmentListView(generics.ListAPIView):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

# List all departments with parent as null (top-level departments)
class ParentDepartmentListView(generics.ListAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Department.objects.filter(parent__isnull=True, is_active=True)

# Retrieve department tree structure
class DepartmentTreeView(generics.ListAPIView):
    serializer_class = DepartmentTreeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only top-level departments
        return Department.objects.filter(parent__isnull=True, is_active=True)

# List all child departments by parent id
class ChildDepartmentsByParentView(generics.ListAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        parent_id = self.kwargs['parent_id']
        return Department.objects.filter(parent_id=parent_id, is_active=True)

# List all child list departments without parent
class ChildDepartmentsListView(generics.ListAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Department.objects.filter(parent__isnull=False, is_active=True)

# Retrieve single department by id
class DepartmentDetailView(generics.RetrieveAPIView):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

# Create new department
class DepartmentCreateView(generics.CreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUser]  # শুধু অ্যাডমিন তৈরি করতে পারবে

# Update existing department
class DepartmentUpdateView(generics.UpdateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUser]

# Soft delete department by setting is_active=False
class DepartmentDeleteView(generics.DestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"detail": "Department deactivated successfully."}, status=status.HTTP_204_NO_CONTENT)
