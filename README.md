# End to End AI Engineer Project

Django + OpenAI Function Calling — lokal klasörden proje alma, dosya okuma, metin değiştirme.

## Başlarken

1. **API anahtarını ayarla**  
   `.env.example` dosyasını kopyalayıp `.env` yap, içine OpenAI API anahtarını yaz:
   ```bash
   cp .env.example .env
   # .env içinde: OPENAI_API_KEY=sk-...
   ```

2. **Sanal ortamı aç ve sunucuyu çalıştır**
   ```bash
   source venv/bin/activate   # Windows: venv\Scripts\activate
   python manage.py runserver
   ```
   Tarayıcıda http://127.0.0.1:8000/ açılır.

3. **Kaynak klasör (opsiyonel)**  
   Proje alınacak izinli klasörü `.env` içinde `SOURCE_PROJECTS_DIR` ile verebilirsin. Vermezsen proje kökünde `source_projects` kullanılır.

## Chat API'yi denemek

Sunucu çalışırken (başka bir terminalde):

```bash
./test_chat.sh
```

Varsayılan mesaj gider. Kendi mesajınla denemek için:

```bash
./test_chat.sh "calisma2/merhaba.txt dosyasını oku"
./test_chat.sh "deneme_projeyi calisma3 e kopyala"
```

## Docker ile çalıştırmak (Faz 5)

Proje kökünde `.env` dosyası olmalı (OpenAI API key vb.). Sonra:

```bash
docker compose up --build
```

Tarayıcıda http://127.0.0.1:8000/ açılır. Durdurmak için `Ctrl+C`.

- `workspace` ve `source_projects` klasörleri volume ile bağlıdır; veri kalıcıdır.
- Loglar (istek, tool çağrısı, sonuç) konsolda görünür.

## Agent akışını loglarda görmek ([AGENT] satırları)

Adım adım akışı (tur, tool çağrısı, nihai cevap) **yerel runserver** ile en net görürsün:

1. Docker’ı durdur (port 8000 boş kalsın): `docker compose down`
2. Bir terminalde: `source venv/bin/activate` → `python manage.py runserver`
3. Başka bir terminalde veya tarayıcıdan istek at: `./test_chat.sh "calisma1/merhaba.txt dosyasını oku"`
4. **Runserver’ın çalıştığı terminalde** `[AGENT] --- Akış başladı ---`, `[AGENT] (3) Model tool çağırmak istiyor`, `[AGENT] (5) Model nihai metin cevabı verdi` vb. satırları görürsün.

Docker’da bazen bu satırlar `docker compose logs` çıktısında görünmeyebilir; yerel runserver’da her zaman aynı terminalde çıkar.

Detaylı adımlar: `YOL_HARITASI.md`