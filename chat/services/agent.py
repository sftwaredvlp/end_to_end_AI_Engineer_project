# Agent: Kullanıcı mesajı → OpenAI → gerekirse tool çağır → sonucu modele ver → nihai cevap

from __future__ import annotations

import json
import logging
import sys
from typing import Any


_TRACE_FILE = "/tmp/agent_trace.log"


def _log(msg: str) -> None:
    """Akış izi: stderr + dosyaya yaz (Docker'da log bazen görünmeyebiliyor)."""
    print(msg, file=sys.stderr, flush=True)
    try:
        with open(_TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except OSError:
        pass


def _log_json(label: str, data: Any, max_stderr: int = 2000) -> None:
    """Uzun JSON'u trace dosyasında tam, stderr'de kısaltılmış yazar."""
    j = json.dumps(data, ensure_ascii=False, indent=2)
    try:
        with open(_TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(f"{label} (tam):\n{j}\n")
    except OSError:
        pass
    if len(j) <= max_stderr:
        print(f"[AGENT] {label}:\n{j}", file=sys.stderr, flush=True)
    else:
        print(
            f"[AGENT] {label} (ilk {max_stderr} karakter, tam metin: {_TRACE_FILE}):\n{j[:max_stderr]}...",
            file=sys.stderr,
            flush=True,
        )

from django.conf import settings
from openai import OpenAI

from chat.tools import (
    copy_project_to_workspace,
    list_files_in_workspace,
    read_file_in_workspace,
    replace_text_in_file,
    run_linter_in_workspace,
    run_tests_in_workspace,
    search_in_workspace,
)

logger = logging.getLogger(__name__)

# OpenAI'ye anlatacağımız 3 aracın tanımı (function calling formatında)
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "copy_project_to_workspace",
            "description": "İzin verilen kaynak klasöründen bir projeyi çalışma alanına (workspace) kopyalar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_folder_name": {
                        "type": "string",
                        "description": "Kaynak projenin klasör adı (örn. deneme_proje)",
                    },
                    "target_folder_name": {
                        "type": "string",
                        "description": "Workspace içinde oluşacak klasör adı (örn. calisma1)",
                    },
                },
                "required": ["source_folder_name", "target_folder_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_in_workspace",
            "description": "Çalışma alanı (workspace) içindeki bir dosyanın metin içeriğini okur.",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "description": "Workspace'e göre dosya yolu (örn. calisma1/merhaba.txt)",
                    },
                },
                "required": ["relative_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "replace_text_in_file",
            "description": "Workspace içindeki bir dosyada belirtilen metni başka bir metinle değiştirir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "description": "Workspace'e göre dosya yolu (örn. calisma1/merhaba.txt)",
                    },
                    "old_text": {
                        "type": "string",
                        "description": "Dosyada aranacak / değiştirilecek metin",
                    },
                    "new_text": {
                        "type": "string",
                        "description": "Yerine yazılacak metin",
                    },
                },
                "required": ["relative_path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files_in_workspace",
            "description": "Çalışma alanı (workspace) içindeki bir klasörün içeriğini listeler. Önce keşfetmek için kullan; boş relative_path = workspace kökü.",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "description": "Workspace'e göre klasör yolu. Boş veya verilmezse workspace kökü listelenir (örn. calisma1, test_kopya).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_workspace",
            "description": "Workspace içinde metin arar (grep gibi). Hangi dosyada geçtiğini bulmak için kullan; sonra read veya replace yapılabilir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Aranacak metin (büyük/küçük harf duyarsız).",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "Aranacak klasör. Boş = tüm workspace.",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests_in_workspace",
            "description": "Workspace içindeki bir klasörde pytest çalıştırır. Değişiklik sonrası testlerin geçip geçmediğini kontrol etmek için kullan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "description": "Testlerin çalışacağı klasör. Boş = workspace kökü.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_linter_in_workspace",
            "description": "Workspace içindeki bir dosya veya klasörde linter çalıştırır. py_compile (sözdizimi), pylint veya flake8.",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "description": "Dosya veya klasör yolu (örn. calisma1/main.py veya calisma1).",
                    },
                    "linter": {
                        "type": "string",
                        "description": "py_compile (sadece sözdizimi), pylint veya flake8.",
                        "enum": ["py_compile", "pylint", "flake8"],
                    },
                },
                "required": ["relative_path"],
            },
        },
    },
]

SYSTEM_MESSAGE = """Sen bir kod asistanısın. Kullanıcının workspace'indeki projeleri keşfedebilir, dosya okuyup düzenleyebilir, test ve lint çalıştırabilirsin.

Davranış:
- Önce keşfet: list_files_in_workspace ile yapıyı gör, search_in_workspace ile metin/dosya bul.
- Oku ve düzenle: read_file_in_workspace ile içeriği al, replace_text_in_file ile değiştir.
- Doğrula: run_tests_in_workspace (pytest) ile testleri çalıştır, run_linter_in_workspace (py_compile, pylint, flake8) ile kodu kontrol et.
- Proje kopyalama: copy_project_to_workspace ile kaynak projeyi workspace'e al.

Kurallar:
- Sadece verilen araçları kullan. İşlemler yalnızca workspace ve izinli kaynak klasörü içinde.
- Değişiklik yaptıysan özetle; test/lint sonucunu kullanıcıya net aktar.
- Cevabı kısa ve net Türkçe ile ver."""


def run_tool(name: str, arguments: dict[str, Any]) -> str:
    """
    Modelin istediği aracı çalıştırır, sonucu metin olarak döndürür.
    """
    try:
        if name == "copy_project_to_workspace":
            return copy_project_to_workspace(
                arguments["source_folder_name"],
                arguments["target_folder_name"],
            )
        if name == "read_file_in_workspace":
            return read_file_in_workspace(arguments["relative_path"])
        if name == "replace_text_in_file":
            return replace_text_in_file(
                arguments["relative_path"],
                arguments["old_text"],
                arguments["new_text"],
            )
        if name == "list_files_in_workspace":
            return list_files_in_workspace(arguments.get("relative_path", ""))
        if name == "search_in_workspace":
            return search_in_workspace(
                arguments["pattern"],
                arguments.get("relative_path", ""),
            )
        if name == "run_tests_in_workspace":
            return run_tests_in_workspace(arguments.get("relative_path", ""))
        if name == "run_linter_in_workspace":
            return run_linter_in_workspace(
                arguments["relative_path"],
                arguments.get("linter", "py_compile"),
            )
        return f"Hata: Bilinmeyen araç: {name}"
    except Exception as e:
        logger.exception("Tool çalıştırma hatası: %s", e)
        return f"Hata: {e}"


# Konuşma geçmişinde en fazla kaç mesaj (user+assistant çiftleri) kullanılsın (token sınırı için)
MAX_HISTORY_MESSAGES = 20


def run_agent(
    user_message: str,
    conversation_history: list[dict[str, Any]] | None = None,
    max_turns: int = 10,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Kullanıcı mesajını (ve isteğe bağlı konuşma geçmişini) alır, OpenAI ile konuşur;
    model tool isterse çalıştırır, sonucu tekrar modele verir.
    (Nihai metin cevabı, tool adımları listesi) döndürür.
    conversation_history: [{"role": "user"|"assistant", "content": "..."}, ...] — sadece metin, tool ayrıntısı yok.
    """
    steps: list[dict[str, Any]] = []

    if not settings.OPENAI_API_KEY:
        return (
            "Hata: OpenAI API anahtarı ayarlanmamış. Lütfen .env dosyasında OPENAI_API_KEY tanımlayın.",
            steps,
        )

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    history = conversation_history or []
    # Son MAX_HISTORY_MESSAGES mesajı al (eski bağlamı kes)
    trimmed = history[-MAX_HISTORY_MESSAGES:] if len(history) > MAX_HISTORY_MESSAGES else history
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        *trimmed,
        {"role": "user", "content": user_message},
    ]
    turn = 0

    try:
        with open(_TRACE_FILE, "w", encoding="utf-8") as _:
            pass
    except OSError:
        pass
    _log("[AGENT] --- Akış başladı ---")
    _log(f"[AGENT] (1) Kullanıcı mesajı: {user_message[:60]}{'...' if len(user_message) > 60 else ''}")

    while turn < max_turns:
        turn += 1
        logger.info("Agent tur %s, mesaj sayısı: %s", turn, len(messages))
        _log(f"[AGENT] --- Tur {turn} --- Mesaj sayısı: {len(messages)}")
        _log("[AGENT] (2) API'ye istek gidiyor (messages + tools)...")
        _log_json("(2b) Gönderilen messages", messages)

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            tools=TOOLS_DEFINITION,
        )
        choice = response.choices[0]
        message = choice.message

        raw_response = {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
                for tc in (message.tool_calls or [])
            ],
        }
        _log_json("(3b) Model cevabı (ham)", raw_response)

        if message.tool_calls:
            names = [tc.function.name for tc in message.tool_calls]
            _log(f"[AGENT] (3) Model tool çağırmak istiyor: {names}")
            # Assistant mesajını bir kez ekle (tool_calls ile)
            assistant_msg = {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
            messages.append(assistant_msg)
            # Her tool çağrısını çalıştırıp cevabı ekle
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args_str = tool_call.function.arguments
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError as e:
                    args = {}
                    result = f"Hata: Geçersiz argüman JSON: {e}"
                else:
                    result = run_tool(name, args)
                    logger.info("Tool çağrısı: %s -> %s", name, result[:100])
                    short_result = (result[:70] + "...") if len(result) > 70 else result
                    _log(f"[AGENT]     Tool çalıştırıldı: {name} -> {short_result}")
                steps.append({
                    "name": name,
                    "arguments": args,
                    "result": (result[:200] + "…") if len(result) > 200 else result,
                })
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )
            _log(f"[AGENT] (4) Tool sonuçları messages'a eklendi. Döngü devam (tur {turn + 1} için API'ye tekrar gidilecek).")
            continue

        # Tool çağrısı yok; nihai cevap
        _log("[AGENT] (5) Model nihai metin cevabı verdi (tool_calls yok), dönülüyor.")
        if message.content:
            return (message.content.strip(), steps)
        return ("Cevap üretilemedi.", steps)

    _log("[AGENT] Maksimum tur sayısına ulaşıldı.")
    return ("Maksimum tur sayısına ulaşıldı; işlem sonlandırıldı.", steps)
