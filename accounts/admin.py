from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from accounts.models import Organization

User = get_user_model()

UserAdmin.fieldsets[1][1]['fields'] += ('organization',)


class UserAdminExtended(UserAdmin):
    list_display = UserAdmin.list_display + ('organization',)
    list_filter = UserAdmin.list_filter + ('organization',)


admin.site.register(User, UserAdminExtended)
admin.site.register(Organization)
