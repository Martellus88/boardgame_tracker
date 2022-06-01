from django.urls import path
from . import views

app_name = 'auth_user'

urlpatterns = [
    path('register/', views.SignUp.as_view(), name='register'),
]
