from django.contrib import admin

from mediately.tools.models import Tool, Log


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    pass


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    pass
