"""
YouTube Shorts Content Generator
Auto-generated vertical short-form video scripts every 5 minutes
"""

import json
import random
from datetime import datetime
from typing import Dict, List

# Niche topics in Bahasa Indonesia
NICHES = [
    {
        "name": "Teknologi & Gadget",
        "keywords": ["smartphone", "teknologi", "gadget", "android", "iphone", "tips hp"],
        "audience": "Pengguna smartphone Indonesia, ages 18-35"
    },
    {
        "name": "Tips Kesehatan & Fitness",
        "keywords": ["kesehatan", "fitness", "olahraga", "diet", "nutrition", "workout"],
        "audience": "Masyarakat Indonesia yang peduli kesehatan, ages 20-45"
    },
    {
        "name": "Keuangan & Investasi",
        "keywords": ["keuangan", "investasi", "uang", "saving", "crypto", "saham"],
        "audience": "Millennials & Gen Z Indonesia yang ingin finansial literate"
    },
    {
        "name": "Masakan & Resep",
        "keywords": ["masakan", "resep", "makan", "kuliner", "food", "recipe"],
        "audience": "Ibu rumah tangga & cooking enthusiasts Indonesia"
    },
    {
        "name": "Motivasi & Produktivitas",
        "keywords": ["motivasi", "produktivitas", "sukses", "self improvement", "mindset"],
        "audience": "Professionals & students Indonesia"
    },
    {
        "name": "Gaming",
        "keywords": ["gaming", "game", "esports", "mobile game", "pc game"],
        "audience": "Gamers Indonesia, ages 16-30"
    },
    {
        "name": "Fashion & Gaya Hidup",
        "keywords": ["fashion", "style", "OOTD", "gaya hidup", "tren"],
        "audience": "Fashion enthusiasts Indonesia, ages 18-35"
    },
    {
        "name": "Berita & Event Trending",
        "keywords": ["berita", "viral", "trending", "event", "update"],
        "audience": "Netizen Indonesia yang update dengan berita terkini"
    }
]

# Hook templates
HOOK_TEMPLATES = [
    "🚨 {statement}?!",
    "⚠️ {statement} - STOP SEKARANG!",
    "❌ {statement} - Yang Ini Jangan Dilakuin!",
    "✅ {statement} - Rahasia Yang Gak Ada Yang Tahu!",
    "🔥 {statement} - Gak Disangka!",
    "💡 {statement} - Auto Jadi Jago!",
    "😱 {statement} -Jangan Sampai Terjadi!",
    "🎯 {statement} - Auto Berubah!",
]

# Content templates per niche
CONTENT_TEMPLATES = {
    "Teknologi & Gadget": [
        {
            "statement": "HP kamu tiba-tiba panas sendiri? Battery cepat habis?",
            "problem": "HP kamu udah disadap!",
            "tips": ["Factory reset HP", "Download dari Play Store resmi", "Jangan klik link mencurigakan", "Update sistem operasi rutin", "Install antivirus"],
            "cta": "Share ke teman yang suka install aplikasi abal-abal!"
        },
        {
            "statement": "WiFi gratisan? Hati-hati bisa dibobol!",
            "problem": "Data pribadi kamu berisiko dicuri!",
            "tips": ["Jangan gunakan WiFi publik untuk banking", "Gunakan VPN", "Matikan auto-connect WiFi", "Pastikan URL HTTPS", "Jangan bagikan data pribadi"],
            "cta": "Tag teman yang suka connect WiFi sembarangan!"
        },
    ],
    "Tips Kesehatan & Fitness": [
        {
            "statement": "Mau sixpack tapi males gym?",
            "problem": "Ini yang selama ini kamu salah!",
            "tips": ["Plank 3x30 detik", "Crunches 3x20", "Russian twist 3x15", "Diet protein tinggi", "Minum air putih 2 liter"],
            "cta": "Lakukan setiap pagi - hasil dalam 30 hari!"
        },
        {
            "statement": "Sleep timer HP rusak? Gak bisa tidur?",
            "problem": "Ini efek blue light yang kamu rasakan!",
            "tips": ["Matikan HP 30 menit sebelum tidur", "Gunakan night mode", "Baca buku sebelum tidur", "Oleskan minyak kayu putih", "Tidur jam 10 malam"],
            "cta": "Coba mulai malam ini!"
        },
    ],
    "Keuangan & Investasi": [
        {
            "statement": "Gaji 5 juta tapi mau jadi kaya?",
            "problem": "Ini kesalahan fatal anak muda!",
            "tips": ["Tabung 20% dari gaji", "Hindari impulsive buying", "Investasi reksadana", "Bikin emergency fund 3 bulan", "Belajar finansial literacy"],
            "cta": "Mulai tabung hari ini - masa depanmu tergantung ini!"
        },
        {
            "statement": "Piutang teman belum dibayar?",
            "problem": "Ini cara aman minta uang balik!",
            "tips": ["Kirim invoice", "Tentukan deadline jelas", "Gunakan aplikasi peminjaman", "Jangan awkward - uang kamu", "Document everything"],
            "cta": "Share ke teman yang suka kredit perut!"
        },
    ],
    "Masakan & Resep": [
        {
            "statement": "Mie instan itu poison?",
            "problem": "Ini cara aman makan mie instan!",
            "tips": ["Jangan masak dengan plastik", "Tuang air panas pertama", "Tambahkan telur & sayur", "Batasi 1x seminggu", "Pilih yang low sodium"],
            "cta": "Steal resep ini dan share ke ibu-ibu!"
        },
        {
            "statement": "Nasi goreng biasa itu mainstream?",
            "problem": "Cobain resep ini auto jadi chef!",
            "tips": ["Gunakan beras dingin", "Bawang putih 3 siung", "Kecap manis - kunci utama", "Saus tiram 1 sdm", "Topping telur mata sapi"],
            "cta": "Masak sekarang dan post ke story!"
        },
    ],
    "Motivasi & Produktivitas": [
        {
            "statement": "Malas terus? Gak ada motivasi?",
            "problem": "Ini 5 hal yang bikin kamu malas terus!",
            "tips": ["Tidur cukup 7-8 jam", "Morning routine 15 menit", "To-do list malam sebelumnya", "Hindari social media pagi", "Celebrate small wins"],
            "cta": "Follow untuk tips produktivitas setiap hari!"
        },
        {
            "statement": "Overthinking menghantui?",
            "problem": "Ini teknik grounding yang work!",
            "tips": ["5-4-3-2-1 technique", "Journaling setiap malam", "Meditasi 5 menit", "Positive affirmation", "Action over perfection"],
            "cta": "Save ini untuk moments yang susah!"
        },
    ],
    "Gaming": [
        {
            "statement": "Rank masih Bronze? Auto Jadi Pro!",
            "problem": "Ini setting yang selama ini kamu salah!",
            "tips": ["Sensitivity 5-8%", "Headphone bukan speaker", "Check mini map setiap 3 detik", "Learn combo skill", "Play 3 rank games per day"],
            "cta": "Share ke teman yang rank nya mentok!"
        },
        {
            "statement": "HP lag pas main game?",
            "problem": "Ini 5 setting yang harus dimatiin!",
            "tips": ["Game mode ON", "Clear RAM sebelum main", "Matikan background apps", "Lower graphics setting", "WiFi 5GHz bukan 2.4GHz"],
            "cta": "Kasih tau squad kamu!"
        },
    ],
    "Fashion & Gaya Hidup": [
        {
            "statement": "Baju sama dengan orang lain? Awkward!",
            "problem": "Ini cara mix-match yang auto standout!",
            "tips": ["Neutrals + 1 statement piece", "Layering basics", "Accessorize minimal", "Color wheel combo", "Tailored fit selalu menang"],
            "cta": "Cobain dan tag @ outfit kamu!"
        },
        {
            "statement": "Parfum cheap = bau murah?",
            "problem": "Ini cara pilih parfum yang richt!",
            "tips": ["Test on skin bukan paper", "Check longevity 6-8 jam", "Notes: citrus fresh, woody sensual", "Spray di titik nadi", "Jangan gosok setelah spray"],
            "cta": "Share ke cowok yang bau nya nista!"
        },
    ],
    "Berita & Event Trending": [
        {
            "statement": "Viral baru ternyata hoax?",
            "problem": "Ini cara bedakan berita nyata dan hoax!",
            "tips": ["Cek sumber resmi", "Cek tanggal berita", "Cross check 3 sumber", "Jangan share langsung", "Fact check di Turn Back Hoax"],
            "cta": "Forward ke grup keluarga yang suka share hoax!"
        },
        {
            "statement": "Event trending yang gak boleh kelewatan?",
            "problem": "Ini cara dapat ticket lebih murah!",
            "tips": ["Early bird discount", "Use promo code", "Group booking discount", "Follow social media organizer", "Wait for last minute deals"],
            "cta": "Bookmark dan share ke temen kamu!"
        },
    ]
}


class YouTubeShortsGenerator:
    def __init__(self):
        self.niches = NICHES
        self.templates = CONTENT_TEMPLATES
        self.used_topics = set()
        self.current_niche_index = 0
    
    def get_next_niche(self) -> Dict:
        """Get next niche that hasn't been used recently"""
        niche = self.niches[self.current_niche_index]
        self.current_niche_index = (self.current_niche_index + 1) % len(self.niches)
        return niche
    
    def generate_hook(self, statement: str) -> str:
        """Generate attention-grabbing hook"""
        template = random.choice(HOOK_TEMPLATES)
        return template.format(statement=statement)
    
    def create_content_segment(self, text: str, index: int, niche: Dict) -> Dict:
        """Create a content segment with B-roll, text overlay, and SFX"""
        return {
            "timestamp_range": f"00:{index * 5:02d} - 00:{index * 5 + 5:02d}" if index * 5 < 60 else f"01:{index * 5 - 60:02d} - 01:{index * 5 + 5 - 60:02d}",
            "voiceover": text,
            "visual_broll": f"Engaging visuals related to: {text[:50]}...",
            "text_overlay": text[:30] + "..." if len(text) > 30 else text,
            "audio_sfx": self.get_sfx_cue(text)
        }
    
    def get_sfx_cue(self, text: str) -> str:
        """Get appropriate SFX cue based on content"""
        sfx_map = {
            "WARNING": "alert sound + suspenseful bass",
            "TIP": "success chime + positive ding",
            "QUESTION": "suspense tone + whoosh",
            "CTA": "call-to-action jingle + share sound"
        }
        
        text_lower = text.lower()
        if any(w in text_lower for w in ["hati-hati", "awas", "jangan", "stop", "bahaya", "🚨", "⚠️"]):
            return sfx_map["WARNING"]
        elif any(w in text_lower for w in ["tips", "cara", "solusi", "✅", "💡"]):
            return sfx_map["TIP"]
        elif any(w in text_lower for w in ["?", "kenapa", "apa", "siapa"]):
            return sfx_map["QUESTION"]
        elif any(w in text_lower for w in ["share", "tag", "follow", "subscribe", "save"]):
            return sfx_map["CTA"]
        return "transition sound effect"
    
    def generate_script(self, niche: str = None) -> Dict:
        """Generate complete YouTube Shorts script"""
        if niche:
            selected_niche = next((n for n in self.niches if n["name"] == niche), self.get_next_niche())
        else:
            selected_niche = self.get_next_niche()
        
        niche_templates = self.templates.get(selected_niche["name"], self.templates["Teknologi & Gadget"])
        template = random.choice(niche_templates)
        
        content_segments = []
        
        # Hook segment (0-5 seconds)
        hook_text = f"{template['statement']} {template['problem']}"
        content_segments.append(self.create_content_segment(hook_text, 0, selected_niche))
        
        # Problem explanation (5-15 seconds)
        problem_text = template['problem']
        content_segments.append(self.create_content_segment(problem_text, 1, selected_niche))
        
        # Tips (15-35 seconds) - 5 tips, 4 seconds each
        for i, tip in enumerate(template['tips'][:4], start=3):
            content_segments.append(self.create_content_segment(f"TIPS #{i-2}: {tip}", i, selected_niche))
        
        # CTA + Loop (35-40 seconds)
        cta_text = f"{template['cta']} {template['statement']} {template['problem']}"
        content_segments.append(self.create_content_segment(cta_text, 7, selected_niche))
        
        # Generate metadata
        title = f"{random.choice(['🚨', '⚠️', '❌', '✅', '🔥', '💡', '😱', '🎯'])} {template['statement'][:45]}!"
        
        script = {
            "timestamp": datetime.now().isoformat(),
            "meta": {
                "topic": selected_niche["name"],
                "target_audience": selected_niche["audience"],
                "seo_keywords": selected_niche["keywords"] + [template["statement"].split()[0]]
            },
            "youtube_metadata": {
                "title": title,
                "description": f"{template['statement']} {template['problem']}\n\n{template['cta']}\n\n#{selected_niche['name'].replace(' ', '')} #Indonesia #Viral #Shorts",
                "tags": selected_niche["keywords"] + ["indonesia", "viral", "shorts", "trending2026"]
            },
            "content": content_segments
        }
        
        self.used_topics.add(selected_niche["name"])
        return script
    
    def generate_all_niches(self) -> List[Dict]:
        """Generate scripts for all niches"""
        return [self.generate_script() for _ in range(len(self.niches))]
    
    def save_script(self, script: Dict, filename: str = None):
        """Save script to JSON file"""
        if not filename:
            filename = f"shorts_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(f"scripts/{filename}", "w", encoding="utf-8") as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        
        return filename


def main():
    """Main execution - Generate YouTube Shorts script"""
    generator = YouTubeShortsGenerator()
    
    print("🎬 YouTube Shorts Generator - Bahasa Indonesia")
    print("=" * 50)
    
    # Generate script for next niche
    script = generator.generate_script()
    
    print(f"\n📌 Topic: {script['meta']['topic']}")
    print(f"📝 Title: {script['youtube_metadata']['title']}")
    print(f"⏱️ Duration: ~40 seconds")
    print("\n📄 Full Script:")
    print(json.dumps(script, ensure_ascii=False, indent=2))
    
    # Save to file
    filename = generator.save_script(script)
    print(f"\n✅ Script saved to: scripts/{filename}")
    
    return script


if __name__ == "__main__":
    main()
