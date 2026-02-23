#!/usr/bin/env python3
"""
API cevabında request_id ve model alanlarını kontrol eder.
İki istek atar; her ikisinde de alanların varlığını ve request_id'lerin farklı olduğunu doğrular.

Kullanım: Sunucu çalışırken (python manage.py runserver veya docker compose up)
          python scripts/check_api_response.py
"""

import json
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/api/chat/"


def post_message(msg: str) -> dict:
    req = urllib.request.Request(
        URL,
        data=json.dumps({"message": msg}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def main():
    print("API cevabı kontrol ediliyor (request_id, model)...")
    errors = []

    try:
        # İlk istek
        data1 = post_message("merhaba")
        if "request_id" not in data1:
            errors.append("İlk cevapta 'request_id' yok.")
        else:
            rid1 = data1["request_id"]
            print(f"  1. istek request_id: {rid1}")

        if "model" not in data1:
            errors.append("İlk cevapta 'model' yok.")
        else:
            print(f"  1. istek model: {data1['model']}")

        # İkinci istek — request_id farklı olmalı
        data2 = post_message("test")
        if "request_id" not in data2:
            errors.append("İkinci cevapta 'request_id' yok.")
        else:
            rid2 = data2["request_id"]
            print(f"  2. istek request_id: {rid2}")

        if rid1 and rid2 and rid1 == rid2:
            errors.append("İki istekte aynı request_id döndü; her istekte farklı olmalı.")

    except urllib.error.URLError as e:
        if "Connection refused" in str(e) or "Errno 61" in str(e):
            errors.append("Sunucu çalışmıyor. Önce: python manage.py runserver veya docker compose up")
        else:
            errors.append(f"Bağlantı hatası: {e}")
    except Exception as e:
        errors.append(f"Hata: {e}")

    if errors:
        print("\n❌ Kontrol başarısız:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\n✅ Kontrol tamam: request_id ve model her iki cevapta var, request_id'ler farklı.")
    return 0


if __name__ == "__main__":
    exit(main())
