from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from rest_framework import routers
from .views import UserCreateView, LoginIndexView, LogOut, UserViewSet
from Notes.views import (NotesListDashboard, TermViewSet, CourseViewSet,
                         ClassNoteViewSet,)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'terms', TermViewSet, basename='term')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'classnotes', ClassNoteViewSet, basename='classnote')

urlpatterns = [
    path(
        'admin/',
         admin.site.urls,
         name = 'admin',
         ),
    path(
        'Dashboard/',
         login_required(NotesListDashboard.as_view()),
         name = 'dashboard',
        ),
    path(
        '',
        LoginIndexView.as_view(),
        name = 'loginindex',
        ),
    path(
        'Logout/',
         login_required(LogOut.as_view()),
         name = 'logout',
         ),
    path(
        'Register/',
        UserCreateView.as_view(),
        name = 'register',
        ),
    path(
        'Notes/',
         include('Notes.urls'),
        ),
    path(
        'Web-API/',
        include(router.urls),
        ),
    path(
        'API-auth/',
        include('rest_framework.urls'),
        name = 'rest_framework',
        ),
]
