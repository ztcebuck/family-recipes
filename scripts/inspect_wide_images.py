# -*- coding: utf-8 -*-
import os
from PIL import Image

base = r'C:\Music\recipes-book\public\recipe-images'
wide_images = []
for root, dirs, files in os.walk(base):
    if 'course-tami' in root or 'docx-media' in root:
        continue
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            p = os.path.join(root, f)
            try:
                with Image.open(p) as im:
                    w, h = im.size
                    if w > h:
                        wide_images.append((p, w, h))
            except Exception as e:
                pass

print(f"Total wide (landscape) recipe images: {len(wide_images)}")
for p, w, h in wide_images[:20]:
    print(f"{w}x{h} -> {p}")
