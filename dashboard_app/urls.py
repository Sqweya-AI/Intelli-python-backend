# dashboard_app/urls.py

from django.urls import include, path
from rest_framework import routers
from .views import  DashboardModelViewSet
# from .views import AgentViewSet, AgentRoleViewSet, ChannelViewSet, DashboardModelViewSet

router = routers.DefaultRouter()
router.register(r'', DashboardModelViewSet)

# router.register(r'agents', AgentViewSet)
# router.register(r'agent-roles', AgentRoleViewSet)
# router.register(r'channels', ChannelViewSet)


urlpatterns = [
    path('', include(router.urls)),
]

