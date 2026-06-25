# 🎬 YouTube Shorts Generator & WhatsApp Bot

Auto-generated YouTube Shorts content scripts dalam Bahasa Indonesia 🇮🇩

## 📋 Fitur

### YouTube Shorts Generator
- ✅ Generate script otomatis untuk 8 niche berbeda
- ✅ Format JSON siap pakai
- ✅ B-roll prompts, text overlays, SFX cues
- ✅ Loop mechanics untuk infinite scroll effect
- ✅ SEO-optimized metadata

### WhatsApp Bot
- ✅ Auto-generate setiap 5 menit
- ✅ Kirim script via WhatsApp
- ✅ 11+ commands untuk kontrol
- ✅ History script management
- ✅ Export ke JSON

## 📚 Niche yang Tersedia

1. Teknologi & Gadget
2. Tips Kesehatan & Fitness
3. Keuangan & Investasi
4. Masakan & Resep
5. Motivasi & Produktivitas
6. Gaming
7. Fashion & Gaya Hidup
8. Berita & Event Trending

## 🚀 Cara Pakai

### 1. Generate Script Manual

```bash
cd youtube_shorts_generator
python youtube_shorts_generator.py
```

### 2. Jalankan WhatsApp Bot

```bash
cd whatsapp_bot
pip install -r requirements.txt
python whatsapp_bot.py
```

### 3. WhatsApp Bot Commands

| Command | Fungsi |
|---------|--------|
| `!help` | Tampilkan semua perintah |
| `!topics` | Daftar semua topik |
| `!generate` | Generate script baru |
| `!generate <topik>` | Generate untuk topik tertentu |
| `!list` | Lihat semua script |
| `!script <nomor>` | Lihat script tertentu |
| `!save` | Simpan script ke file |
| `!export` | Export semua script |
| `!stats` | Statistik penggunaan |
| `!schedule` | Setup auto-generate |
| `!stop` | Stop auto-generate |

## 📄 Output Format

```json
{
  "timestamp": "2026-06-25T17:12:46.066945Z",
  "meta": {
    "topic": "Teknologi & Gadget",
    "target_audience": "Pengguna smartphone Indonesia",
    "seo_keywords": ["smartphone", "tips hp", "teknologi"]
  },
  "youtube_metadata": {
    "title": "🚨 HP Kamu Aman? Cek 5 Tanda HP Disadap! 📱",
    "description": "Deskripsi dengan hashtags...",
    "tags": ["teknologi", "gadget", "indonesia"]
  },
  "content": [
    {
      "timestamp_range": "00:00 - 00:03",
      "voiceover": "Script untuk voiceover",
      "visual_broll": "Prompt untuk video generation",
      "text_overlay": "Text yang muncul di layar",
      "audio_sfx": "Sound effect cue"
    }
  ]
}
```

## 📂 Struktur Project

```
.
├── youtube_shorts_generator/
│   └── youtube_shorts_generator.py    # Script generator
├── whatsapp_bot/
│   └── whatsapp_bot.py               # WhatsApp bot
├── requirements.txt                   # Dependencies
└── README.md                          # Documentation
```

## 🛠️ Teknologi

- **Python 3.8+**
- **whatsapp-web.js** - WhatsApp Web API
- **Selenium** - Browser automation
- **JSON** - Data format

## 📝 Lisensi

MIT License

---

_by OpenHands Agent 🤖_
