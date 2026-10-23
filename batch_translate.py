# -*- coding: utf-8 -*-
import os, sys, glob, re, time, json
import urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ENG_DIR = "eng"
TH_DIR = "TH"
os.makedirs(TH_DIR, exist_ok=True)

TITLE_MAP = {
    178: ("ศึกปราบปรามเอ็ด (1)", "Ed Subjugation (1)"),
    179: ("ศึกปราบปรามเอ็ด (2)", "Ed Subjugation (2)"),
    180: ("ศึกปราบปรามเอ็ด (3)", "Ed Subjugation (3)"),
    181: ("ศึกปราบปรามเอ็ด (4)", "Ed Subjugation (4)"),
    182: ("ศึกปราบปรามเอ็ด (5)", "Ed Subjugation (5)"),
    183: ("ศึกปราบปรามเอ็ด (6)", "Ed Subjugation (6)"),
    184: ("ศึกปราบปรามเอ็ด (7)", "Ed Subjugation (7)"),
    185: ("ศึกปราบปรามเอ็ด (8)", "Ed Subjugation (8)"),
    186: ("ศึกปราบปรามเอ็ด (9)", "Ed Subjugation (9)"),
    187: ("ศึกปราบปรามเอ็ด (10)", "Ed Subjugation (10)"),
    188: ("ศึกปราบปรามเอ็ด (11)", "Ed Subjugation (11)"),
    189: ("ศึกปราบปรามเอ็ด (12)", "Ed Subjugation (12)"),
    190: ("ศึกปราบปรามเอ็ด (13)", "Ed Subjugation (13)"),
    191: ("หลังค่ำคืนอันยาวนาน (1)", "After a Long Night (1)"),
    192: ("หลังค่ำคืนอันยาวนาน (2)", "After a Long Night (2)"),
    193: ("รู้อยู่แล้วเชียวว่าต้องเป็นแบบนี้ (1)", "I Knew This Would Happen (1)"),
    194: ("รู้อยู่แล้วเชียวว่าต้องเป็นแบบนี้ (2)", "I Knew This Would Happen (2)"),
    195: ("รู้อยู่แล้วเชียวว่าต้องเป็นแบบนี้ (3)", "I Knew This Would Happen (3)"),
    196: ("รู้อยู่แล้วเชียวว่าต้องเป็นแบบนี้ (4)", "I Knew This Would Happen (4)"),
    197: ("รู้อยู่แล้วเชียวว่าต้องเป็นแบบนี้ (5)", "I Knew This Would Happen (5)"),
    198: ("ความหมายของการมีอยู่ (1)", "Having Meaning (1)"),
    199: ("ความหมายของการมีอยู่ (2)", "Having Meaning (2)"),
    200: ("ความหมายของการมีอยู่ (3)", "Having Meaning (3)")
}

GLOSSARY_REPLACE = [
    (r"\bEd Rothstaylor\b", "เอ็ด โรสเทย์เลอร์"),
    (r"\bEd\b", "เอ็ด"),
    (r"\bYennekar Palerover\b", "เยนิกา เฟลเลเวอร์"),
    (r"\bYennekar\b", "เยนิกา"),
    (r"\bYenika\b", "เยนิกา"),
    (r"\bLucy Mayreel\b", "ลูซี่ เมย์ริล"),
    (r"\bLucy\b", "ลูซี่"),
    (r"\bLortel Kehelland\b", "ลอร์เทล เคเฮล์น"),
    (r"\bLortel\b", "ลอร์เทล"),
    (r"\bPenia Elias Kroel\b", "เพเนีย เอเลียส โครเอล"),
    (r"\bPrincess Penia\b", "เจ้าหญิงเพเนีย"),
    (r"\bTaylee McLaure\b", "เทย์ลี แม็กลอร์"),
    (r"\bTaylee\b", "เทย์ลี"),
    (r"\bAyla Triss\b", "ไอรา ทริส"),
    (r"\bAyla\b", "ไอรา"),
    (r"\bClevius Nortondale\b", "คลีวิอุส นอร์ตันเดล"),
    (r"\bClevius\b", "คลีวิอุส"),
    (r"\bElvira Aniston\b", "เอลวิรา แอนิสตัน"),
    (r"\bElvira\b", "เอลวิรา"),
    (r"\bZiggs Eiffelstein\b", "ซิกส์ ไอเฟลสไตน์"),
    (r"\bZiggs\b", "ซิกส์"),
    (r"\bBelle Mayar\b", "เบลล์ มายาร์"),
    (r"\bBell Maya\b", "เบลล์ มายาร์"),
    (r"\bBell\b", "เบลล์"),
    (r"\bDune Grex\b", "ดูน เกร็กซ์"),
    (r"\bDune\b", "ดูน"),
    (r"\bTrayciana Bloomriver\b", "ทราเซียนา บลูมริเวอร์"),
    (r"\bTrayciana\b", "ทราเซียนา"),
    (r"\bSilvenia Academy\b", "สถาบันซิลเวเนีย"),
    (r"\bSilvenia\b", "ซิลเวเนีย"),
    (r"\bOphelis Hall\b", "หอพักโอฟีเลียส"),
    (r"\bOphelius Hall\b", "หอพักโอฟีเลียส"),
    (r"\bLorail Hall\b", "หอพักลอเรล"),
    (r"\bElte Company\b", "สมาคมการค้าเอลเต้"),
    (r"\bElte Store\b", "สมาคมการค้าเอลเต้"),
    (r"\bElte\b", "เอลเต้"),
    (r"\bMexes Bridge\b", "สะพานเมกเซส"),
    (r"\bSwordmaster\b", "ปรมาจารย์ดาบ"),
    (r"\bNorthern Forest\b", "ป่าทิศเหนือ"),
    (r"\bAcken Island\b", "เกาะอาเคน")
]

def translate_chunk(chunk: str) -> str:
    if not chunk.strip():
        return ""
    url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=th&dt=t&q=' + urllib.parse.quote(chunk)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return ''.join([part[0] for part in data[0] if part[0]])
        except Exception:
            time.sleep(0.5)
    return chunk

def apply_glossary(text: str) -> str:
    for pattern, repl in GLOSSARY_REPLACE:
        text = re.sub(pattern, repl, text)
    return text

def translate_chapter(ch_num: int):
    th_title, eng_title = TITLE_MAP.get(ch_num, (f"ตอนที่ {ch_num}", f"Chapter {ch_num}"))
    out_filename = f"chapter{ch_num} - {th_title} ({eng_title}).md"
    out_path = os.path.join(TH_DIR, out_filename)

    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        print(f"[=] ข้ามตอนที่ {ch_num} (มีไฟล์อยู่แล้ว): {out_filename}", flush=True)
        return True

    eng_matches = glob.glob(os.path.join(ENG_DIR, f"{ch_num:03d}*.md"))
    if not eng_matches:
        print(f"[!] ไม่พบไฟล์ต้นฉบับตอนที่ {ch_num}", flush=True)
        return False

    eng_path = eng_matches[0]
    eng_basename = os.path.basename(eng_path)
    print(f"[*] กำลังแปลตอนที่ {ch_num}: {eng_basename} -> {out_filename}", flush=True)

    with open(eng_path, "r", encoding="utf-8") as f:
        content = f.read()

    # ตัด TL's Note และ footer ออก
    if "TL’s Note:" in content:
        content = content.split("TL’s Note:")[0]
    elif "TL's Note:" in content:
        content = content.split("TL's Note:")[0]

    # แยกย่อหน้า
    raw_paras = [p.strip() for p in content.split("\n\n") if p.strip()]
    
    # กรองเอาเฉพาะย่อหน้าเนื้อเรื่อง (ข้าม header ต้นฉบับ)
    story_paras = []
    found_separator = False
    for p in raw_paras:
        if not found_separator:
            if p == "---" or p.startswith("---"):
                found_separator = True
            continue
        if p == "---" or p.startswith("---") or "https://" in p:
            continue
        story_paras.append(p)

    if not story_paras:
        story_paras = raw_paras[4:]

    # รวมเป็น chunks ละ ~1500 ตัวอักษร
    chunks = []
    curr = []
    curr_len = 0
    for p in story_paras:
        if curr_len + len(p) > 1500 and curr:
            chunks.append("\n\n".join(curr))
            curr = [p]
            curr_len = len(p)
        else:
            curr.append(p)
            curr_len += len(p)
    if curr:
        chunks.append("\n\n".join(curr))

    # แปลแบบขนานด้วย ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        trans_chunks = list(executor.map(translate_chunk, chunks))

    full_body = "\n\n".join(trans_chunks)
    full_body = apply_glossary(full_body)

    # ประกอบเป็นไฟล์ Markdown พร้อม Header
    doc = (
        f"# Chapter {ch_num} : {th_title} ({eng_title})\n\n"
        f"- **ชื่อเรื่อง:** The Extra’s Academy Survival Guide\n"
        f"- **ตอนที่:** {ch_num}\n"
        f"- **ชื่อตอนภาษาอังกฤษ:** {eng_title}\n"
        f"- **ไฟล์ต้นฉบับ:** `eng/{eng_basename}`\n\n"
        f"---\n\n"
        f"{full_body}\n"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)

    print(f"[✓] แปลตอนที่ {ch_num} เสร็จสิ้น: {out_filename} ({len(doc)} ตัวอักษร)", flush=True)
    return True

def main():
    print("=" * 65, flush=True)
    print("  The Extra's Academy Survival Guide - Fast Translator (178 - 200)", flush=True)
    print("=" * 65, flush=True)
    t0 = time.time()
    success = 0
    total = len(range(178, 201))

    for ch in range(178, 201):
        if translate_chapter(ch):
            success += 1
        time.sleep(0.2)

    elapsed = time.time() - t0
    print("=" * 65, flush=True)
    print(f"[✓] ดำเนินการเสร็จสิ้น! สำเร็จ {success}/{total} ตอน (ใช้เวลา {elapsed:.2f} วินาที)", flush=True)
    print("=" * 65, flush=True)

if __name__ == "__main__":
    main()