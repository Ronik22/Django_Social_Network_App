from django.contrib import admin

from .models import Profile, Relationship


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "verified", "relationship_status_override", "relationship_status")


admin.site.register(Relationship)
