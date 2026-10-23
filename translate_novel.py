# -*- coding: utf-8 -*-
"""
The Extra's Academy Survival Guide - Translation Helper Script
สคริปต์ตัวช่วยสำหรับจัดการและแปลนิยายจากโฟลเดอร์ eng/ ไปยังโฟลเดอร์ TH/
ตามรูปแบบชื่อไฟล์: chapter{N} - {ชื่อตอน ไทย} ({ชื่อตอน อังกฤษ}).md
"""

import os
import sys
import re
import argparse
from typing import List, Dict, Optional

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ENG_DIR = "eng"
TH_DIR = "TH"
PROMPT_FILE = "prompt_translate.md"


def get_all_eng_chapters() -> List[Dict]:
    """ดึงรายชื่อและข้อมูลตอนทั้งหมดจากโฟลเดอร์ eng/"""
    if not os.path.exists(ENG_DIR):
        print(f"[ERROR] ไม่พบโฟลเดอร์ '{ENG_DIR}'")
        return []

    files = [f for f in os.listdir(ENG_DIR) if f.endswith(".md") and not f.startswith("000_")]
    files.sort()

    chapters = []
    for f in files:
        # ตัวอย่าง: 001 - The Extra's Academy Survival Guide Chapter 1 - Prologue.md
        # หรือ: 251 - The Extra's Academy Survival Guide - Side Story 0 - Postscript.md
        m = re.match(r"^(\d{3})\s*-\s*(.+)\.md$", f)
        if m:
            idx = int(m.group(1))
            full_title = m.group(2)
            
            # แยก Chapter / Side Story และชื่อตอน
            is_side_story = "Side Story" in full_title
            
            # หาหมายเลขตอนจริง (เช่น Chapter 1 หรือ Side Story 0)
            ch_num_match = re.search(r"(?:Chapter|Side Story)\s*(\d+)", full_title, re.IGNORECASE)
            real_ch_num = ch_num_match.group(1) if ch_num_match else str(idx)
            
            # สกัดชื่อตอนย่อย (หลังเครื่องหมาย - ตัวสุดท้าย)
            parts = full_title.split(" - ")
            sub_title = parts[-1].strip() if len(parts) > 1 else full_title

            prefix = f"side_story{real_ch_num}" if is_side_story else f"chapter{real_ch_num}"

            chapters.append({
                "index": idx,
                "filename": f,
                "prefix": prefix,
                "real_ch_num": real_ch_num,
                "is_side_story": is_side_story,
                "full_title": full_title,
                "sub_title": sub_title
            })
    return chapters


def show_status():
    """แสดงสถานะตอนที่แปลเสร็จแล้วในโฟลเดอร์ TH/"""
    os.makedirs(TH_DIR, exist_ok=True)
    eng_chapters = get_all_eng_chapters()
    th_files = os.listdir(TH_DIR)

    print("=" * 65)
    print("  The Extra's Academy Survival Guide - Translation Status")
    print("=" * 65)
    print(f"[*] จำนวนตอนต้นฉบับภาษาอังกฤษ (eng/): {len(eng_chapters)} ตอน")
    print(f"[*] จำนวนตอนที่แปลเป็นภาษาไทยแล้ว (TH/): {len(th_files)} ตอน")
    print("-" * 65)
    
    if th_files:
        print("ไฟล์ภาษาไทยที่มีอยู่แล้วใน TH/:")
        for f in sorted(th_files)[:10]:
            print(f"  [✓] {f}")
        if len(th_files) > 10:
            print(f"  ... และอีก {len(th_files) - 10} ตอน")
    else:
        print("  ยังไม่มีไฟล์แปลใน TH/")
    print("=" * 65)


def generate_prompt_for_chapter(ch_num: int):
    """สร้าง Prompt พร้อมเนื้อหาตอนที่ต้องการ สำหรับส่งให้ AI ทำการแปล"""
    eng_chapters = get_all_eng_chapters()
    target_ch = None
    for ch in eng_chapters:
        if ch["index"] == ch_num or ch["real_ch_num"] == str(ch_num):
            target_ch = ch
            break

    if not target_ch:
        print(f"[!] ไม่พบตอนที่ {ch_num}")
        return

    eng_path = os.path.join(ENG_DIR, target_ch["filename"])
    with open(eng_path, "r", encoding="utf-8") as f:
        content = f.read()

    # อ่านแม่แบบคำสั่ง
    prompt_header = ""
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_header = f.read()

    print(f"[*] เตรียมเนื้อหาสำหรับตอนที่ {ch_num}: {target_ch['filename']}")
    print(f"[*] รูปแบบชื่อไฟล์ผลลัพธ์ที่ต้องการ:")
    print(f"    TH/{target_ch['prefix']} - [ชื่อตอนภาษาไทย] ({target_ch['sub_title']}).md\n")
    print("=" * 60)
    print("--- ข้อความที่สามารถคัดลอกส่งให้ AI แปลได้ทันที ---")
    print("=" * 60)
    print(f"กรุณาแปลเนื้อหานิยายตอนต่อไปนี้เป็นภาษาไทย ตามข้อกำหนดในคู่มือ:")
    print(f"บันทึกเป็นชื่อไฟล์: {target_ch['prefix']} - [ชื่อตอนภาษาไทย] ({target_ch['sub_title']}).md")
    print(f"โฟลเดอร์: TH/\n")
    print(content)


def main():
    parser = argparse.ArgumentParser(description="Translation manager for The Extra's Academy Survival Guide")
    parser.add_argument("--status", action="store_true", help="Show translation progress status")
    parser.add_argument("--chapter", "-c", type=int, help="Output prompt & text for a specific chapter index")
    args = parser.parse_args()

    if args.chapter:
        generate_prompt_for_chapter(args.chapter)
    else:
        show_status()


if __name__ == "__main__":
    main()