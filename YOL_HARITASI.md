# Django + OpenAI Function Calling — Yol Haritası

Bu doküman, **1-Project-taks.ipynb** içindeki adımlara göre hazırlanmış pratik bir yol haritasıdır.

---

## Genel Bakış

| Aşama | Konu | Tahmini süre |
|-------|------|--------------|
| 0 | Ortam hazırlığı | 1 gün |
| 1 | Proje iskeleti + klasör yapısı | 1–2 gün |
| 2 | Ayarlar + güvenlik + tool tasarımı | 1–2 gün |
| 3 | Agent + function calling + API | 2–3 gün |
| 4 | Ön yüz (Django Template) | 1 gün |
| 5 | Docker + test + teslim | 1–2 gün |

**Toplam:** yaklaşık 7–10 gün (tempo size bağlı).

---

## Faz 0: Başlamadan Önce (Bölüm 2)

**Yapılacaklar:**

- [ ] Güncel Python (3.10+ önerilir) kurulu
- [ ] [OpenAI](https://platform.openai.com/) hesabı + API anahtarı
- [ ] Çalışma klasörü (örn. `end_to_end_AI_Engineer_project`)
- [ ] Proje alınacak **kaynak klasör** (lokal, izin verilen tek yer)
- [ ] Docker + Docker Compose kurulu

**Çıktı:** Ortam hazır; proje kurulumuna geçilebilir.

---

## Faz 1: Proje İskeleti (Bölüm 3 + 4)

### 1.1 Django projesi (Bölüm 3)

1. Yeni proje klasörü aç
2. Sanal ortam: `python -m venv venv` → aktif et
3. Kur: `django`, `openai` (ve ihtiyaç varsa `python-dotenv`)
4. `django-admin startproject <proje_adi> .`
5. `python manage.py startapp <uygulama_adi>`

**Çıktı:** Proje açılıyor, `manage.py runserver` çalışıyor.

### 1.2 Yapısal klasörler (Bölüm 4)

Uygulama içinde şu sorumlulukları net ayır:

| Katman | Amaç | Örnek |
|--------|------|--------|
| **API** | İstek al, cevap dön | `views.py`, `urls.py` (chat endpoint) |
| **Agent** | LLM + function call döngüsü | `agent.py` veya `services/agent.py` |
| **Tool** | Proje alma, dosya oku, metin değiştir | `tools/` (3 fonksiyon) |
| **Template** | Kullanıcı ekranları | `templates/` |
| **Static** | CSS, JS | `static/` |
| **Çalışma alanı** | Alınan projelerin kopyalandığı klasör | `workspace/` (izinli tek yazma alanı) |

**Çıktı:** Her sorumluluk ayrı dosya/klasörde.

---

## Faz 2: Ayarlar, Güvenlik, Tool Tasarımı (Bölüm 5, 6, 7)

### 2.1 Ayarlar ve anahtarlar (Bölüm 5)

- [ ] API anahtarı **kodda yok**; `.env` kullan
- [ ] Django settings’te: `OPENAI_API_KEY`, model adı `.env`’den okunur
- [ ] Uygulama `INSTALLED_APPS`’e eklendi
- [ ] `TEMPLATES` ve `STATIC` dizinleri açıkça ayarlandı

**Çıktı:** Anahtarlar güvenli ve merkezi.

### 2.2 Tool tasarımı — 3 araç (Bölüm 6)

Sadece tasarım (parametreler, davranış); kod sonra yazılacak.

| # | Aracın adı | Girdi | Çıktı (başarı) | Hata |
|---|------------|--------|-----------------|------|
| 1 | **Proje al** | Kaynak klasör yolu, hedef çalışma klasörü adı | "Proje X, Y klasörüne kopyalandı" | Kaynak yok, hedef dolu, path güvensiz |
| 2 | **Dosya oku** | Çalışma alanındaki dosya yolu (relative) | Dosya içeriği (metin) | Dosya yok, path güvensiz |
| 3 | **Metin değiştir** | Dosya yolu, eski metin, yeni metin | "X satırda Y değiştirildi" | Dosya yok, metin bulunamadı, path güvensiz |

**Çıktı:** Her aracın amacı, girdisi ve hata mesaj mantığı net.

### 2.3 Güvenlik kuralları (Bölüm 7)

- [ ] Sadece **belirlenen çalışma klasörü** altında işlem
- [ ] Sadece **izinli kaynak klasör**den proje alma
- [ ] `../` gibi üst dizine çıkış **reddedilir**
- [ ] Olmayan dosya/klasör için **açık hata mesajı**
- [ ] Aynı hedefe ikinci “proje alma” **kontrol edilir** (üzerine yazma / çakışma)

**Çıktı:** Araçlar kontrollü; sadece izin verilen alanlarda çalışır.

---

## Faz 3: Function Calling + API (Bölüm 8, 9)

### 3.1 Function calling akışı (Bölüm 8)

```
Kullanıcı mesajı → Model → (gerekirse) tool önerisi
    → Tool çalıştır → Sonucu modele ver → Model nihai cevabı üret
```

- [ ] **Maksimum tur sayısı** (örn. 5–10) tanımla; sonsuz döngüyü engelle
- [ ] Tool sonuçları modele **tekrar gönderilir**; model gerekirse yeni tool önerebilir

**Çıktı:** Agent katmanında bu döngü kodda net.

### 3.2 Django API ucu (Bölüm 9)

- [ ] Tek endpoint (örn. `/api/chat/` veya `/chat/`)
- [ ] Sadece **POST**
- [ ] Body: JSON, örn. `{"message": "..."}`
- [ ] Bu istek → agent’ı tetikler → sonuç JSON döner
- [ ] Loglara yaz: gelen istek, yapılan tool çağrıları, dönen sonuç

**Hata senaryoları:**

- Boş mesaj → 400 + açıklayıcı mesaj
- Geçersiz JSON → 400
- İç işlem hatası → 500 + güvenli mesaj (detay logda)

**Çıktı:** Postman/curl ile endpoint test edilebilir.

---

## Faz 4: Ön Yüz — Django Template (Bölüm 10)

- [ ] Template klasör yapısı (uygulama/templates/…)
- [ ] Basit bir ekran: kullanıcı komutu yazabilsin (input + buton)
- [ ] Form/JS ile API endpoint’ine POST
- [ ] Cevap aynı sayfada gösterilsin
- [ ] Hata mesajları okunaklı (ör. kırmızı kutu)

**Çıktı:** Tarayıcıdan chat/komut ekranı çalışıyor.

---

## Faz 5: Docker + Test + Teslim (Bölüm 11, 12, 13, 14)

### 5.1 Docker (Bölüm 11)

- [ ] **Dockerfile:** Python + dependencies + uygulama kopyalama + `run`
- [ ] **docker-compose.yml:** servis tanımı, port, env dosyası
- [ ] `.env` container’a geliyor (volume veya env_file)
- [ ] `docker compose up` ile uygulama ayağa kalkıyor
- [ ] Loglardan istek → tool çağrıları → sonuç görünüyor

**Çıktı:** Tek komutla konteyner üzerinden çalışan uygulama.

### 5.2 Test senaryoları (Bölüm 12)

Sırayla dene ve sonucu not et:

1. Lokal kaynaktan projeyi çalışma klasörüne alma
2. Alınan projeden bir metin dosyası okuma
3. Dosyada hedef metni değiştirme
4. Olmayan dosyayı okuma → hata mesajı
5. Güvensiz path (örn. `../etc/passwd`) → red
6. Template ekranından API’nin çalışması
7. Docker Compose ile uygulamanın kalkması
8. Loglarda tool çağrıları ve sonuç görünmesi

**Çıktı:** Her senaryoda beklenen davranış (başarı veya hata) net.

### 5.3 Teslim (Bölüm 13)

- Kısa mimari açıklama (1 sayfa)
- Hangi aracın ne yaptığı özeti
- En az 2 başarılı işlem kanıtı (ekran/log)
- En az 2 hata senaryosu kanıtı
- Template ekranı görüntüsü
- Docker Compose ile çalışan servis kanıtı
- Loglardan akış kanıtı
- Kısa değerlendirme: ne çalıştı, nerede zorlandın, ne öğrendin

### 5.4 Kabul kriterleri (Bölüm 14)

Projeyi teslim etmeden önce tümünü işaretle:

- [ ] Chat endpoint çalışıyor
- [ ] En az bir kez model function call üretti
- [ ] Proje alma aracı başarıyla çalıştı
- [ ] Dosya okuma aracı başarıyla çalıştı
- [ ] Metin değiştirme aracı başarıyla çalıştı
- [ ] Güvensiz path engellendi
- [ ] Hata mesajları anlaşılır
- [ ] Template arayüzü tarayıcıda çalışıyor
- [ ] Dockerfile var ve image oluşuyor
- [ ] Docker Compose ile servis kalkıyor
- [ ] Loglarda istek, tool çağrısı, sonuç görünüyor
- [ ] Test kanıtları düzenli sunuldu
- [ ] Sistem akışını sözlü/yazılı açıklayabiliyorsun

---

## Önerilen Sıra (Tek Sayfa Özet)

```
0. Ortam (Python, API key, Docker, kaynak klasör)
   ↓
1. Django projesi + venv + uygulama + klasör yapısı (API, agent, tools, templates, static, workspace)
   ↓
2. .env + settings + 3 tool tasarımı + güvenlik kuralları
   ↓
3. Tool’ları kodla → Agent (LLM + function call döngüsü, max tur) → API endpoint
   ↓
4. Template + form + API çağrısı + cevap/hata gösterimi
   ↓
5. Dockerfile + docker-compose → test senaryoları → teslim dokümanı + kabul listesi
```

---

## İpuçları

- **Önce tool’ları bitir:** API ve agent, tool’lara güvenecek; önce onları test et.
- **Path’leri sabit tut:** Kaynak ve workspace yollarını settings’te tek yerden oku.
- **Loglama:** Her tool çağrısı ve agent adımını logla; debug ve teslim kanıtı için gerekli.
- **Kabul listesini erken aç:** Bölüm 14’ü proje başında oku; neyin isteneceğini bilerek ilerle.

Bu yol haritası, notebook’taki bölümlerle bire bir eşleşecek şekilde hazırlandı. İstersen bir sonraki adımda doğrudan “Faz 1” için Django komutlarını veya klasör iskeletini birlikte yazabiliriz.
