# 🚀 GitHub Setup Instructions

## Repository Created Locally

Kode sudah siap dan di-commit di branch `feature/youtube-shorts-whatsapp-bot`.

Untuk push ke GitHub, ikuti langkah-langkah berikut:

---

## Option 1: Buat Repository di GitHub.com (Recommended)

### Langkah 1: Buat Repository Baru
1. Buka https://github.com/new
2. Isi form:
   - **Repository name:** `youtube-shorts-whatsapp-bot`
   - **Description:** `Auto-generated YouTube Shorts content scripts in Bahasa Indonesia with WhatsApp bot integration`
   - **Public** ✅
   - **Don't initialize with README** ✅
3. Klik **Create repository**

### Langkah 2: Push Kode
Setelah buat repository, jalankan:

```bash
cd /workspace/project

# Add remote (ganti USERNAME dengan username GitHub kamu)
git remote add origin https://github.com/USERNAME/youtube-shorts-whatsapp-bot.git

# Push
git push -u origin feature/youtube-shorts-whatsapp-bot
```

### Langkah 3: Buat Pull Request
```bash
gh pr create --title "feat: Add YouTube Shorts generator and WhatsApp bot" --body "## Summary
- YouTube Shorts Generator dengan 8 niche Bahasa Indonesia
- WhatsApp Bot dengan pywhatkit/selenium integration
- Auto-generate script setiap 5 menit
- JSON output format" --base main
```

---

## Option 2: Via GitHub CLI

```bash
# Buat repo
gh repo create youtube-shorts-whatsapp-bot --public

# Push
git push -u origin feature/youtube-shorts-whatsapp-bot

# Buat PR
gh pr create --fill
```

---

## Option 3: Via Browser

1. Buka https://github.com/new
2. Buat repository baru
3. Di halaman kosong repo, cari tombol **"push an existing repository from command line"**
4. Copy-paste command yang ditampilkan

---

## ⚠️ Catatan Penting

- Pastikan GitHub token punya permission `repo` untuk create repository
- Jika tidak punya permission, minta admin untuk extend token scope
- Atau buat repository manual di web dan push ke sana

---

## 📁 Struktur Final Project

```
youtube-shorts-whatsapp-bot/
├── youtube_shorts_generator/
│   ├── __init__.py
│   └── youtube_shorts_generator.py
├── whatsapp_bot/
│   ├── __init__.py
│   └── whatsapp_bot.py
├── scripts/
│   └── shorts_script_*.json
├── requirements.txt
├── README.md
├── .gitignore
└── GITHUB_SETUP.md
```

---

## 🔧 Setup Setelah Clone

```bash
# Clone repository
git clone https://github.com/USERNAME/youtube-shorts-whatsapp-bot.git
cd youtube-shorts-whatsapp-bot

# Install dependencies
pip install -r requirements.txt

# Jalankan YouTube Shorts Generator
python youtube_shorts_generator/youtube_shorts_generator.py

# Jalankan WhatsApp Bot
python whatsapp_bot/whatsapp_bot.py
```
