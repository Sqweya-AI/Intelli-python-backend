# dashboard_app/urls.py
from django.urls import include, path
from rest_framework import routers
from .views import  *


router = routers.DefaultRouter()
router.register(r'', DashboardModelViewSet)
router.register(r'agents', AgentViewSet)
router.register(r'channels', ChannelViewSet)
router.register(r'user-settings', UserSettingsViewSet)
router.register(r'company-settings', HotelSettingsViewSet)



urlpatterns = [
    path('', include(router.urls)),
]