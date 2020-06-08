from django.views.generic import RedirectView
from .views import (
	DashboardView,
	CallView,
	WelcomeView,
)
from django.urls import path

urlpatterns = [
	path('welcome/', WelcomeView.as_view(), name='welcome'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('new_call/', CallView.as_view(), name='new_call'),
]