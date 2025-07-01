from django.urls import path
from .views import (
    DepartmentListView, ParentDepartmentListView, DepartmentTreeView,
    ChildDepartmentsByParentView, ChildDepartmentsListView,DepartmentDetailView,
    DepartmentCreateView, DepartmentUpdateView, DepartmentDeleteView
)

urlpatterns = [
    path('', DepartmentListView.as_view(), name='department-list'),
    path('parents/', ParentDepartmentListView.as_view(), name='parent-departments'),
    path('tree/', DepartmentTreeView.as_view(), name='department-tree'),
    path('children/', ChildDepartmentsListView.as_view(), name='department-children-list'),
    path('children/<int:parent_id>/', ChildDepartmentsByParentView.as_view(), name='department-children'),
    path('<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    path('create/', DepartmentCreateView.as_view(), name='department-create'),
    path('update/<int:pk>/', DepartmentUpdateView.as_view(), name='department-update'),
    path('delete/<int:pk>/', DepartmentDeleteView.as_view(), name='department-delete'),
]
