# Proje Devami: RAG + LangChain (2. Dosya)

Bu dokuman, `1-Project-taks.ipynb` icindeki temel akisin devamidir.
Bu asamada en uygun yol: **RAG + LangChain**.

## Neden Bu Secim?

- Mevcut proje zaten agent/tool dusuncesine sahip.
- RAG, modele dogrudan ezber yerine **dokuman tabanli cevap** uretmeyi saglar.
- LangChain; bolme (chunking), embedding, retriever ve zincir kurulumunu hizlandirir.
- MCP bu noktada zorunlu degil; daha sonra harici araclari standart protokolle baglamak icin eklenebilir.

## Hedef

Uygulamanin, sadece genel model cevabi degil;
proje dokumanlarina dayanarak kaynak gosterebilen yanitlar uretmesi.

## Faz 2 Mimari (Ozet)

1. **Ingestion**
   - `README.md` ve proje dokumanlarini oku
   - Metinleri parcalara ayir (chunk)
2. **Indexing**
   - Embedding olustur
   - Vektor veritabanina yaz (FAISS/Chroma)
3. **Retrieval**
   - Kullanici sorusunda ilgili parcalari bul
4. **Generation**
   - Bulunan parcalar + soru ile LLM cevabi olustur
5. **Grounding Kontrolu**
   - Cevapta kullanilan kaynaklari listele

## Teknik Yol Haritasi

### 1) Paketler

- `langchain`
- `langchain-openai`
- `langchain-community`
- `faiss-cpu` (veya `chromadb`)
- `tiktoken`

### 2) Yeni Moduller

- `rag/loader.py` -> dosya okuma ve temizleme
- `rag/indexer.py` -> chunk + embedding + index yazma
- `rag/retriever.py` -> benzer parca getirme
- `rag/chain.py` -> retriever + prompt + llm akisi

### 3) Django Entegrasyonu

- Chat endpoint'i icinde su sira izlenir:
  1. Soru al
  2. Retriever ile baglam cek
  3. LLM'e baglam + soru gonder
  4. Cevap + kaynak dosya yollarini don

### 4) Basari Kriterleri

- Ayni soru, baglamsiz modele gore daha dogru cevap uretiyor mu?
- Cevapta en az 1 kaynak dokuman listeleniyor mu?
- Dokuman degistiginde index guncellenince cevaplar da degisiyor mu?

## MCP Ne Zaman Eklenmeli?

MCP'yi su durumda eklemek mantikli olur:
- Birden fazla harici araca (dosya sistemi, veritabani, issue tracker vb.) standart arayuzle baglanmak istiyorsan
- Agent'in farkli servislerle guvenli/izlenebilir sekilde konusmasini istiyorsan

Bu projede siralama onerisi:
1. Once **RAG + LangChain** ile bilgi tabanli cevaplari oturt
2. Sonra gerekiyorsa **MCP** ile arac ekosistemini buyut

## Kisa Sonuc

Bu proje devami icin en uygun tercih: **RAG + LangChain**.
MCP, cekirdek RAG akisi stabil olduktan sonra 2. genisleme adimi olarak eklenmeli.
