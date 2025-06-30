from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, ProfileView, UserView, UserDetailView, UserUpdateView,
    UserUpdateProfileView, UserDeleteView, UserDeleteSelfView,
    RoleViewSet, PermissionViewSet, AssignRoleToUserView, UserRolesView, AssignUserPermissionsView, RemoveUserPermissionsView
)

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'permissions', PermissionViewSet, basename='permissions')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('list/', UserView.as_view(), name='user_list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('update/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
    path('update/', UserUpdateProfileView.as_view(), name='user_update_self'),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('delete/', UserDeleteSelfView.as_view(), name='user_delete_self'),

    # ✅ Include role and permission routes
    path('assign-role/', AssignRoleToUserView.as_view(), name='assign_role'),
    path('user-roles/<int:user_id>/', UserRolesView.as_view(), name='user_roles'),
    path('assign-user-permissions/', AssignUserPermissionsView.as_view(), name='assign_user_permissions'),
    path('remove-user-permissions/', RemoveUserPermissionsView.as_view(), name='remove_user_permissions'),

    # ✅ Include all routes from the router (roles + permissions)
    path('', include(router.urls)),
]
