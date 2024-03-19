# users/urls.py
from django.urls import include, path
from rest_framework import routers
from .views import UserViewSet

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += router.urls