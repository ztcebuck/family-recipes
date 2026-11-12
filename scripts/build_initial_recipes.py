import os
import re
import json
import shutil
import struct
import zipfile
from PIL import Image, ImageOps

SRC_ROOT = r'C:\Users\משתמש\Pictures\מתכונים'
BOOK_ROOT = r'C:\Music\recipes-book'
PUBLIC_IMG = os.path.join(BOOK_ROOT, 'public', 'recipe-images')
PUBLIC_PDF = os.path.join(BOOK_ROOT, 'public', 'recipe-pdfs')
DATA_DIR = os.path.join(BOOK_ROOT, 'data')

for d in [PUBLIC_IMG, PUBLIC_PDF, DATA_DIR, os.path.join(PUBLIC_IMG, 'docx-media'), os.path.join(PUBLIC_IMG, 'course-tami')]:
    os.makedirs(d, exist_ok=True)

with open(r'C:\Music\recipes-book\scripts\sources_inventory.json', encoding='utf-8') as f:
    inv = json.load(f)

with open(r'C:\Music\recipes-book\scripts\img_details.json', encoding='utf-8') as f:
    img_details_list = json.load(f)
img_details_map = {x['rel']: x for x in img_details_list}

CATEGORIES = [
    { "id": "cakes", "name": "עוגות ועוגיות", "icon": "🎂" },
    { "id": "breads", "name": "לחמים ומאפים", "icon": "🥖" },
    { "id": "mains", "name": "עיקריות ובשרים", "icon": "🥩" },
    { "id": "salads", "name": "סלטים, רטבים ומטבלים", "icon": "🥗" },
    { "id": "desserts", "name": "קינוחים, מוסים וגלידות", "icon": "🍨" },
    { "id": "sides", "name": "תוספות", "icon": "🥔" },
    { "id": "pesach", "name": "מתכוני פסח", "icon": "🍷" },
    { "id": "fish", "name": "דגים", "icon": "🐟" },
    { "id": "dairy", "name": "חלבי", "icon": "🧀" },
    { "id": "starters", "name": "מנות ראשונות", "icon": "🥟" },
    { "id": "soups", "name": "מרקים", "icon": "🍲" }
]
CAT_NAME_BY_ID = {c['id']: c['name'] for c in CATEGORIES}

SKIP_PDFS = {
    ",_חוברת מתכונים לחג השבועות פ_ו מבית טוויסט .pdf",
    "K 200 22-06-09 Behaalosecha.pdf",
    "about_blank.pdf",
    "חוברת חגים תשפד איכות נמוכה.pdf",
    "חוברת מתכונים חגים תשפג (1) (1).pdf",
    "חוברת מתכונים לראש השנה.pdf",
    "חוברת מתכונים של סלברייט לתשעת הימים (1).pdf",
    "מאגר מתכונים ענק.pdf",
    "מגזין מתכונים לתשעת הימים (2).pdf",
    "נפגשות שבועות חוברת מתכונים.pdf",
    "שבועות של טעם מסלברייט.pdf",
    "סלטים/חוברת מתכונים סלטים פרוג גמורה קטן.pdf",
    "פסח/חוברת מתכונים פסח תשפ''ו - העני בקר.pdf",
}

FOLDER_TO_CAT = {
    'עוגות': 'cakes',
    'עוגות/עוגת מספרים': 'cakes',
    'סופגניות': 'cakes',
    'לחמים': 'breads',
    'עיקריות': 'mains',
    'סלטים': 'salads',
    'מנות אחרונות': 'desserts',
    'תוספות': 'sides',
    'פסח': 'pesach',
    'פסח/fwd': 'pesach',
    'פסח/פסח': 'pesach',
    'דגים': 'fish',
    'חלבי': 'dairy',
    'מנות ראשונות': 'starters',
}

SPECIAL_CAT_MAP = {
    # Root files
    'מילוי לטרטלים שוקולד.docx': 'desserts',
    'מתכון לקישקע.docx': 'sides',
    'פיתות במחבת.docx': 'breads',
    'קציצות טונה.docx': 'fish',
    'רוטב פטריות לברוקס.docx': 'salads',
    '_חלקנו בתורתך מתכון עוגיות קפה.pdf': 'cakes',
    'חטיפי-בארקס-עם-אגוזים-ופירות-יבשים-.pdf': 'desserts',
    'מרק כרובית.pdf': 'soups',
    "מתכון חצ'פורי.pdf": 'breads',
    'פאי אלפחורס.pdf': 'cakes',
    'פיצה בשר מטריפה לא מהעולם הזה! עם זילוף טחינה מעל - פודי - Foody (1).pdf': 'mains',
    'אקלרים במילוי קרם קפה.JPG': 'cakes',
    'הדלקעלך של סבתא.JPG': 'cakes',
    'חטיפי אנרגיה.JPG': 'desserts',
    'כדורי מוס בטעם נוגט.JPG': 'desserts',
    'לוג שוקולד.JPG': 'desserts',
    'מעדן פצפוצי אורז.JPG': 'desserts',
    'ספיסי מיונז.JPG': 'salads',
    'פריקסה.png': 'breads',
    'קרקר דק דק.JPG': 'breads',
    'קרקר דק דק המשך.JPG': 'breads',
    # תיקיה חדשה files
    '‏‏תיקיה חדשה/בטטות מקורמלות במילוי אורז משובץ בשקדים וצימוקים.docx': 'sides',
    '‏‏תיקיה חדשה/בייגלס.docx': 'breads',
    '‏‏תיקיה חדשה/טורטיה עם בשר טחיון על שיפוד.docx': 'mains',
    '‏‏תיקיה חדשה/טורטיות עם קבב.docx': 'mains',
    '‏‏תיקיה חדשה/כרובית קלויה.docx': 'sides',
    "‏‏תיקיה חדשה/מאפינס שוקולד צ'יפס.docx": 'cakes',
    '‏‏תיקיה חדשה/מוס חום.docx': 'desserts',
    '‏‏תיקיה חדשה/מוסקה.docx': 'mains',
    '‏‏תיקיה חדשה/מרק בצל.docx': 'soups',
    '‏‏תיקיה חדשה/מרק פטריות.docx': 'soups',
    '‏‏תיקיה חדשה/מרק קישואים וקולרבי.docx': 'soups',
    '‏‏תיקיה חדשה/עודה מפנקייק.docx': 'desserts',
    '‏‏תיקיה חדשה/ערייס רול.docx': 'mains',
    '‏‏תיקיה חדשה/פוקצות קנובל.docx': 'breads',
    '‏‏תיקיה חדשה/פיתות בצל מטוגנות.docx': 'breads',
    '‏‏תיקיה חדשה/פנקייק.docx': 'desserts',
    '‏‏תיקיה חדשה/קינוח פירות יער, גבניה ופירורים.docx': 'desserts',
    '‏‏תיקיה חדשה/רצועות חזה עוף.docx': 'mains',
    '‏‏תיקיה חדשה/שיפודי פרגית.docx': 'mains',
    '‏‏תיקיה חדשה/תפוחי אדמה בתנור.docx': 'sides',
    '‏‏תיקיה חדשה/תפוחי אדמה בתנור (.png': 'sides',
}

def get_cat_id(rel_path: str) -> str:
    if rel_path in SPECIAL_CAT_MAP:
        return SPECIAL_CAT_MAP[rel_path]
    folder = os.path.dirname(rel_path)
    return FOLDER_TO_CAT.get(folder, 'cakes')

def reset_jpeg_exif_orientation(data: bytearray) -> bool:
    if data[:2] != b'\xff\xd8':
        return False
    pos = 2
    while pos + 4 <= len(data) and pos < 65536:
        if data[pos] != 0xFF:
            break
        marker = data[pos+1]
        if marker == 0xDA:
            break
        length = struct.unpack('>H', data[pos+2:pos+4])[0]
        if marker == 0xE1 and data[pos+4:pos+10] == b'Exif\x00\x00':
            tiff = pos + 10
            endian = '<' if data[tiff:tiff+2] == b'II' else '>'
            ifd0_off = struct.unpack(endian + 'I', data[tiff+4:tiff+8])[0]
            ifd0 = tiff + ifd0_off
            if ifd0 + 2 <= len(data):
                num_entries = struct.unpack(endian + 'H', data[ifd0:ifd0+2])[0]
                for i in range(num_entries):
                    entry = ifd0 + 2 + i * 12
                    if entry + 12 <= len(data):
                        tag = struct.unpack(endian + 'H', data[entry:entry+2])[0]
                        if tag == 0x0112:
                            struct.pack_into(endian + 'H', data, entry + 8, 1)
                            return True
        pos += 2 + length
    return False

def copy_and_normalize_image(rel_path: str, cat_slug: str, custom_name: str = None) -> str:
    src_full = os.path.join(SRC_ROOT, rel_path.replace('/', os.sep))
    target_dir = os.path.join(PUBLIC_IMG, cat_slug)
    os.makedirs(target_dir, exist_ok=True)
    fname = custom_name if custom_name else os.path.basename(rel_path)
    fname = fname.replace('&', 'ו').replace('#', '')
    dst_full = os.path.join(target_dir, fname)
    url_path = f"/recipe-images/{cat_slug}/{fname}"

    if not os.path.exists(dst_full):
        info = img_details_map.get(rel_path, {})
        orient = info.get('exif_orientation')
        if orient in (3, 8):
            with Image.open(src_full) as im:
                im2 = ImageOps.exif_transpose(im)
                im2.save(dst_full, quality=92)
        else:
            raw = bytearray(open(src_full, 'rb').read())
            reset_jpeg_exif_orientation(raw)
            with open(dst_full, 'wb') as out_f:
                out_f.write(raw)
    return url_path

def extract_docx_media(rel_path: str, slug_prefix: str):
    src_full = os.path.join(SRC_ROOT, rel_path.replace('/', os.sep))
    urls = []
    with zipfile.ZipFile(src_full) as z:
        for m in sorted(z.namelist()):
            if m.startswith('word/media/'):
                data = z.read(m)
                if len(data) < 3000:
                    # Skip tiny 1x1 or email tracking gifs
                    continue
                ext = os.path.splitext(m)[1].lower()
                fname = f"{slug_prefix}_{os.path.basename(m)}"
                dst = os.path.join(PUBLIC_IMG, 'docx-media', fname)
                if not os.path.exists(dst):
                    with open(dst, 'wb') as fp:
                        fp.write(data)
                urls.append(f"/recipe-images/docx-media/{fname}")
    return urls

def copy_pdf(rel_path: str) -> str:
    src_full = os.path.join(SRC_ROOT, rel_path.replace('/', os.sep))
    prefix = os.path.dirname(rel_path).replace('/', '_').replace('\\', '_')
    base = os.path.basename(rel_path)
    fname = f"{prefix}_{base}" if prefix else base
    fname = fname.replace('&', 'ו').replace('#', '').replace('[', '').replace(']', '')
    dst_full = os.path.join(PUBLIC_PDF, fname)
    if not os.path.exists(dst_full):
        shutil.copy2(src_full, dst_full)
    return f"/recipe-pdfs/{fname}"

def guess_kashrut(title: str, text: str, cat_id: str) -> str:
    if cat_id == 'dairy':
        return 'חלבי'
    combined = f"{title} {text}"
    if 'טבעול' in combined or 'צמחוני' in combined or 'כבד צמחי' in combined:
        return 'פרווה'
    meat_words = ['בשר', 'עוף', 'פרגית', 'פרגיות', 'אסאדו', 'קבב', 'כבד', 'כבדים', 'פסטרמה', 'שניצל', 'שווארמה', 'שאוורמה', 'אנטריקוט', 'כתף עגל', 'הודו', 'עראייס', 'ערייס']
    dairy_words = ['חמאה', 'גבינה', 'גבינות', 'שמנת מתוקה', 'שמנת חמוצה', 'חלב ', 'מוצרלה', 'קוטג', 'גב"צ', 'גבצ', 'יוגורט', 'פרמזן', 'בולגרית', 'חלבי', 'ריבת חלב', 'חלבה וחמאת בוטנים' if False else 'שוקולד חלב']
    for w in meat_words:
        if w in combined:
            if 'בטעם כבד' in combined and w == 'כבד':
                continue
            if 'מרק עוף' in combined and w == 'עוף' and 'חזה עוף' not in combined and 'שוקי עוף' not in combined and 'עוף מטוגן' not in combined:
                continue
            return 'בשרי'
    for w in dairy_words:
        if w and w in combined:
            if 'חלב/ מים' in combined or 'מחמאה' in combined or 'שמנת מתוקה במקום הריצ' in combined or 'חמאה או נטורינה' in combined:
                continue
            return 'חלבי'
    return 'פרווה'

def clean_title_from_filename(fname: str) -> str:
    base = os.path.splitext(os.path.basename(fname))[0]
    base = base.lstrip('_').strip()
    base = re.sub(r'\s*\(\d+\)\s*$', '', base)
    base = re.sub(r'^\(\d+\)\s*', '', base)
    base = re.sub(r'\s+(המשך|תמונות|תמונה)\s*$', '', base)
    base = re.sub(r'_\d+$', '', base)
    base = base.replace(' - פודי - Foody', '').replace(' - עוגיו.נט', '')
    return base.strip()

def parse_paras_into_recipe(paras, default_title=""):
    if not paras:
        return default_title, [], [], ""
    lines = []
    for p in paras:
        if len(p) > 160 and '–' in p:
            parts = [x.strip() for x in p.split('–') if x.strip()]
            lines.extend(parts)
        else:
            lines.append(p.strip())
    title = default_title
    start_idx = 0
    while start_idx < len(lines) and (
        '@gmail.com' in lines[start_idx] or
        lines[start_idx].startswith('יום ') or
        lines[start_idx] == 'אני' or
        lines[start_idx].startswith('זמן קריאה') or
        lines[start_idx].startswith('עודכן:') or
        lines[start_idx] == 'מחוי' or
        re.match(r'^\d+ ב[א-ת]+׳? \d{4}$', lines[start_idx])
    ):
        start_idx += 1

    if start_idx < len(lines):
        first_clean = lines[start_idx].replace('מחוי', '').rstrip(':').strip()
        if not title:
            title = first_clean
            start_idx += 1
        elif len(first_clean) < 55 and not any(ch.isdigit() for ch in first_clean[:3]):
            if not any(first_clean.startswith(h) for h in ['החומרים', 'מצרכים', 'מרכיבים', 'רכיבים', 'אופן ההכנה', 'הוראות הכנה']):
                title = first_clean
                start_idx += 1

    ingredients = []
    steps = []
    notes_list = []
    mode = 'ingredients'

    step_headers = ('הוראות הכנה', 'אופן ההכנה', 'אופן הכנה', 'הוראת הכנה', 'הראות הכנה', 'הכנה:', 'הוראות:', 'אופן ההכנה לסלט')
    ing_headers = ('החומרים', 'מצרכים', 'מרכיבים', 'רכיבים', 'המתכון:', 'המצרכים')
    step_verbs = ('מערבבים', 'ערבבי', 'הקציפי', 'מקציפים', 'מחממים', 'אופים', 'אפי ', 'טגני', 'מטגנים', 'מבשלים', 'בשלי', 'לושי', 'לשים ', 'חותכים', 'חתכי', 'פורסים', 'מניחים', 'מוסיפים', 'הוסיפי', 'טוחנים', 'טחני', 'שמים ', 'בקערה ', 'בסיר ', 'במחבת ', 'לערבב', 'להקציף', 'לחתוך', 'לטגן', 'לבשל', 'לאפות', 'להמיס', 'ממיסים', 'המיסי')

    seen_lines = set()
    for line in lines[start_idx:]:
        clean = line.strip()
        if not clean or clean == 'מחוי':
            continue
        # Deduplicate repeated paragraphs (like in פאי גבינה חגיגית.docx)
        if len(clean) > 40 and clean in seen_lines:
            continue
        seen_lines.add(clean)

        if any(clean.startswith(h) for h in ing_headers):
            mode = 'ingredients'
            rest = re.sub(r'^(החומרים|מצרכים|מרכיבים|רכיבים|המתכון|המצרכים)\s*:?\s*', '', clean).strip()
            if rest and len(rest) < 100:
                ingredients.append(rest)
            elif rest:
                steps.append(rest)
            continue
        if any(clean.startswith(h) for h in step_headers):
            mode = 'steps'
            rest = re.sub(r'^(הוראות הכנה|אופן ההכנה|אופן הכנה|הוראת הכנה|הראות הכנה|הכנה|הוראות)\s*:?\s*', '', clean).strip()
            if rest:
                steps.append(rest)
            continue
        if clean.startswith('הערות') or clean.startswith('טיפ'):
            notes_list.append(clean)
            continue

        if clean.endswith(':') and len(clean) < 35:
            if mode == 'steps' or clean.startswith(('להכנת', 'הרכבת', 'עיצוב', 'מגישים', 'מכינים', 'ממלאים')):
                mode = 'steps'
                steps.append(clean)
            else:
                ingredients.append(clean)
            continue

        if mode == 'ingredients':
            if len(clean) > 85 or clean.startswith(step_verbs) or re.match(r'^\d+[\.\)]\s*', clean):
                mode = 'steps'
                steps.append(clean)
            else:
                ingredients.append(clean)
        else:
            steps.append(clean)

    return title or default_title, ingredients, steps, "\n".join(notes_list)

def split_meutzav_docx(paras):
    recipes_out = []
    n = len(paras)
    title_indices = []
    for i in range(n - 1):
        nxt = paras[i+1].strip()
        cur = paras[i].strip()
        if nxt.startswith('החומרים') and not cur.endswith(':'):
            title_indices.append(i)
    for idx_pos, start_i in enumerate(title_indices):
        end_i = title_indices[idx_pos + 1] if idx_pos + 1 < len(title_indices) else n
        chunk = paras[start_i:end_i]
        r_title = chunk[0].strip()
        _, ings, stps, nts = parse_paras_into_recipe(chunk[1:], default_title=r_title)
        cat_id = 'cakes'
        if any(w in r_title for w in ['מוס ', 'גלידת', 'ג\'לי', 'טרפל', 'סופלה', 'אייס קפה', 'כדורי ']):
            cat_id = 'desserts'
        elif any(w in r_title for w in ['רוטב ', 'מלית לפיצה', 'חצילים', 'כבד צמחי']):
            cat_id = 'salads'
        elif any(w in r_title for w in ['חלות', 'פיתות', 'לחמניות', 'פיצה']):
            cat_id = 'breads'
        elif any(w in r_title for w in ['קציצות טונה', 'פשטידת טונה']):
            cat_id = 'fish'
        elif any(w in r_title for w in ['פשטידת אטריות חלבית', 'לביבות גבינה']):
            cat_id = 'dairy'
        elif any(w in r_title for w in ['פשטידת', 'פלאפל', 'קרפלך']):
            cat_id = 'sides'
        recipes_out.append({
            'title': r_title,
            'categoryId': cat_id,
            'ingredients': ings,
            'steps': stps,
            'notes': nts,
            'rawText': "\n".join(chunk)
        })
    return recipes_out

# Build unified recipes list
recipes = []
recipe_Counter = 0
def next_id(prefix='rec'):
    global recipe_Counter
    recipe_Counter += 1
    return f"{prefix}-{recipe_Counter:03d}"

# Track Companion images and PDFs that merge into DOCX or PDF recipes
# 1. Exact duplicate DOCX in תיקיה חדשה -> merge into סלטים
DUP_DOCX_MAP = {
    'סלטים/סלט בטטות.docx': '‏‏תיקיה חדשה/סלט בטטות.docx',
    'סלטים/סלט חצילים בצילי.docx': '‏‏תיקיה חדשה/סלט חצילים בצילי.docx',
    'סלטים/סלט ירקות מוחמצים.docx': '‏‏תיקיה חדשה/סלט ירקות מוחמצים.docx',
    'סלטים/סלט עוף קר.docx': '‏‏תיקיה חדשה/סלט עוף קר.docx',
    'סלטים/סלט פסטרמה.docx': '‏‏תיקיה חדשה/סלט פסטרמה.docx',
}
SKIP_DUP_DOCX = set(DUP_DOCX_MAP.values())

# Companion images for DOCX files
DOCX_COMPANION_IMGS = {
    'סלטים/סלט כרוב.docx': ['סלטים/סלט כרוב.jpg', 'סלטים/סלט כרוב (2).JPG'],
    'סלטים/רוטב פיצה.docx': ['סלטים/רוטב פיצה.jpg'],
    '‏‏תיקיה חדשה/תפוחי אדמה בתנור.docx': ['‏‏תיקיה חדשה/תפוחי אדמה בתנור (.png'],
}
CONSUMED_IMGS = set()
for imgs in DOCX_COMPANION_IMGS.values():
    CONSUMED_IMGS.update(imgs)

# Process all individual DOCX files (except מתכונים שלנו מעוצב.docx and 5 exact duplicates)
indiv_docx_titles = {}
for item in inv['docx']:
    rel = item['rel']
    if rel in SKIP_DUP_DOCX or rel == 'מתכונים שלנו מעוצב.docx':
        continue
    cat_id = get_cat_id(rel)
    default_t = clean_title_from_filename(item['name'])
    title, ings, stps, nts = parse_paras_into_recipe(item['paras'], default_title=default_t)
    raw_text = "\n".join(item['paras']) if item['paras'] else title

    # Special case: תפוחי אדמה עם קורנפלור(פוטטוס).docx has 3 embedded PNG screenshots of the recipe
    if rel == 'תוספות/תפוחי אדמה עם קורנפלור(פוטטוס).docx':
        title = 'תפוחי אדמה עם קורנפלור (פוטטוס)'
        ings = [
            '5-6 תפוחי אדמה בינוניים חתוכים לפלחים (סירות)',
            '3-4 כפות שמן זית',
            '2 כפות גדושות קורנפלור',
            '1 כפית פפריקה מתוקה',
            '1 כפית אבקת שום / שום גבישי',
            '1 כפית אורגנו יבש או טימין',
            'מלח ופלפל שחור גרוס לפי הטעם'
        ]
        stps = [
            'שוטפים היטב את תפוחי האדמה (עם הקליפה) וחותכים לפלחים שווים בצורת סירות.',
            'משרים בקערת מים קרים ל-15 דקות להוצאת העמילן, מסננים ומייבשים היטב במגבת.',
            'מעבירים לקערה גדולה או שקית, מוסיפים את הקורנפלור והתבלינים ומנערים היטב עד שכל הפלחים מצופים בשכבה דקה.',
            'מוסיפים את שמן הזית ומערבבים שוב.',
            'מסדרים בשכבה אחת מרווחת על תבנית מרופדת בנייר אפייה.',
            'אופים בתנור שחומם מראש ל-200 מעלות כ-40-45 דקות עד שהפוטטוס זהובים ופריכים מאוד מבחוץ ורכים מבפנים.'
        ]
        raw_text = title + "\n" + "\n".join(ings + stps)

    elif rel == '‏‏תיקיה חדשה/תפוחי אדמה בתנור.docx':
        title = 'תפוחי אדמה בתנור (פוטטוס מושלמים)'
        ings = [
            '6 תפוחי אדמה חתוכים לפלחים',
            '1/4 כוס שמן זית',
            'כף פפריקה מתוקה',
            'כפית שום גבישי',
            'כפית מלח גס, פלפל שחור',
            'כף רוזמרין או טימין קצוץ'
        ]
        stps = [
            'חותכים את תפוחי האדמה לפלחים ומערבבים בקערה עם שמן הזית והתבלינים.',
            'מסדרים בתבנית על נייר אפייה בשכבה אחת.',
            'אופים ב-200 מעלות כ-45 דקות עד להשחמה ופריכות.'
        ]
        raw_text = title + "\n" + "\n".join(ings + stps) + "\n" + raw_text

    rid = next_id('docx')
    orig_imgs = extract_docx_media(rel, rid)
    if rel in DOCX_COMPANION_IMGS:
        for c_img in DOCX_COMPANION_IMGS[rel]:
            orig_imgs.append(copy_and_normalize_image(c_img, cat_id))

    src_files = [rel]
    if rel in DUP_DOCX_MAP:
        src_files.append(DUP_DOCX_MAP[rel])

    rec = {
        "id": rid,
        "title": title,
        "category": CAT_NAME_BY_ID[cat_id],
        "categoryId": cat_id,
        "subcategory": "סופגניות ודונאטס" if item['folder'] == 'סופגניות' else "",
        "kashrut": guess_kashrut(title, raw_text, cat_id),
        "prepTime": "",
        "servings": "",
        "difficulty": "",
        "ingredients": ings,
        "steps": stps,
        "notes": nts,
        "rawText": raw_text,
        "originalImages": orig_imgs,
        "originalPdf": "",
        "sourceType": "docx",
        "sourceFolder": item['folder'] or "ראשי",
        "sourceFiles": src_files,
        "favorite": False
    }
    recipes.append(rec)
    indiv_docx_titles[title.strip()] = rec

# Now process מתכונים שלנו מעוצב.docx (91 recipes, merging with indiv_docx_titles if identical title)
meutzav = next(x for x in inv['docx'] if x['rel'] == 'מתכונים שלנו מעוצב.docx')
for sub in split_meutzav_docx(meutzav['paras']):
    t = sub['title'].strip()
    if t in indiv_docx_titles:
        existing = indiv_docx_titles[t]
        if 'מתכונים שלנו מעוצב.docx' not in existing['sourceFiles']:
            existing['sourceFiles'].append('מתכונים שלנו מעוצב.docx')
        continue
    cat_id = sub['categoryId']
    rid = next_id('docx')
    recipes.append({
        "id": rid,
        "title": t,
        "category": CAT_NAME_BY_ID[cat_id],
        "categoryId": cat_id,
        "subcategory": "מתכונים שלנו מעוצב",
        "kashrut": guess_kashrut(t, sub['rawText'], cat_id),
        "prepTime": "",
        "servings": "",
        "difficulty": "",
        "ingredients": sub['ingredients'],
        "steps": sub['steps'],
        "notes": sub['notes'],
        "rawText": sub['rawText'],
        "originalImages": [],
        "originalPdf": "",
        "sourceType": "docx",
        "sourceFolder": "מתכונים שלנו מעוצב",
        "sourceFiles": ["מתכונים שלנו מעוצב.docx"],
        "favorite": False
    })

# Process 3 TXT files
for item in inv['txt']:
    rel = item['rel']
    cat_id = get_cat_id(rel)
    default_t = clean_title_from_filename(item['name'])
    if default_t == 'גילדת אוראו':
        default_t = 'גלידת אוראו'
    paras = [ln.strip() for ln in (item['text'] or '').splitlines() if ln.strip()]
    title, ings, stps, nts = parse_paras_into_recipe(paras, default_title=default_t)
    raw_text = item['text'] or title
    recipes.append({
        "id": next_id('txt'),
        "title": title,
        "category": CAT_NAME_BY_ID[cat_id],
        "categoryId": cat_id,
        "subcategory": "",
        "kashrut": guess_kashrut(title, raw_text, cat_id),
        "prepTime": "",
        "servings": "",
        "difficulty": "",
        "ingredients": ings,
        "steps": stps,
        "notes": nts,
        "rawText": raw_text,
        "originalImages": [],
        "originalPdf": "",
        "sourceType": "txt",
        "sourceFolder": item['folder'] or "ראשי",
        "sourceFiles": [rel],
        "favorite": False
    })

# Companion images for PDF files
PDF_COMPANION_IMGS = {
    'סלטים/סלט חזה חרדל ודבש.pdf': ['סלטים/סלט חזה חרדל ודבש.JPG'],
    'עוגות/ביסקוטי בציפוי שוקולד.pdf': ['עוגות/ביסקוטים בציפוי שוקולד.JPG'],
    'עוגות/סטיק שוקולד ציפס.pdf': ["עוגות/סטיק שוקולד צ'יפס.JPG", 'עוגות/סטיקס שוקו ציפס.jpg'],
    'עוגות/עוגיות במילוי שוקולד.pdf': ['עוגות/עוגיות במילוי קרם שוקולד.JPG'],
    'עיקריות/חלת אסאדו מפורק.pdf': ['לחמים/חלת אסאדו מפורק.JPG'],
}
for imgs in PDF_COMPANION_IMGS.values():
    CONSUMED_IMGS.update(imgs)

# Process active PDFs
for item in inv['pdf']:
    rel = item['rel']
    if rel in SKIP_PDFS:
        continue
    if rel == 'מתכונית סדנה עם בשר (2).pdf':
        # Exact duplicate of עיקריות/חזה עוף פסטרמה קר הקמפוס הקולינרי.pdf
        continue
    pdf_url = copy_pdf(rel)
    cat_id = get_cat_id(rel)
    title = clean_title_from_filename(item['name'])
    orig_imgs = []
    if rel in PDF_COMPANION_IMGS:
        for c_img in PDF_COMPANION_IMGS[rel]:
            orig_imgs.append(copy_and_normalize_image(c_img, cat_id))
    src_files = [rel]
    if rel == 'עיקריות/חזה עוף פסטרמה קר הקמפוס הקולינרי.pdf':
        src_files.append('מתכונית סדנה עם בשר (2).pdf')
    if rel in PDF_COMPANION_IMGS:
        src_files.extend(PDF_COMPANION_IMGS[rel])

    recipes.append({
        "id": next_id('pdf'),
        "title": title,
        "category": CAT_NAME_BY_ID[cat_id],
        "categoryId": cat_id,
        "subcategory": "כשר לפסח" if cat_id == 'pesach' else "",
        "kashrut": guess_kashrut(title, title, cat_id),
        "prepTime": "",
        "servings": "",
        "difficulty": "",
        "ingredients": [],
        "steps": [],
        "notes": "",
        "rawText": title,
        "originalImages": orig_imgs,
        "originalPdf": pdf_url,
        "sourceType": "pdf",
        "sourceFolder": item['folder'] or "ראשי",
        "sourceFiles": src_files,
        "favorite": False
    })

# Now group and process all Recipe Images
# Explicit multi-page groups and duplicate merges
EXPLICIT_IMG_GROUPS = [
    {
        'title': 'קרקר דק דק',
        'cat_id': 'breads',
        'folder': 'לחמים',
        'files': ['לחמים/קרקר דק דק.JPG', 'קרקר דק דק המשך.JPG', 'לחמים/קרקר דק דק תמונות.JPG', 'קרקר דק דק.JPG'],
        'unique_imgs': ['לחמים/קרקר דק דק.JPG', 'קרקר דק דק המשך.JPG', 'לחמים/קרקר דק דק תמונות.JPG']
    },
    {
        'title': 'פיתות בצל או זעתר',
        'cat_id': 'breads',
        'folder': 'לחמים',
        'files': ['לחמים/פיתות בצל.JPG', 'לחמים/פיתות בצל או זעתר.JPG', 'לחמים/פיתות בצל תמונות.JPG'],
        'unique_imgs': ['לחמים/פיתות בצל.JPG', 'לחמים/פיתות בצל תמונות.JPG']
    },
    {
        'title': 'עוגה (צילום מתכון)',
        'cat_id': 'cakes',
        'folder': 'עוגות',
        'files': ['עוגות/עוגה.png', 'עוגות/image (2) (1).png'],
        'unique_imgs': ['עוגות/עוגה.png']
    },
    {
        'title': 'עוגת מספרים',
        'cat_id': 'cakes',
        'folder': 'עוגות/עוגת מספרים',
        'files': ['עוגות/עוגת מספרים/003.jpg', 'עוגות/עוגת מספרים/004.jpg', 'עוגות/עוגת מספרים/005.jpg', 'עוגות/עוגת מספרים/006.jpg'],
        'unique_imgs': ['עוגות/עוגת מספרים/003.jpg', 'עוגות/עוגת מספרים/004.jpg', 'עוגות/עוגת מספרים/005.jpg', 'עוגות/עוגת מספרים/006.jpg']
    },
    {
        'title': 'ביגלס',
        'cat_id': 'breads',
        'folder': 'לחמים',
        'files': ['לחמים/ביגלס 1.jpg', 'לחמים/ביגלס 2.jpg'],
        'unique_imgs': ['לחמים/ביגלס 1.jpg', 'לחמים/ביגלס 2.jpg']
    },
    {
        'title': 'פרצל חם ורך',
        'cat_id': 'breads',
        'folder': 'לחמים',
        'files': ['לחמים/פרצל חם ורך 1.JPG', 'לחמים/פרצל חם ורך 2.JPG'],
        'unique_imgs': ['לחמים/פרצל חם ורך 1.JPG', 'לחמים/פרצל חם ורך 2.JPG']
    },
    {
        'title': 'חצילים ממולאים בירקות',
        'cat_id': 'salads',
        'folder': 'סלטים',
        'files': ['סלטים/חצילים ממולאים בירקות.jpg', 'סלטים/חצילים ממולאים ירקות תמונה.jpg'],
        'unique_imgs': ['סלטים/חצילים ממולאים בירקות.jpg', 'סלטים/חצילים ממולאים ירקות תמונה.jpg']
    },
    {
        'title': 'טורטיות במילוי חזה עוף',
        'cat_id': 'starters',
        'folder': 'מנות ראשונות',
        'files': ['מנות ראשונות/טורטיות במילוי חזה.png', 'מנות ראשונות/(2)טורטיות במילוי חזה.png', 'מנות ראשונות/טורטיות במילוי חזה עוף.JPG'],
        'unique_imgs': ['מנות ראשונות/טורטיות במילוי חזה.png', 'מנות ראשונות/(2)טורטיות במילוי חזה.png', 'מנות ראשונות/טורטיות במילוי חזה עוף.JPG']
    },
]

for grp in EXPLICIT_IMG_GROUPS:
    CONSUMED_IMGS.update(grp['files'])
    urls = [copy_and_normalize_image(u, grp['cat_id']) for u in grp['unique_imgs']]
    recipes.append({
        "id": next_id('img'),
        "title": grp['title'],
        "category": CAT_NAME_BY_ID[grp['cat_id']],
        "categoryId": grp['cat_id'],
        "subcategory": "",
        "kashrut": guess_kashrut(grp['title'], grp['title'], grp['cat_id']),
        "prepTime": "",
        "servings": "",
        "difficulty": "",
        "ingredients": [],
        "steps": [],
        "notes": "",
        "rawText": grp['title'],
        "originalImages": urls,
        "originalPdf": "",
        "sourceType": "image",
        "sourceFolder": grp['folder'],
        "sourceFiles": grp['files'],
        "favorite": False
    })

# Auto-group remaining images by (folder, normalized_base_name)
remaining_imgs = [im for im in inv['img'] if im['folder'] != 'תמונות קורס תמי פיליפ' and im['rel'] not in CONSUMED_IMGS]

def normalize_img_group_key(name: str) -> str:
    stem = os.path.splitext(name)[0].strip()
    stem = re.sub(r'\s*\(\d+\)\s*$', '', stem)
    stem = re.sub(r'^\(\d+\)\s*', '', stem)
    stem = re.sub(r'\s+(המשך|תמונות|תמונה)\s*$', '', stem)
    return stem.strip()

grouped_remaining = {}
for im in remaining_imgs:
    key = (im['folder'], normalize_img_group_key(im['name']))
    grouped_remaining.setdefault(key, []).append(im)

for (folder, base_title), items in grouped_remaining.items():
    # Sort so main page comes before (2), (3), המשך, תמונות, תמונה
    def sort_key(x):
        n = x['name']
        if 'תמונות' in n or 'תמונה' in n:
            return (2, n)
        if '(2)' in n or 'המשך' in n:
            return (1, n)
        if '(3)' in n:
            return (3, n)
        return (0, n)
    items_sorted = sorted(items, key=sort_key)
    first_rel = items_sorted[0]['rel']
    cat_id = get_cat_id(first_rel)
    urls = [copy_and_normalize_image(x['rel'], cat_id) for x in items_sorted]
    src_files = [x['rel'] for x in items_sorted]
    clean_t = base_title.lstrip('_').strip()
    recipes.append({
        "id": next_id('img'),
        "title": clean_t,
        "category": CAT_NAME_BY_ID[cat_id],
        "categoryId": cat_id,
        "subcategory": "סופגניות ודונאטס" if folder == 'סופגניות' else "",
        "kashrut": guess_kashrut(clean_t, clean_t, cat_id),
        "prepTime": "",
        "servings": "",
        "difficulty": "",
        "ingredients": [],
        "steps": [],
        "notes": "",
        "rawText": clean_t,
        "originalImages": urls,
        "originalPdf": "",
        "sourceType": "image",
        "sourceFolder": folder or "ראשי",
        "sourceFiles": src_files,
        "favorite": False
    })

# Course gallery (29 photos)
course_gallery = []
course_imgs = [im for im in inv['img'] if im['folder'] == 'תמונות קורס תמי פיליפ']
for idx, im in enumerate(course_imgs, 1):
    url = copy_and_normalize_image(im['rel'], 'course-tami')
    num = os.path.splitext(im['name'])[0].replace('IMG_', '')
    course_gallery.append({
        "id": f"tami-{num}",
        "title": f"קורס תמי פיליפ - תמונה {idx}",
        "imageUrl": url
    })

output_db = {
    "updatedAt": "2026-11-11T14:15:00Z",
    "categories": CATEGORIES,
    "recipes": recipes,
    "courseGallery": course_gallery
}

out_path = os.path.join(DATA_DIR, 'recipes.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output_db, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(recipes)} recipes and {len(course_gallery)} course photos to {out_path}")
from collections import Counter
print("By sourceType:", dict(Counter(r['sourceType'] for r in recipes)))
print("By categoryId:", dict(Counter(r['categoryId'] for r in recipes)))
