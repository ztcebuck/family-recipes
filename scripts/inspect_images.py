import os
import json
import hashlib
from PIL import Image, ExifTags

SRC = r'C:\Users\משתמש\Pictures\מתכונים'
with open(r'C:\Music\recipes-book\scripts\sources_inventory.json', encoding='utf-8') as f:
    inv = json.load(f)

img_details = []
hash_map = {}

for item in inv['img']:
    full = os.path.join(SRC, item['rel'].replace('/', os.sep))
    h = hashlib.md5(open(full, 'rb').read()).hexdigest()
    try:
        with Image.open(full) as im:
            w, ht = im.size
            exif = im.getexif()
            orient = exif.get(274, None) if exif else None
    except Exception as e:
        w, ht, orient = 0, 0, str(e)
    info = {
        'rel': item['rel'],
        'name': item['name'],
        'folder': item['folder'],
        'size': item['size'],
        'md5': h,
        'width': w,
        'height': ht,
        'exif_orientation': orient
    }
    img_details.append(info)
    hash_map.setdefault(h, []).append(item['rel'])

print("Duplicate image MD5s:")
for h, rels in hash_map.items():
    if len(rels) > 1:
        print(f"  {h[:8]}: {rels}")

with open(r'C:\Music\recipes-book\scripts\img_details.json', 'w', encoding='utf-8') as f:
    json.dump(img_details, f, ensure_ascii=False, indent=2)
print(f"Inspected {len(img_details)} images.")
