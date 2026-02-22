"""
URL configuration for aiagent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from chat.views import chat_endpoint, home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', chat_endpoint, name='chat_endpoint'),
    path('', home_view, name='home'),
]
