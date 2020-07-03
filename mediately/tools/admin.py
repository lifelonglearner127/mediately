from django.contrib import admin

from mediately.tools.models import Tool


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    pass
