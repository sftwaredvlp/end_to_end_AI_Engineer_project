# Proje Amacına Yönelik Pratikler

Her maddeyi sırayla yap. Cevap veya kod takıldığında "şu maddeyi yapıyorum, şuraya takıldım" de; birlikte üzerinden geçeriz.

---

## 1. Django ile API ve ön yüzü birlikte kurgulamak

**Pratik 1.1 — Eşleştirme**  
Projede API tarafı ile ön yüzün nasıl bağlandığını bul:

- Tarayıcıda "Gönder"e bastığında istek hangi URL’e gidiyor? (Sayfadaki JavaScript’e bak.)
- Bu URL’i Django’da hangi view karşılıyor? (Önce `config/urls.py`, sonra `chat/views.py`.)

**Pratik 1.2 — Küçük değişiklik**  
API’nin döndüğü JSON’a bir alan daha ekle (örneğin `"test": "pratik"`). Değişikliği `chat/views.py` içinde `chat_api` fonksiyonunda yap. Tarayıcıda bir mesaj gönderip (veya `./test_chat.sh`) cevabı inceleyerek yeni alanın geldiğini gör.

---

## 2. Ön yüzde Django Template ile chat/komut ekranı

**Pratik 2.1 — Template nerede?**  
Chat ekranının HTML’i hangi dosyada? (Proje içinde "Mesajın" veya "Gönder" geçen dosyayı bul.)

**Pratik 2.2 — Placeholder değiştir**  
Mesaj kutusundaki placeholder metnini değiştir (örneğin: "Örn: calisma2/merhaba.txt dosyasını oku"). Sayfayı yenileyip değişikliği gör.

**Pratik 2.3 — Cevap kutusunun rengi**  
Başarılı cevap kutusu şu an yeşil. Template’teki CSS’te bu rengi değiştir (örneğin açık mavi). Kaydedip sayfayı yenile.

---

## 3. OpenAI function calling mantığını anlamak

**Pratik 3.1 — Tool listesi**  
Modelin kullanabileceği araçlar nerede tanımlı? `chat/services/agent.py` dosyasını aç; `TOOLS_DEFINITION` listesinde kaç araç var ve her birinin `name` değeri ne?

**Pratik 3.2 — Bir aracın parametreleri**  
`read_file_in_workspace` için OpenAI’ye verilen tanımda (agent.py içinde) hangi parametre var? İsmi ve kısa açıklaması ne?

**Pratik 3.3 — Deney**  
Tarayıcıdan veya `./test_chat.sh` ile şu mesajı gönder: "calisma1/merhaba.txt dosyasının ilk satırını oku ve bana yaz." Cevabı incele: Model hangi tool’u kullanmış olmalı?

---

## 4. Modelin araç çağırdığı iş akışında doğru sıra

**Pratik 4.1 — Akışı takip et**  
`agent.py` içinde `run_agent` fonksiyonunu oku. Adımlar kabaca şöyle mi: (1) kullanıcı mesajı modele gidiyor, (2) model tool_calls döndürürse tool’lar çalıştırılıyor, (3) tool sonuçları modele geri veriliyor, (4) model nihai cevabı yazıyor? Evet/hayır ve kısaca neden?

**Pratik 4.2 — Maksimum tur**  
Sonsuz döngüyü engellemek için `run_agent` içinde bir limit var mı? Varsa değişken adı ve varsayılan değeri ne?

**Pratik 4.3 — İki tool arka arkaya**  
Şu mesajı gönder: "Önce calisma1/merhaba.txt dosyasını oku, sonra calisma2/merhaba.txt dosyasını oku ve ikisini karşılaştır." Cevabı oku; model muhtemelen iki kez tool çağırmış olacak. (İsteğe bağlı: `docker compose logs` veya terminal loglarına bakıp tool çağrılarını say.)

---

## 5. Lokal kaynaktan proje alma, dosya okuma, metin değiştirme

**Pratik 5.1 — Üç tool’u çağır**  
Sırayla şu üç işlemi **tarayıcıdan veya test_chat.sh ile** yap; her birinde cevabın başarılı olduğunu gör:

1. "deneme_projeyi calisma_pratik klasörüne kopyala"
2. "calisma_pratik/merhaba.txt dosyasını oku"
3. "calisma_pratik/merhaba.txt dosyasında 'deneme' kelimesini 'pratik' ile değiştir"

Sonra `workspace/calisma_pratik/merhaba.txt` dosyasını açıp "pratik" geçtiğini kontrol et.

**Pratik 5.2 — Hata senaryosu**  
Şu mesajı gönder: "var_olmayan_klasor/abc.txt dosyasını oku." Cevapta hata mesajı gelmeli. Mesajın anlaşılır olduğunu kontrol et.

**Pratik 5.3 — Güvenlik**  
`chat/tools/path_utils.py` dosyasını aç. `has_traversal` ne yapıyor? Neden `..` veya `/` ile başlayan path’leri reddediyoruz, tek cümleyle yaz.

---

## 6. Dockerfile ve Docker Compose ile çalışır hale getirmek

**Pratik 6.1 — Dockerfile adımları**  
`Dockerfile` dosyasını aç. Sırayla hangi işlemler yapılıyor? (FROM, WORKDIR, COPY, RUN, CMD vb. satırlarını kendi cümlelerinle özetle.)

**Pratik 6.2 — Compose’da port ve env**  
`docker-compose.yml` içinde uygulama hangi portu dışarı açıyor? API anahtarı container’a nasıl veriliyor (hangi anahtar)?

**Pratik 6.3 — Volume**  
`workspace` ve `source_projects` klasörleri Docker’da neden volume ile bağlı? Volume kullanmasaydık ne olurdu (bir cümle)?

---

## 7. Kritik adımları uygulama loglarından izleyebilmek

**Pratik 7.1 — Log nerede yazılıyor?**  
`chat/views.py` ve `chat/services/agent.py` dosyalarında `logger.info` (veya benzeri) ile ne loglanıyor? Birer cümleyle yaz.

**Pratik 7.2 — Logları gör**  
Docker ile çalıştırıyorsan: `docker compose up` çalışırken bir mesaj gönder (tarayıcıdan veya test_chat.sh). Aynı terminalde "Chat API isteği", "Tool çağrısı" vb. satırların çıktığını gör. Yerelde `python manage.py runserver` ile çalıştırıyorsan aynı denemeyi yapıp runserver’ın açık olduğu terminalde logları izle.

**Pratik 7.3 — Kısa özet**  
Bir chat isteğinde sırayla logda ne görürsün? (İstek geldi → tool çağrıldı → sonuç döndü gibi 2–3 cümle.)

---

## Bitiş

Tüm maddeleri yaptıysan, proje amacındaki yedi beceriyi pratikle pekiştirmiş oldun. Takıldığın maddeyi yazarsan, o maddeye özel adım adım yardım edebilirim.
