from django.contrib import admin

# Register your models here.

from .models import * 


admin.site.register(AppService)
admin.site.register(ChatSession)
admin.site.register(Message)
