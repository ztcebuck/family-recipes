# -*- coding: utf-8 -*-
import os
from PIL import Image

base = r'C:\Music\recipes-book\public\recipe-images'
wide_info = []

for root, dirs, files in os.walk(base):
    if 'course-tami' in root or 'docx-media' in root:
        continue
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            p = os.path.join(root, f)
            with Image.open(p) as im:
                w, h = im.size
                if w > h:
                    wide_info.append((w, h, p, f))

print(f"Total wide images: {len(wide_info)}")
# group by (w, h)
from collections import Counter
dims = Counter((w, h) for w, h, p, f in wide_info)
print("Dimensions:", dims)

# Let's inspect images whose dimensions are NOT 2000x1500
non_std = [item for item in wide_info if (item[0], item[1]) != (2000, 1500)]
print(f"Non 2000x1500 wide images ({len(non_std)}):")
for item in non_std:
    print(item[0], item[1], item[3])
