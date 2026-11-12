import os
import json

BOOK_ROOT = r'C:\Music\recipes-book'
DATA_PATH = os.path.join(BOOK_ROOT, 'data', 'recipes.json')
BATCH_DIR = os.path.join(BOOK_ROOT, 'scripts', 'batches')
os.makedirs(BATCH_DIR, exist_ok=True)

with open(DATA_PATH, encoding='utf-8') as f:
    db = json.load(f)

pdf_recipes = []
img_recipes = []

for r in db['recipes']:
    if r['sourceType'] == 'pdf':
        pdf_recipes.append({
            'id': r['id'],
            'title': r['title'],
            'categoryId': r['categoryId'],
            'pdfFile': os.path.join(BOOK_ROOT, 'public', r['originalPdf'].lstrip('/').replace('/', os.sep)),
            'imageFiles': [os.path.join(BOOK_ROOT, 'public', u.lstrip('/').replace('/', os.sep)) for u in r['originalImages']],
            'originalImages': r['originalImages']
        })
    elif r['sourceType'] == 'image':
        img_recipes.append({
            'id': r['id'],
            'title': r['title'],
            'categoryId': r['categoryId'],
            'imageFiles': [os.path.join(BOOK_ROOT, 'public', u.lstrip('/').replace('/', os.sep)) for u in r['originalImages']],
            'originalImages': r['originalImages']
        })

# Batch 1: 48 PDF recipes
with open(os.path.join(BATCH_DIR, 'manifest_pdf.json'), 'w', encoding='utf-8') as f:
    json.dump(pdf_recipes, f, ensure_ascii=False, indent=2)

# Split 243 img_recipes into 6 batches of ~40 recipes each
chunk_size = 41
for i in range(6):
    chunk = img_recipes[i*chunk_size : (i+1)*chunk_size]
    with open(os.path.join(BATCH_DIR, f'manifest_img_{i+1}.json'), 'w', encoding='utf-8') as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)
    print(f"Batch img_{i+1}: {len(chunk)} recipes ({chunk[0]['id']}..{chunk[-1]['id']})")

print(f"Batch pdf: {len(pdf_recipes)} recipes")
