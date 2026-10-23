# -*- coding: utf-8 -*-
"""
The Extra's Academy Survival Guide - Markdown to TXT Converter
สคริปต์แปลงไฟล์ .md ในโฟลเดอร์ TH เป็นไฟล์ .txt บันทึกไว้ในโฟลเดอร์ TH/txt/
โดยตั้งชื่อไฟล์ตามชื่อไฟล์ต้นฉบับ: {ชื่อไฟล์เดิม}.txt
"""

import os
import sys
import re
import argparse
from typing import List, Tuple

# ตั้งค่า stdout สำหรับ Windows เพื่อรองรับภาษาไทย
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_INPUT_DIR = "TH"
DEFAULT_OUTPUT_DIR = os.path.join("TH", "txt")


def clean_markdown_text(content: str, strip_header: bool = False) -> str:
    """
    แปลงเนื้อหา Markdown ให้เป็นข้อความ Text ล้วนที่อ่านง่าย สบายตา
    - ลบเครื่องหมายหัวข้อ (#, ##, ...)
    - ลบตัวหนา/ตัวเอียง (**, *, __, _)
    - ลบ code backticks (`)
    - จัดรูปแบบเส้นคั่นหน้า (---)
    - (ทางเลือก) ลบกล่องข้อมูลหัวเรื่อง (metadata) เช่น ชื่อเรื่อง, ตอนที่, ไฟล์ต้นฉบับ
    """
    lines = content.splitlines()

    # ถ้าเลือกตัด header metadata ออก
    if strip_header:
        filtered_lines = []
        found_divider = False

        for i, line in enumerate(lines):
            # เก็บหัวข้อหลักบรรทัดแรกไว้ (เช่น # Chapter 1 : บทนำ ...)
            if i == 0 and line.startswith('#'):
                filtered_lines.append(line)
                continue

            # ตรวจสอบเส้นคั่น ---
            if re.match(r'^\s*[-*_]{3,}\s*$', line):
                found_divider = True
                continue

            # หากยังไม่เจอเส้นคั่น และเป็นรายการ metadata (- **ชื่อเรื่อง:** ...)
            if not found_divider:
                if line.strip().startswith('-') or line.strip() == '':
                    continue

            filtered_lines.append(line)
        lines = filtered_lines

    cleaned_lines = []
    for line in lines:
        cleaned = line

        # 1. ลบเครื่องหมาย Header เช่น #, ##, ### ด้านหน้าบรรทัด
        cleaned = re.sub(r'^#{1,6}\s*', '', cleaned)

        # 2. ลบตัวหนา + ตัวเอียง (***text***, ___text___)
        cleaned = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', cleaned)
        cleaned = re.sub(r'___(.*?)___', r'\1', cleaned)

        # 3. ลบตัวหนา (**text**, __text__)
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
        cleaned = re.sub(r'__(.*?)__', r'\1', cleaned)

        # 4. ลบตัวเอียง (*text*, _text_)
        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
        cleaned = re.sub(r'_(.*?)_', r'\1', cleaned)

        # 5. ลบ inline code (`code`)
        cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)

        # 6. ลบ blockquote (> text)
        cleaned = re.sub(r'^>\s?', '', cleaned)

        # 7. เส้นคั่นแนวนอน (--- หรือ *** หรือ ****) แปลงเป็นเส้นประอ่านง่าย
        if re.match(r'^\s*[-*_]{3,}\s*$', line):
            cleaned = "--------------------------------------------------"

        cleaned_lines.append(cleaned)

    # รวมบรรทัดกลับเข้าด้วยกัน
    result = '\n'.join(cleaned_lines)

    # ตัดช่องว่างซ้ำซ้อนท้ายไฟล์
    return result.strip() + '\n'


def convert_files(input_dir: str = DEFAULT_INPUT_DIR,
                  output_dir: str = DEFAULT_OUTPUT_DIR,
                  mode: str = "clean",
                  strip_header: bool = False,
                  overwrite: bool = True) -> Tuple[int, int, List[str]]:
    """
    ค้นหาไฟล์ .md ใน input_dir และแปลงเป็น .txt บันทึกใน output_dir
    """
    if not os.path.exists(input_dir):
        print(f"[ERROR] ไม่พบโฟลเดอร์ต้นทาง: '{input_dir}'")
        return 0, 0, []

    # สร้างโฟลเดอร์ผลลัพธ์ (เช่น TH/txt/)
    os.makedirs(output_dir, exist_ok=True)

    # ค้นหาไฟล์ .md ทั้งหมด (ไม่รวมโฟลเดอร์ย่อย)
    all_files = [f for f in os.listdir(input_dir)
                 if f.lower().endswith(".md") and os.path.isfile(os.path.join(input_dir, f))]

    # เรียงลำดับชื่อไฟล์ให้สวยงาม (พยายามเรียงตามหมายเลขตอน)
    def natural_sort_key(s: str):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', s)]

    all_files.sort(key=natural_sort_key)

    total_files = len(all_files)
    if total_files == 0:
        print(f"[!] ไม่พบไฟล์ .md ในโฟลเดอร์ '{input_dir}'")
        return 0, 0, []

    print("============================================================")
    print("  แปลงไฟล์นิยายจาก Markdown (.md) เป็น Text (.txt)")
    print("============================================================")
    print(f"[*] โฟลเดอร์ต้นทาง:   {input_dir}")
    print(f"[*] โฟลเดอร์ปลายทาง:  {output_dir}")
    print(f"[*] จำนวนไฟล์ทั้งหมด: {total_files} ไฟล์")
    print(f"[*] โหมดการแปลง:      {mode} ('ข้อความสะอาดตา ไร้สัญลักษณ์ markdown' if mode == 'clean' else 'คัดลอกเนื้อหาเดิมทุกประการ')")
    if mode == "clean":
        print(f"[*] ตัด Header เมทาดาทา: {'เปิดใช้งาน' if strip_header else 'ไม่ตัด (เก็บไว้)'}")
    print("============================================================\n")

    success_count = 0
    skip_count = 0
    errors = []

    for idx, filename in enumerate(all_files, start=1):
        in_path = os.path.join(input_dir, filename)
        
        # ตั้งชื่อไฟล์ปลายทางเป็น {ชื่อไฟล์เดิม}.txt
        base_name = os.path.splitext(filename)[0]
        out_filename = f"{base_name}.txt"
        out_path = os.path.join(output_dir, out_filename)

        if not overwrite and os.path.exists(out_path):
            skip_count += 1
            print(f"[{idx:3d}/{total_files}] (ข้าม - มีไฟล์แล้ว) {out_filename}")
            continue

        try:
            with open(in_path, "r", encoding="utf-8") as f_in:
                raw_text = f_in.read()

            if mode == "clean":
                final_text = clean_markdown_text(raw_text, strip_header=strip_header)
            else:
                final_text = raw_text

            with open(out_path, "w", encoding="utf-8") as f_out:
                f_out.write(final_text)

            success_count += 1
            print(f"[{idx:3d}/{total_files}] แปลงเรียบร้อย: {out_filename}")

        except Exception as e:
            errors.append((filename, str(e)))
            print(f"[{idx:3d}/{total_files}] [ERROR] ไม่สามารถแปลงไฟล์ {filename}: {e}")

    print("\n============================================================")
    print("[*] สรุปผลการทำงาน:")
    print(f"    - แปลงสำเร็จ:     {success_count} ไฟล์")
    if skip_count > 0:
        print(f"    - ข้าม:           {skip_count} ไฟล์")
    if errors:
        print(f"    - เกิดข้อผิดพลาด: {len(errors)} ไฟล์")
    print(f"[*] บันทึกไฟล์ทั้งหมดไว้ที่: {os.path.abspath(output_dir)}")
    print("============================================================\n")

    return success_count, skip_count, errors


def main():
    parser = argparse.ArgumentParser(
        description="แปลงไฟล์นิยาย .md ในโฟลเดอร์ TH เป็น .txt ในโฟลเดอร์ TH/txt"
    )
    parser.add_argument(
        "--input", "-i",
        default=DEFAULT_INPUT_DIR,
        help=f"โฟลเดอร์ต้นทางที่มีไฟล์ .md (ค่าเริ่มต้น: {DEFAULT_INPUT_DIR})"
    )
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"โฟลเดอร์ปลายทางสำหรับบันทึก .txt (ค่าเริ่มต้น: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["clean", "raw"],
        default="clean",
        help="โหมดการแปลง: 'clean' (ลบสัญลักษณ์ Markdown เพื่อการอ่านง่าย) หรือ 'raw' (คงเนื้อหาเดิมไว้ทุกตัวอักษร) (ค่าเริ่มต้น: clean)"
    )
    parser.add_argument(
        "--strip-header",
        action="store_true",
        help="ตัดกล่องข้อมูลด้านบน (ชื่อเรื่อง, ตอนที่, ไฟล์ต้นฉบับ) ออก เหลือเฉพาะเนื้อเรื่อง"
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="ไม่ต้องเขียนทับไฟล์ที่มีอยู่แล้ว"
    )

    args = parser.parse_args()

    convert_files(
        input_dir=args.input,
        output_dir=args.output,
        mode=args.mode,
        strip_header=args.strip_header,
        overwrite=not args.no_overwrite
    )


if __name__ == "__main__":
    main()