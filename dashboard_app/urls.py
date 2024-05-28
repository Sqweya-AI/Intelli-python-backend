# # dashboard_app/urls.py
# from django.urls import include, path
# from rest_framework import routers
# from .views import *

# router = routers.DefaultRouter()
# router.register(r'dashboard', DashboardModelViewSet)
# router.register(r'agents', AgentViewSet)
# router.register(r'channels', ChannelViewSet)
# router.register(r'user-settings', UserSettingsViewSet)
# router.register(r'company-settings', HotelSettingsViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
#     path('employees/', CreateEmployeeView.as_view(), name='create_employee'),
# ]

from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'', views.DashboardModelViewSet, basename='dashboard')
router.register(r'channels', views.ChannelViewSet, basename='channels')
router.register(r'agents', views.AgentViewSet, basename='agents')
router.register(r'user-settings', views.UserSettingsViewSet, basename='user-settings')
router.register(r'hotel-settings', views.HotelSettingsViewSet, basename='hotel-settings')

urlpatterns = [
    path('', include(router.urls)),
    path('create-employee/', views.CreateEmployeeView.as_view(), name='create-employee'),
]