# -*- coding: utf-8 -*-
import os
import json
import glob
from PIL import Image

def main():
    print("--- STEP 1: ROTATING SIDEWAYS IMAGES ON DISK ---")
    base_img_dir = r'C:\Music\recipes-book\public\recipe-images'
    rotated_count = 0

    for root, dirs, files in os.walk(base_img_dir):
        if 'course-tami' in root or 'docx-media' in root:
            continue
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                p = os.path.join(root, f)
                try:
                    with Image.open(p) as im:
                        # 2000x1500 camera scans or cappuccino cake 2000x1333
                        if im.size == (2000, 1500) or f == '_עוגת קפוצינו - מרוה.jpg':
                            im_cw = im.transpose(Image.Transpose.ROTATE_270)
                            # Overwrite directly
                            im_cw.save(p, quality=85)
                            rotated_count += 1
                except Exception as e:
                    print(f"Error rotating {p}: {e}")

    print(f"Successfully rotated {rotated_count} images 90° CW to upright portrait mode.")

    print("\n--- STEP 2: LOADING BATCH RESULTS ---")
    results_by_id = {}

    # Load image batches 1-6
    for b in range(1, 7):
        batch_path = f'C:/Music/recipes-book/scripts/batches/result_img_{b}.json'
        with open(batch_path, 'r', encoding='utf-8') as f:
            items = json.load(f)
            for item in items:
                results_by_id[item['id']] = item

    # Load PDF batch
    pdf_path = 'C:/Music/recipes-book/scripts/batches/result_pdf.json'
    with open(pdf_path, 'r', encoding='utf-8') as f:
        pdf_items = json.load(f)
        for item in pdf_items:
            results_by_id[item['id']] = item

    print(f"Loaded {len(results_by_id)} transcribed items from batches.")

    print("\n--- STEP 3: UPDATING recipes.json ---")
    recipes_json_path = r'C:\Music\recipes-book\data\recipes.json'
    with open(recipes_json_path, 'r', encoding='utf-8') as f:
        db = json.load(f)

    updated_recipes_count = 0
    for r in db['recipes']:
        rid = r['id']
        if rid in results_by_id:
            res = results_by_id[rid]
            # Update fields
            if res.get('title') and len(res['title']) > len(r.get('title', '')):
                r['title'] = res['title']
            elif res.get('title') and not r.get('title'):
                r['title'] = res['title']

            if res.get('kashrut'):
                r['kashrut'] = res['kashrut']
            if res.get('prepTime'):
                r['prepTime'] = res['prepTime']
            if res.get('servings'):
                r['servings'] = res['servings']
            if res.get('difficulty'):
                r['difficulty'] = res['difficulty']

            if res.get('ingredients') and len(res['ingredients']) > 0:
                r['ingredients'] = res['ingredients']

            if res.get('steps') and len(res['steps']) > 0:
                r['steps'] = res['steps']

            if res.get('notes'):
                r['notes'] = res['notes']

            # Build full rawText
            full_parts = [r.get('title', '')]
            if r.get('category'):
                full_parts.append(r['category'])
            if r.get('notes'):
                full_parts.append(r['notes'])
            if r.get('ingredients'):
                full_parts.extend(r['ingredients'])
            if r.get('steps'):
                full_parts.extend(r['steps'])
            r['rawText'] = "\n".join([str(p) for p in full_parts if p])
            updated_recipes_count += 1

    print(f"Updated {updated_recipes_count} recipes with rich transcribed data.")

    # Re-save recipes.json
    with open(recipes_json_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("\n--- STEP 4: VERIFYING ASSETS AND DATABASE ---")
    public_root = r'C:\Music\recipes-book\public'
    missing_assets = []
    
    source_type_counts = {}
    category_counts = {}

    for r in db['recipes']:
        st = r.get('sourceType', 'unknown')
        cat = r.get('category', 'unknown')
        source_type_counts[st] = source_type_counts.get(st, 0) + 1
        category_counts[cat] = category_counts.get(cat, 0) + 1

        for img_url in r.get('originalImages', []):
            rel = img_url.lstrip('/').replace('/', os.sep)
            full_path = os.path.join(public_root, rel)
            if not os.path.exists(full_path):
                missing_assets.append(f"Image not found: {img_url} in recipe {r['id']}")

        if r.get('originalPdf'):
            pdf_url = r['originalPdf']
            rel = pdf_url.lstrip('/').replace('/', os.sep)
            full_path = os.path.join(public_root, rel)
            if not os.path.exists(full_path):
                missing_assets.append(f"PDF not found: {pdf_url} in recipe {r['id']}")

    for gal in db.get('courseGallery', []):
        img_url = gal.get('imageUrl', '')
        rel = img_url.lstrip('/').replace('/', os.sep)
        full_path = os.path.join(public_root, rel)
        if not os.path.exists(full_path):
            missing_assets.append(f"Gallery image not found: {img_url}")

    print(f"Total recipes: {len(db['recipes'])}")
    print(f"By sourceType: {source_type_counts}")
    print(f"By category: {category_counts}")
    print(f"Total Course Gallery items: {len(db.get('courseGallery', []))}")
    print(f"Missing assets: {len(missing_assets)}")
    if missing_assets:
        for m in missing_assets[:10]:
            print("  ", m)
    else:
        print("ALL ASSETS VERIFIED ON DISK! 100% PERFECT!")

if __name__ == '__main__':
    main()
