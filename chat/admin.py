from django.contrib import admin
from .models import ChatSession, Message, ToolCall


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['session_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'created_at']
    list_filter = ['role', 'session', 'created_at']
    search_fields = ['content']
    readonly_fields = ['created_at']


@admin.register(ToolCall)
class ToolCallAdmin(admin.ModelAdmin):
    list_display = ['session', 'tool_name', 'created_at']
    list_filter = ['tool_name', 'session', 'created_at']
    search_fields = ['tool_name']
    readonly_fields = ['created_at']
