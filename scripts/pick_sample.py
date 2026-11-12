# -*- coding: utf-8 -*-
import os

base = r'C:\Music\recipes-book\public\recipe-images'
sample = []
for cat in ['cakes', 'mains', 'salads', 'soups', 'sides', 'pesach', 'desserts']:
    cat_dir = os.path.join(base, cat)
    if os.path.exists(cat_dir):
        files = [f for f in os.listdir(cat_dir) if f.upper().endswith('.JPG')]
        if files:
            sample.append(os.path.join(cat_dir, files[0]))

print("Sample files to check:", sample)
