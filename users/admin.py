from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from users.forms import UserRegisterForm
from users.models import Profile, Relationship


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "verified", "relationship_status_override", "relationship_status")


class CustomUserAdmin(UserAdmin):
    add_form = UserRegisterForm


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Relationship)
