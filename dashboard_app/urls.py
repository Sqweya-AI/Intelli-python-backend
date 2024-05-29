# dashboard_app/urls.py

from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'', views.DashboardModelViewSet, basename='dashboard')
router.register(r'channels', views.ChannelViewSet, basename='channels')
router.register(r'agents', views.AgentViewSet, basename='agents')
router.register(r'user-settings', views.UserSettingsViewSet, basename='user-settings')
router.register(r'company-settings', views.HotelSettingsViewSet, basename='company-settings')

# Create a nested router for reservations
reservations_router = routers.NestedDefaultRouter(router, r'', lookup='dashboard')
reservations_router.register(r'reservations', views.DashboardModelViewSet, basename='dashboard-reservations')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(reservations_router.urls)),
]
