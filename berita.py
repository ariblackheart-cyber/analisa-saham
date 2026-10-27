"""Ambil berita dari feed RSS di feeds.txt dan simpan ke Supabase (tabel saham_berita).

Pencarian dengan kata kunci dilakukan di database (fungsi saham_cari_berita) dan di dashboard.
Berita lebih tua dari SIMPAN_HARI dihapus.

    python berita.py                 # ambil semua feed, simpan ke Supabase
    python berita.py --file a.xml    # uji: baca file RSS lokal, tampilkan hasil tanpa menyimpan
"""
import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

import db

ROOT = Path(__file__).parent
SIMPAN_HARI = 30
UA = "analisa-saham/1.0 (+https://github.com/ariblackheart-cyber/analisa-saham)"


def bersih(teks: str | None, maks: int = 300) -> str:
    t = html.unescape(re.sub(r"<[^>]+>", " ", teks or ""))
    t = re.sub(r"\s+", " ", t).strip()
    return t[:maks].rstrip() + ("…" if len(t) > maks else "")


def waktu(s: str | None):
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s.strip())
        return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).isoformat()
    except Exception:
        return None


def baca_rss(xml_teks: str, url: str) -> list[dict]:
    """Parse RSS 2.0. Jika XML rusak/terpotong, ambil blok <item> yang utuh dengan regex."""
    items, nama = [], None
    try:
        root = ET.fromstring(xml_teks)
        ch = root.find("channel")
        nama = (ch.findtext("title") if ch is not None else None)
        for it in root.iter("item"):
            items.append({k: it.findtext(k) for k in ("title", "link", "description", "pubDate", "guid")})
    except ET.ParseError:
        m = re.search(r"<channel>.*?<title>(.*?)</title>", xml_teks, re.S)
        nama = m.group(1) if m else None
        for blok in re.findall(r"<item>(.*?)</item>", xml_teks, re.S):
            def tag(t):
                m = re.search(rf"<{t}[^>]*>(.*?)</{t}>", blok, re.S)
                return re.sub(r"^<!\[CDATA\[|\]\]>$", "", m.group(1).strip()) if m else None
            items.append({k: tag(k) for k in ("title", "link", "description", "pubDate", "guid")})
    nama = bersih(re.sub(r"^<!\[CDATA\[|\]\]>$", "", nama or ""), 60) or re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    hasil = []
    for it in items:
        link = (it.get("link") or it.get("guid") or "").strip()
        judul = bersih(it.get("title"), 300)
        if not link.startswith("http") or not judul:
            continue
        hasil.append(dict(link=link, judul=judul, ringkasan=bersih(it.get("description")),
                          sumber=nama, terbit=waktu(it.get("pubDate"))))
    return hasil


def baca_feeds() -> list[str]:
    return [s.strip() for s in (ROOT / "feeds.txt").read_text().splitlines()
            if s.strip() and not s.strip().startswith("#")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="uji dengan file RSS lokal")
    a = ap.parse_args()
    if a.file:
        hasil = baca_rss(Path(a.file).read_text(encoding="utf-8", errors="replace"), a.file)
        for h in hasil[:5]:
            print(h["terbit"], "|", h["sumber"], "|", h["judul"])
        print(f"{len(hasil)} berita terbaca.")
        return
    semua, gagal = {}, []
    for url in baca_feeds():
        try:
            r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml"}, timeout=30)
            r.raise_for_status()
            hasil = baca_rss(r.text, url)
            for h in hasil:
                semua[h["link"]] = h
            print(f"::notice title=Feed OK::{url}: HTTP {r.status_code}, {len(r.content)} byte, {len(hasil)} berita")
        except requests.HTTPError as e:
            gagal.append(url)
            print(f"::warning title=Feed gagal::{url}: HTTP {e.response.status_code}")
        except Exception as e:
            gagal.append(url)
            print(f"::warning title=Feed gagal::{url}: {type(e).__name__}: {str(e)[:150]}")
    if not db.aktif():
        sys.exit("SUPABASE_URL / SUPABASE_SERVICE_KEY belum diisi.")
    sb = db.Supabase()
    if semua:
        sb.upsert("saham_berita", list(semua.values()), "link")
    batas = (datetime.now(timezone.utc) - timedelta(days=SIMPAN_HARI)).isoformat()
    sb.hapus("saham_berita", {"terbit": f"lt.{batas}"})
    print(f"Tersimpan {len(semua)} berita. Feed gagal: {len(gagal)}.")
    if gagal and not semua:
        sys.exit(1)


if __name__ == "__main__":
    main()
