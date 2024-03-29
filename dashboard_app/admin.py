from django.contrib import admin
from .models import HotelSettingsModel, AgentModel, AgentRoleModel, ReservationModel, ContactChannelModel, DashboardModel

admin.site.register(HotelSettingsModel)
admin.site.register(AgentModel)
admin.site.register(AgentRoleModel)
admin.site.register(ReservationModel)
admin.site.register(ContactChannelModel)
admin.site.register(DashboardModel)
