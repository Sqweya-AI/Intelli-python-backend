# users/urls.py

from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'auth', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += router.urls