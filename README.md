# 🎓 Akademik AI Aggregator

Akademik dosya yönetimi ve yapay zeka destekli bilgi sistemi.

## Özellikler

- **📁 Dosya Yönetimi**: Google Drive benzeri arayüz ile dosya yükleme, indirme, silme
- **🤖 AI Asistan**: Veritabanına bağlı yapay zeka ile dosyalar hakkında soru sorma
- **📚 Bilgi Tabanı**: Akademik bilgileri kaydetme ve yönetme
- **📊 İstatistikler**: Sistem kullanım istatistikleri
- **🔍 Arama**: Dosya ve bilgi arama

## Kurulum

### 1. Gereksinimler
- Python 3.10+

### 2. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### 3. Ortam değişkenleri (opsiyonel)
```bash
cp .env.example .env
# .env dosyasına OpenAI API anahtarınızı ekleyin
```

### 4. Uygulamayı çalıştırın
```bash
python main.py
```

Uygulama `http://localhost:8000` adresinde çalışacaktır.

## API Endpoints

| Yöntem | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/files` | Dosyaları listele |
| POST | `/api/files` | Dosya yükle |
| GET | `/api/files/{id}` | Dosya detayı |
| DELETE | `/api/files/{id}` | Dosya sil |
| GET | `/api/files/{id}/download` | Dosya indir |
| POST | `/api/ai/query` | AI'a soru sor |
| GET | `/api/ai/history` | AI sorgu geçmişi |
| POST | `/api/knowledge` | Bilgi ekle |
| GET | `/api/knowledge` | Bilgi listele |
| DELETE | `/api/knowledge/{id}` | Bilgi sil |
| GET | `/api/stats` | İstatistikler |

## Veritabanı

SQLite veritabanı otomatik olarak oluşturulur (`academic_ai.db`).

### Tablolar:
- **users**: Kullanıcılar
- **files**: Dosya metadata
- **ai_queries**: AI sorgu geçmişi
- **knowledge_base**: Bilgi tabanı

## AI Entegrasyonu

- **OpenAI API anahtarı varsa**: GPT-4o-mini kullanılır
- **Yoksa**: Yerel veritabanı araması ile yanıt üretilir
