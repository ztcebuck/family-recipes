import os
import json
import zipfile
import xml.etree.ElementTree as ET
import hashlib

SRC = r'C:\Users\משתמש\Pictures\מתכונים'
OUT_DIR = r'C:\Music\recipes-book\scripts'
os.makedirs(OUT_DIR, exist_ok=True)

docx_data = []
txt_data = []
pdf_files = []
img_files = []

for root, dirs, files in os.walk(SRC):
    for f in sorted(files):
        full = os.path.join(root, f)
        rel = os.path.relpath(full, SRC).replace('\\', '/')
        ext = os.path.splitext(f)[1].lower()
        if ext == '.docx':
            with open(full, 'rb') as fp:
                file_hash = hashlib.md5(fp.read()).hexdigest()
            with zipfile.ZipFile(full) as z:
                media = [m for m in z.namelist() if m.startswith('word/media/')]
                xml_content = z.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                paras = []
                for elem in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                    texts = [t.text for t in elem.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
                    line = ''.join(texts).strip()
                    if line:
                        paras.append(line)
            docx_data.append({
                'rel': rel,
                'name': f,
                'folder': os.path.dirname(rel),
                'hash': file_hash,
                'media': media,
                'paras': paras
            })
        elif ext == '.txt':
            text = None
            for enc in ['utf-8-sig', 'utf-8', 'cp1255', 'iso-8859-8']:
                try:
                    with open(full, 'r', encoding=enc) as fp:
                        text = fp.read()
                    break
                except Exception:
                    pass
            txt_data.append({
                'rel': rel,
                'name': f,
                'folder': os.path.dirname(rel),
                'text': text
            })
        elif ext == '.pdf':
            pdf_files.append({
                'rel': rel,
                'name': f,
                'folder': os.path.dirname(rel),
                'size': os.path.getsize(full)
            })
        elif ext in ('.jpg', '.jpeg', '.png'):
            img_files.append({
                'rel': rel,
                'name': f,
                'folder': os.path.dirname(rel),
                'size': os.path.getsize(full)
            })

with open(os.path.join(OUT_DIR, 'sources_inventory.json'), 'w', encoding='utf-8') as fp:
    json.dump({
        'docx': docx_data,
        'txt': txt_data,
        'pdf': pdf_files,
        'img': img_files
    }, fp, ensure_ascii=False, indent=2)

print(f"Saved inventory: {len(docx_data)} docx, {len(txt_data)} txt, {len(pdf_files)} pdf, {len(img_files)} img")
