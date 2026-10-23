#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Extra's Academy Survival Guide - Chapter Downloader
Script สำหรับดาวน์โหลดนิยาย The Extra's Academy Survival Guide รายตอนจาก WordPress
บันทึกใส่โฟลเดอร์ eng เป็นไฟล์ Markdown (.md) เรียงตามลำดับตอน และตั้งชื่อไฟล์ตามชื่อตอนในลิงก์
"""

import os
import sys
import re
import html
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import List, Dict, Optional
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

# ปรับ stdout ให้รองรับ UTF-8 บน Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ค่าคงที่เริ่มต้น
SITE_DOMAIN = "bettertranslation9.wordpress.com"
TOC_SLUG = "the-extras-academy-survival-guide-novel-english-translation"
DEFAULT_OUTPUT_DIR = "eng"
DEFAULT_WORKERS = 5

print_lock = Lock()


def safe_print(*args, **kwargs):
    """พิมพ์ข้อความแบบ Thread-safe"""
    with print_lock:
        print(*args, **kwargs)


def sanitize_filename(name: str) -> str:
    """
    ทำความสะอาดชื่อไฟล์ให้สามารถบันทึกบนระบบปฏิบัติการ Windows/Linux/macOS ได้อย่างถูกต้อง
    - แปลง HTML Entities เช่น &#8217; เป็น '
    - แปลง Smart quotes และ Dashes เป็น ASCII
    - แทนที่เครื่องหมายที่ไม่ได้รับอนุญาต เช่น : เป็น -
    - ลบอักขระต้องห้าม < > : " / \\ | ? *
    """
    name = html.unescape(name)
    name = name.replace('’', "'").replace('‘', "'")
    name = name.replace('“', '"').replace('”', '"')
    name = name.replace('–', '-').replace('—', '-')
    # แทนที่ colon ด้วย dash
    name = re.sub(r'\s*:\s*', ' - ', name)
    # ลบอักขระต้องห้ามของ Windows
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # ยุบช่องว่างซ้ำซ้อน
    name = re.sub(r'\s+', ' ', name).strip()
    # ตัดจุดหรือช่องว่างท้ายชื่อไฟล์
    return name.rstrip('. ')


def simplify_title(full_title: str) -> str:
    """
    ตัดชื่อเรื่องนำหน้าออกเพื่อให้ได้ชื่อตอนที่กระชับ เช่น
    'The Extra’s Academy Survival Guide Chapter 1: Prologue' -> 'Chapter 1: Prologue'
    'The Extra’s Academy Survival Guide – Side Story 1: Wind Flower (1)' -> 'Side Story 1: Wind Flower (1)'
    """
    clean = re.sub(r"^The Extra['’]s Academy Survival Guide\s*[-–—]?\s*", "", full_title, flags=re.IGNORECASE)
    return clean.strip()


def clean_chapter_content_to_md(content_html: str) -> str:
    """
    สกัดและแปลงเนื้อหานิยายจาก HTML เป็น Markdown (.md):
    - ลบแท็ก script, style, form, iframe
    - แปลงแท็กตัวหนา (<strong>, <b>) เป็น **bold**
    - แปลงแท็กตัวเอียง (<em>, <i>) เป็น *italic*
    - แปลง blockquote และหัวข้อระดับต่างๆ (h1-h6)
    - ตัดปุ่มนำทางท้ายหน้าเว็บ (Next Chapter / Previous Chapter / Index)
    - คืนค่าเป็นข้อความ Markdown จัดย่อหน้าอย่างสวยงาม
    """
    soup = BeautifulSoup(content_html, 'html.parser')
    for tag in soup(['script', 'style', 'form', 'iframe', 'noscript']):
        tag.decompose()

    paragraphs = []
    elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'hr'])

    for el in elements:
        if el.name == 'hr':
            paragraphs.append('---')
            continue

        text_check = el.get_text().strip()
        if not text_check:
            continue

        # ตรวจสอบและตัดปุ่ม Navigation ท้ายหน้า
        lower_t = text_check.lower()
        if ('index' in lower_t or 'next chapter' in lower_t or 'previous chapter' in lower_t) and \
           any(sym in text_check for sym in ['↑', '←', '→', '|']):
            continue

        # แปลงตัวหนา (bold)
        for strong in el.find_all(['strong', 'b']):
            t = strong.get_text()
            if t:
                strong.replace_with(f"**{t}**")
            else:
                strong.decompose()

        # แปลงตัวเอียง (italic)
        for em in el.find_all(['em', 'i']):
            t = em.get_text()
            if t:
                em.replace_with(f"*{t}*")
            else:
                em.decompose()

        text = el.get_text().strip()
        if not text:
            continue

        if el.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(el.name[1])
            prefix = '#' * min(level + 1, 6)
            paragraphs.append(f"{prefix} {text}")
        elif el.name == 'blockquote':
            quoted = '\n'.join(f"> {line}" for line in text.split('\n'))
            paragraphs.append(quoted)
        else:
            paragraphs.append(text)

    # ตัด separator ท้ายสุดหากมี
    while paragraphs and paragraphs[-1] in ('---', ''):
        paragraphs.pop()

    return '\n\n'.join(paragraphs)


def fetch_chapter_list(session: requests.Session) -> List[Dict]:
    """
    ดึงรายชื่อตอนทั้งหมดจากสารบัญ (TOC) ผ่าน WordPress REST API
    """
    url = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE_DOMAIN}/posts/slug:{TOC_SLUG}"
    safe_print(f"[*] กำลังดึงสารบัญนิยายจาก: {url}")

    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    content_html = data.get('content', '')
    soup = BeautifulSoup(content_html, 'html.parser')

    raw_links = []
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True)
        href = a['href'].strip()

        # กรองเฉพาะลิงก์ที่เป็นตอนของนิยาย
        lower_h = href.lower()
        lower_t = text.lower()
        if any(k in lower_h or k in lower_t for k in ['chapter', 'side-story', 'side story', 'prologue', 'epilogue']):
            raw_links.append((text, href))

    # บนหน้าเว็บแสดงตอนใหม่อยู่บนสุด จึงต้องกลับลำดับ (reverse)
    # เพื่อให้ตอนที่ 1 (Prologue) อยู่ลำดับแรกสุด
    raw_links.reverse()

    chapters = []
    for idx, (title, href) in enumerate(raw_links, start=1):
        slug = href.rstrip('/').split('/')[-1]
        chapters.append({
            'index': idx,
            'title': title,
            'url': href,
            'slug': slug
        })

    safe_print(f"[+] พบทั้งหมด {len(chapters)} ตอน")
    return chapters


def download_chapter(session: requests.Session, chapter: Dict, output_dir: str, 
                     use_full_title: bool = True, force: bool = False, ext: str = "md") -> bool:
    """
    ดาวน์โหลดและบันทึกตอนนิยายเป็นไฟล์ Markdown (.md)
    """
    idx = chapter['index']
    title_text = chapter['title'] if use_full_title else simplify_title(chapter['title'])
    safe_name = sanitize_filename(title_text)
    filename = f"{idx:03d} - {safe_name}.{ext}"
    filepath = os.path.join(output_dir, filename)

    # ข้ามถ้ามีไฟล์อยู่แล้ว และไม่ได้เปิดโหมด force
    if not force and os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        safe_print(f"[=] [{idx:03d}] ข้าม (มีไฟล์อยู่แล้ว): {filename}")
        return True

    api_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE_DOMAIN}/posts/slug:{chapter['slug']}"

    for attempt in range(1, 4):
        try:
            resp = session.get(api_url, timeout=15)
            if resp.status_code == 200:
                post_data = resp.json()
                raw_content = post_data.get('content', '')
                post_title = html.unescape(post_data.get('title', chapter['title']))

                body_text = clean_chapter_content_to_md(raw_content)

                # จัดรูปแบบเนื้อหา Markdown พร้อม Header ที่สวยงาม
                file_content = (
                    f"# {post_title}\n\n"
                    f"- **Source:** [{chapter['url']}]({chapter['url']})\n"
                    f"- **Chapter Index:** {idx}\n\n"
                    f"---\n\n"
                    f"{body_text}\n"
                )

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(file_content)

                safe_print(f"[✓] [{idx:03d}] ดาวน์โหลดเสร็จสิ้น: {filename}")
                return True
            else:
                safe_print(f"[!] [{idx:03d}] ข้อผิดพลาด HTTP {resp.status_code} สำหรับตอน {chapter['slug']} (ครั้งที่ {attempt}/3)")
        except Exception as e:
            safe_print(f"[!] [{idx:03d}] ล้มเหลว: {e} (ครั้งที่ {attempt}/3)")

        time.sleep(1.0 * attempt)

    safe_print(f"[✗] [{idx:03d}] ไม่สามารถดาวน์โหลดได้: {filename}")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Download 'The Extra's Academy Survival Guide' chapters to a folder as Markdown (.md) files."
    )
    parser.add_argument(
        '--folder', '-f', default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save chapter files (default: '{DEFAULT_OUTPUT_DIR}')"
    )
    parser.add_argument(
        '--workers', '-w', type=int, default=DEFAULT_WORKERS,
        help=f"Number of concurrent download threads (default: {DEFAULT_WORKERS})"
    )
    parser.add_argument(
        '--format', choices=['md', 'txt'], default='md',
        help="File format to save: 'md' (default) or 'txt'"
    )
    parser.add_argument(
        '--short-name', action='store_true',
        help="Use shortened filename (e.g., '001 - Chapter 1 - Prologue.md' instead of full series name)"
    )
    parser.add_argument(
        '--force', action='store_true',
        help="Force re-download even if file already exists"
    )
    parser.add_argument(
        '--limit', type=int, default=None,
        help="Limit download to first N chapters (for testing)"
    )
    args = parser.parse_args()

    output_dir = args.folder
    os.makedirs(output_dir, exist_ok=True)

    use_full_title = not args.short_name
    ext = args.format
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    safe_print("=" * 65)
    safe_print("  The Extra's Academy Survival Guide - Chapter Downloader")
    safe_print(f"  เป้าหมาย: โฟลเดอร์ '{output_dir}'")
    safe_print(f"  รูปแบบไฟล์: .{ext}")
    safe_print(f"  จำนวน Threads: {args.workers}")
    safe_print(f"  รูปแบบชื่อไฟล์: {'ชื่อเต็มตามลิงก์' if use_full_title else 'ชื่อย่อเฉพาะตอน'}")
    safe_print("=" * 65)

    chapters = fetch_chapter_list(session)
    if args.limit and args.limit > 0:
        chapters = chapters[:args.limit]
        safe_print(f"[*] จำกัดการดาวน์โหลดเฉพาะ {args.limit} ตอนแรกตามคำสั่ง")

    # บันทึกไฟล์สารบัญรวม (000_Index.md)
    index_file = os.path.join(output_dir, f"000_Index.{ext}")
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# The Extra's Academy Survival Guide - Table of Contents\n\n")
        f.write("| # | Chapter Title | Local File | Source Link |\n")
        f.write("|---|---|---|---|\n")
        for ch in chapters:
            t = ch['title'] if use_full_title else simplify_title(ch['title'])
            sname = sanitize_filename(t)
            fname = f"{ch['index']:03d} - {sname}.{ext}"
            file_link = f"[{fname}](./{quote(fname)})"
            f.write(f"| {ch['index']:03d} | {ch['title']} | {file_link} | [Online Link]({ch['url']}) |\n")
    safe_print(f"[+] สร้างไฟล์สารบัญ: {index_file}")

    safe_print(f"[*] เริ่มต้นดาวน์โหลดทั้งหมด {len(chapters)} ตอน...")
    start_time = time.time()
    success_count = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                download_chapter, session, ch, output_dir, use_full_title, args.force, ext
            ): ch for ch in chapters
        }

        for future in as_completed(futures):
            if future.result():
                success_count += 1

    elapsed = time.time() - start_time
    safe_print("=" * 65)
    safe_print("[✓] ดาวน์โหลดเสร็จสิ้น!")
    safe_print(f"  - สำเร็จ: {success_count}/{len(chapters)} ตอน")
    safe_print(f"  - เวลาที่ใช้: {elapsed:.2f} วินาที")
    safe_print(f"  - ที่อยู่โฟลเดอร์: {os.path.abspath(output_dir)}")
    safe_print("=" * 65)


if __name__ == '__main__':
    main()