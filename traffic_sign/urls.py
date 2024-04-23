"""traffic_sign URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('predictPic/', views.predictPic.as_view(), name="predict"),
    path('predictVideo/', views.predictVideo.as_view(), name="predictVideo"),
    path('login/', views.login,name="login"),
    path('logout/',views.logout,name='logout'),
    path('register/',views.register.as_view(),name='logout'),
    path('',views.index,name='index'),
    path('favicon.ico/', RedirectView.as_view(url='/static/favicon.ico')),
    path('me/', views.me.as_view(), name='me'),
    path('update/', views.update.as_view(), name='update'),
    path('detection/', views.detection.as_view(), name='detection'),
    path('detectionResault/', views.detectionResault.as_view(), name="detectionResault")
]
