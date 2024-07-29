# INTELLI_PROJECT/urls.py
from django.contrib import admin
from django.urls import path, include
from bot_app.views import webhook, get_chat_histories
from waitlist.views import waitlist_create

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard_app.urls')),
    path('auth/', include('auth_app.urls')),
    path('chat/', include('bot_app.urls')),
    path('', include('main_app.urls')), 
    path('webhook/', webhook, name="verify webhook"),
    path('appservice/', include('appservice.urls')),
    # path('notification/', include('notifications.urls')),
    path('intelli_waitlist/', waitlist_create),

]