from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from rest_framework import viewsets
from .serializers import UserSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for displaying active user data as JSON.
    """
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        Retrieves active user.
        """
        username = self.request.user.username
        user = get_user_model().objects.filter(username=username)
        return user

class UserCreateView(CreateView):
    """
    Displays a form for user registration.
    """
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('loginindex')

    def form_valid(self, form):
        """
        Creates user given the data provided to the user creation form.
        """
        user_form = UserCreationForm(self.request.POST)
        user = user_form.save()
        return HttpResponseRedirect(self.success_url)

class LoginIndexView(LoginView):
    """
    Simple view for user login.
    """
    template_name = 'index.html'

    def get_success_url(self):
        """
        Directs user to the dashboard upon successful login.
        """
        url = reverse_lazy('dashboard')
        return resolve_url(url)

class LogOut(LogoutView):
    """
    Simple view for logging out.
    """

    def get_next_page(self):
        """
        Directs user back to the login page upon successful logout.
        """
        next_page = reverse_lazy('loginindex')
        return resolve_url(next_page)
