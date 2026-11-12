# -*- coding: utf-8 -*-
import json

for b in range(1, 7):
    path = f'C:/Music/recipes-book/scripts/batches/result_img_{b}.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        non_zero = {}
        for item in data:
            rots = item.get('imageRotations', {})
            for k, v in rots.items():
                if v and v != 0:
                    non_zero[k] = v
        print(f"Batch {b}: found {len(non_zero)} rotated images: {non_zero}")
