# AI Engineer Agent - Django + OpenAI Function Calling

Lokal klasörden alınan projeleri OpenAI function calling aracılığıyla otomatik olarak düzenleyen bir Django uygulaması.

## 🎯 Proje Amacı

Bu proje aşağıdaki beceri setini öğretmeyi amaçlaşmaktadır:
- Django ile API ve ön yüz birlikte kurgulamak
- OpenAI function calling mantığını anlamak
- Tool çağrısı döngüsünü uygulamak
- Güvenli dosya işlemleri yapı mak
- Docker ile containerization

## 🚀 Kurulum

### 1. Sanal Ortam ve Paketler
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Ortam Değişkenleri
```bash
cp .env.example .env
# .env dosyasında OPENAI_API_KEY'i düzenle
```

### 3. Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Server Çalıştırma
```bash
python manage.py runserver
# http://localhost:8000 adresinde açılır
```

## 🐳 Docker ile Çalıştırma

```bash
docker-compose up --build
# http://localhost:8000 adresinde açılır
```

## 📋 API Endpoints

### POST /api/chat/
Chat API - Mesaj gönder ve cevap al

**Request:**
```json
{
    "message": "Proje klasörünü al",
    "session_id": "opsiyonel"
}
```

**Response:**
```json
{
    "success": true,
    "response": "Proje başarıyla alındı...",
    "session_id": "uuid-string",
    "turns": 2,
    "tool_calls": [
        {
            "name": "pull_project_from_source",
            "input": {"project_name": "..."},
            "result": {...}
        }
    ]
}
```

### GET /
Ana sayfa - Chat ön yüzü

## 🛠️ Mevcut Tools

### 1. pull_project_from_source
Lokal kaynak klasörden bir projeyi çalışma alanına kopyalar.

**Parametreler:**
- `project_name` (string): Kopyalanacak proje klasörünün adı

**Örnek:**
```
"Proje klasörünü al"
```

### 2. read_file_from_workspace
Çalışma alanındaki bir dosyayı okur.

**Parametreler:**
- `file_path` (string): Çalışma alanı içinde göreceli path

**Örnek:**
```
"Proje adında __init__.py dosyasını oku"
```

### 3. replace_file_content
Dosya içeriğinde bir metni başka bir metinle değiştirir.

**Parametreler:**
- `file_path` (string): Düzenlenecek dosya
- `old_text` (string): Bulunacak metin
- `new_text` (string): Yerine konulacak metin

**Örnek:**
```
"main.py dosyasında 'hello' yazısını 'merhaba' olarak değiştir"
```

## 🔒 Güvenlik Kuralları

1. **Path Validation**: Yalnızca çalışma alanı içindeki dosyalara erişim
2. **Traversal Koruması**: `../` ile ust dizine çıkış engellenir
3. **Duplicat Kontrol**: Aynı proje iki kez alınamaz
4. **Kaynak Kontrol**: Yalnızca izinli kaynak klasörden proje alınır

## 📁 Klasör Yapısı

```
project/
├── aiagent/              # Django settings
│   ├── settings.py       # .env'den değişkenleri oku
│   ├── urls.py          # API routes
│   └── wsgi.py
├── chat/                # Chat app
│   ├── models.py        # ChatSession, Message, ToolCall
│   ├── views.py         # API endpoints
│   ├── agent.py         # OpenAI agent logic
│   ├── tools.py         # Tool implementations
│   ├── security.py      # Path validation
│   └── admin.py         # Django admin
├── templates/           # HTML templates
│   └── chat/
│       └── index.html   # Chat UI
├── static/              # CSS, JS, images
├── manage.py            # Django CLI
├── requirements.txt     # Python packages
├── Dockerfile           # Container image
├── docker-compose.yml   # Orchestration
└── .env.example         # Environment template
```

## 🧪 Test Senaryoları

### 1. Proje Alma
**Input:** "Proje klasörünü al"
**Expected:** Proje başarıyla workspace'e kopyalanır

### 2. Dosya Okuma
**Input:** "Proje adında var olan bir dosyayı oku"
**Expected:** Dosya içeriği döner

### 3. Dosya Düzenleme
**Input:** "Dosya içeriğinde metin değiştir"
**Expected:** Metin başarıyla değiştirilir

### 4. Hata Senaryoları
- Olmayan dosya okuma
- Workspace dışı path erişimi
- Duplicate proje alma
- Geçersiz JSON

## 📊 Function Calling Akışı

```
1. User Message
   ↓
2. OpenAI Model (gpt-4o-mini)
   ↓
3. Tool Call Detected? 
   ├─ Yes → Execute Tool
   │        ↓
   │        Tool Result
   │        ↓
   │        Back to Step 2 (max 10 turns)
   └─ No → Final Response
        ↓
4. Return Response to UI
```

## 🔧 Ayarlar (.env)

```
SECRET_KEY=your-key
DEBUG=True
OPENAI_API_KEY=sk-...
ALLOWED_HOSTS=localhost,127.0.0.1
WORKSPACE_DIR=/tmp/ai_workspace
SOURCE_PROJECT_DIR=/apps/end_to_end_AI_Engineer_project
```

## 📝 Logging

Uygulaması şu işlemleri loglar:
- Kullanıcı mesajları
- Tool çağrıları ve parametreleri
- Tool sonuçları
- Hata ve istisna durumları

Logları görüntülemek:
```bash
python manage.py runserver | grep -E "(Tool|Error|Message)"
```

## 🐛 Debugging

Django debug mode anutol:
```bash
DEBUG=True python manage.py runserver
```

OpenAI call'ları debug:
```python
# views.py veya agent.py'de
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Öğrenci Çıktıları

Proje tamamlanırken:
- ✅ Django template sistemini anlamak
- ✅ OpenAI API ile entegrasyon yapmak
- ✅ Function calling mantığını uygulamak
- ✅ Dosya system işlemleri ve güvenliği
- ✅ Docker containerization

## 🎓 Kabul Kriterleri

- [ ] Chat endpoint çalışıyor
- [ ] OpenAI function call yapılıyor
- [ ] 3 tool tamamlandı
- [ ] Güvenlik kuralları uygulanıyor 
- [ ] Template ön yüz tarayıcıda çalışıyor
- [ ] Docker Compose ile başlatılabiliyor
- [ ] Loglar kritik adımları gösteriyor

## 🔗 Teknoloji Stack

- **Backend**: Django 6.0
- **API**: OpenAI GPT-4o-mini  
- **Database**: SQLite (Development)
- **Frontend**: HTML + Vanilla JS
- **Container**: Docker + Docker Compose
- **Python Version**: 3.12

## 📞 Destek

Sorunlar veya sorularınız için:
1. Logları (stdout) kontrol edin
2. Django admin paneline gidip ChatSession/Message/ToolCall tuşa bakın
3. .env dosyasının doğru yapılandırıldığından emin olun

