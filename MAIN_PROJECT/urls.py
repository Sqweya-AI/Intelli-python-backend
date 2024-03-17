# # MAIN_PROJECT/urls.py
# from django.contrib import admin
# from django.urls import path
# from django.urls import include, path
# from rest_framework_simplejwt.views import TokenObtainPairView

# urlpatterns = [
#    path('admin/', admin.site.urls),
#    path('api/token/', TokenObtainPairView.as_view()),
#    path('users/', include('auth_app.urls')),
#    path('chat/', include('bot_app.urls')),
#    path('', include('main_app.urls')),
# ]

# INTELLI_PROJECT/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from auth_app import views

router = routers.DefaultRouter()
router.register(r'auth', views.UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)), 
    path('chat/', include('bot_app.urls')),
    path('main/', include('main_app.urls')), 
]