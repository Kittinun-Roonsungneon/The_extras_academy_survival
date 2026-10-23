# The Extra's Academy Survival Guide - Chapter Downloader

สคริปต์ภาษา Python สำหรับดาวน์โหลดนิยายเรื่อง **The Extra’s Academy Survival Guide** รายตอนจากบล็อก BetterTranslation บันทึกใส่โฟลเดอร์ `eng` เป็นไฟล์ **Markdown (.md)** โดยเรียงลำดับตามตอน และตั้งชื่อไฟล์ตามชื่อตอนในลิงก์สารบัญ

---

## 📁 โครงสร้างไฟล์

```text
The_extras_academy_survival/
│
├── download_novel.py      # สคริปต์หลักสำหรับดาวน์โหลด (บันทึกเป็น .md โดยอัตโนมัติ)
├── requirements.txt       # รายการ Library ที่จำเป็น (requests, beautifulsoup4)
├── run.bat                # ไฟล์ Double-click เพื่อรันบน Windows ได้ทันที
├── README.md              # คำอธิบายการใช้งาน
│
└── eng/                   # โฟลเดอร์เก็บไฟล์นิยายรายตอน (.md)
    ├── 000_Index.md       # สารบัญรวมทุกตอน พร้อมลิงก์เปิดไฟล์และลิงก์ต้นฉบับ
    ├── 001 - The Extra's Academy Survival Guide Chapter 1 - Prologue.md
    ├── 002 - The Extra's Academy Survival Guide Chapter 2 - 10 Days Before School Starts.md
    ├── ...
    ├── 250 - The Extra's Academy Survival Guide Chapter 250 - Epilogue (3).md
    ├── 251 - The Extra's Academy Survival Guide - Side Story 0 - Postscript.md
    ├── ...
    └── 299 - The Extra's Academy Survival Guide - Side Story 48 - A Proud Maid (10).md
```

---

## 🚀 วิธีใช้งาน

### วิธีที่ 1: ดับเบิลคลิก `run.bat` (สะดวกที่สุด)
- ดับเบิลคลิกที่ไฟล์ `run.bat`
- สคริปต์จะค้นหา Python ในเครื่อง ติดตั้ง Library ที่จำเป็น และเริ่มดาวน์โหลดให้อัตโนมัติ

### วิธีที่ 2: รันผ่าน Terminal / Command Line
```powershell
# 1. ติดตั้ง Library ที่จำเป็น
pip install -r requirements.txt

# 2. รันสคริปต์ดาวน์โหลดทั้งหมดเป็นไฟล์ .md
python download_novel.py
```

---

## ⚙️ ตัวเลือกคำสั่งเพิ่มเติม (Command-Line Options)

| ตัวเลือก | คำสั่งย่อ | ค่าเริ่มต้น | คำอธิบาย |
|---|---|---|---|
| `--format` | | `md` | รูปแบบไฟล์ที่ต้องการบันทึก (`md` หรือ `txt`) |
| `--folder` | `-f` | `eng` | กำหนดโฟลเดอร์ปลายทางที่ใช้บันทึกไฟล์ |
| `--workers` | `-w` | `5` | จำนวน Threads ในการดาวน์โหลดพร้อมกัน |
| `--short-name` | | ปิด | บันทึกชื่อไฟล์แบบสั้น (ตัดชื่อเรื่องนำหน้าออก เหลือเฉพาะ `001 - Chapter 1 - Prologue.md`) |
| `--force` | | ปิด | บังคับดาวน์โหลดใหม่ทับไฟล์เดิม แม้จะมีไฟล์อยู่แล้ว |
| `--limit` | | ทั้งหมด | จำกัดจำนวนตอนที่ต้องการดาวน์โหลด (เหมาะสำหรับทดสอบ) |

### ตัวอย่างการรันแบบกำหนดตัวเลือก:
```powershell
# บันทึกเป็น .md ด้วยชื่อไฟล์สั้น
python download_novel.py --short-name

# ดาวน์โหลดด้วยความเร็ว 10 Threads
python download_novel.py --workers 10

# หากต้องการบันทึกเป็น .txt แบบเดิม
python download_novel.py --format txt

# ทดสอบดาวน์โหลดเฉพาะ 5 ตอนแรก
python download_novel.py --limit 5
```

---

## ✨ จุดเด่นของการบันทึกเป็น Markdown (.md)
1. **จัดรูปแบบสมบูรณ์แบบ**: รองรับตัวหนา (`**bold**`), ตัวเอียง (`*italic*`), หัวข้อ และย่อหน้าอย่างสวยงาม
2. **เปิดอ่านสะดวก**: รองรับโปรแกรมอ่าน Markdown ทุกประเภท เช่น Obsidian, Typora, VS Code, GitHub
3. **สารบัญแบบคลิกได้ (`000_Index.md`)**: มีตารางสารบัญพร้อม Markdown Link ที่สามารถคลิกเปิดแต่ละตอนในโปรแกรมได้ทันที
4. **ดึงข้อมูลผ่าน Official REST API**: ไม่โดน Cloudflare / Bot Protection บล็อก
5. **Resume อัตโนมัติ**: ข้ามตอนที่โหลดเสร็จแล้วอัตโนมัติหากรันซ้ำ