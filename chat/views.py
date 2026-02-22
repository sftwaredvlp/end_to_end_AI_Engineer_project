"""
Chat views - API endpoints ve web interface
"""
import json
import logging
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .agent import create_agent
from .models import ChatSession, Message, ToolCall

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def chat_endpoint(request):
    """
    Chat API Endpoint
    
    POST ayarı:
    {
        "message": "Kullanıcı mesajı",
        "session_id": "opsiyonel session id"
    }
    
    Dönüş:
    {
        "success": bool,
        "response": str,
        "session_id": str,
        "turns": int,
        "tool_calls": List
    }
    """
    try:
        # 1. İstek analiz et
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        # 2. Message boş mu kontrol et
        if not user_message:
            logger.warning("Empty message received")
            return JsonResponse({
                'success': False,
                'error': 'Mesaj boş olamaz',
                'response': None
            }, status=400)
        
        # 3. Session kontrol et
        if not session_id:
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(session_id=session_id)
            logger.info(f"New session created: {session_id}")
        else:
            try:
                session = ChatSession.objects.get(session_id=session_id)
            except ChatSession.DoesNotExist:
                logger.warning(f"Session not found: {session_id}")
                session = ChatSession.objects.create(session_id=session_id)
        
        # 4. Agent oluştur
        agent = create_agent()
        
        # 5. Chat çalıştır
        logger.info(f"Processing message in session {session_id}: {user_message[:50]}...")
        result = agent.chat(user_message)
        
        # 6. Message'ları kaydet
        Message.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        Message.objects.create(
            session=session,
            role='assistant',
            content=result.get('response', '')
        )
        
        # 7. Tool calls'ı kaydet
        for tool_call in result.get('tool_calls', []):
            ToolCall.objects.create(
                session=session,
                tool_name=tool_call.get('name'),
                tool_input=tool_call.get('input'),
                tool_result=tool_call.get('result')
            )
        
        # 8. Döndür
        logger.info(f"Chat completed in {result.get('turns')} turns")
        
        return JsonResponse({
            'success': True,
            'response': result.get('response'),
            'session_id': session_id,
            'turns': result.get('turns'),
            'tool_calls': result.get('tool_calls'),
            'error': None
        })
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request")
        return JsonResponse({
            'success': False,
            'error': 'Geçersiz JSON',
            'response': None
        }, status=400)
    
    except Exception as e:
        logger.exception(f"Chat error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'response': None
        }, status=500)


def home_view(request):
    """
    Ana sayfa - Chat arayüzü
    """
    return render(request, 'chat/index.html')

