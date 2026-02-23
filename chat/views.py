import json
import logging
import uuid
from zoneinfo import ZoneInfo

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from chat.services.agent import run_agent

logger = logging.getLogger(__name__)

ORLANDO_TZ = ZoneInfo("America/New_York")


def get_orlando_time():
    """Şu an Orlando (America/New_York) saat diliminde tarih ve saat."""
    now = timezone.now()
    orlando_now = now.astimezone(ORLANDO_TZ)
    return {
        "display": orlando_now.strftime("%b %d, %Y %I:%M %p"),  # örn: Feb 23, 2026 12:01 AM
        "iso": orlando_now.isoformat(),
    }


def home(request):
    """Ana sayfa — chat arayuzu buraya gelecek (Faz 4)."""
    return render(request, "chat/home.html")


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """
    POST ile JSON alır: {"message": "kullanıcı mesajı"}
    Agent'ı çalıştırır, sonucu JSON döner: {"response": "..."}
    """
    logger.info("Chat API isteği alındı")
    import sys; print("[CHAT] API isteği alındı", file=sys.stderr, flush=True)
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError as e:
        logger.warning("Geçersiz JSON: %s", e)
        return JsonResponse(
            {"error": "Geçersiz JSON."},
            status=400,
        )
    message = body.get("message") or body.get("msg", "").strip()
    if not message:
        return JsonResponse(
            {"error": "Mesaj boş olamaz."},
            status=400,
        )
    history = body.get("history") or []
    if not isinstance(history, list):
        history = []
    history = [
        {"role": str(h.get("role", "")), "content": str(h.get("content", ""))}
        for h in history
        if h.get("role") in ("user", "assistant") and str(h.get("content", "")).strip()
    ]
    try:
        request_id = str(uuid.uuid4())
        response_text, steps = run_agent(message, conversation_history=history)
        logger.info("Agent cevabı üretildi")
        import sys; print("[CHAT] Agent cevabı üretildi", file=sys.stderr, flush=True)
        orlando = get_orlando_time()
        return JsonResponse({
            "response": response_text,
            "steps": steps,
            "test": "pratik",
            "timestamp": timezone.now().isoformat(),
            "orlando_time": orlando["display"],
            "orlando_time_iso": orlando["iso"],
            "request_id": request_id,
            "model": getattr(settings, "OPENAI_MODEL", ""),
        })
    except Exception as e:
        logger.exception("Chat API hatası: %s", e)
        return JsonResponse(
            {"error": "İşlem sırasında bir hata oluştu."},
            status=500,
        )
