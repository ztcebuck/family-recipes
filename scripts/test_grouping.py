import os
import re
import json

with open(r'C:\Music\recipes-book\scripts\sources_inventory.json', encoding='utf-8') as f:
    inv = json.load(f)

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

print("Active PDFs:")
active_pdfs = [p for p in inv['pdf'] if p['rel'] not in SKIP_PDFS]
print(f"Total active PDFs: {len(active_pdfs)} (skipped {len(inv['pdf']) - len(active_pdfs)})")
for p in active_pdfs:
    print("  PDF:", p['rel'])

# Check images by folder
recipe_imgs = [im for im in inv['img'] if im['folder'] != 'תמונות קורס תמי פיליפ']
course_imgs = [im for im in inv['img'] if im['folder'] == 'תמונות קורס תמי פיליפ']
print(f"Recipe images: {len(recipe_imgs)}, Course images: {len(course_imgs)}")
