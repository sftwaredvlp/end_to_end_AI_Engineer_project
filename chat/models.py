"""
Chat models - Konuşma geçmişi vs
"""
from django.db import models
from django.utils import timezone


class ChatSession(models.Model):
    """Bir sohbet oturumu (konuşma)"""
    
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"ChatSession {self.session_id}"
    
    class Meta:
        ordering = ['-created_at']


class Message(models.Model):
    """Konuşma içindeki bir ileti"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('tool', 'Tool'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
    
    class Meta:
        ordering = ['created_at']


class ToolCall(models.Model):
    """Yapılan bir tool çağrısı"""
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='tool_calls')
    tool_name = models.CharField(max_length=100)
    tool_input = models.JSONField()
    tool_result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tool_name}() - {self.created_at}"
    
    class Meta:
        ordering = ['created_at']
