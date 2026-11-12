# -*- coding: utf-8 -*-
import os
from PIL import Image

base = r'C:\Music\recipes-book\public\recipe-images'
p2000_1500 = []

for root, dirs, files in os.walk(base):
    if 'course-tami' in root or 'docx-media' in root:
        continue
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            p = os.path.join(root, f)
            with Image.open(p) as im:
                if im.size == (2000, 1500):
                    p2000_1500.append(p)

print(f"Found {len(p2000_1500)} images of size (2000, 1500).")
