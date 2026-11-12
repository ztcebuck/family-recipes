#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
שרת מקומי לספר המתכונים המשפחתי
Family Recipe Book Local Server (Port 8090)
"""

import argparse
import base64
import datetime
import email.parser
import json
import mimetypes
import os
import re
import sys
import threading
import time
import urllib.parse
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

try:
    from PIL import Image, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
DATA_DIR = os.path.join(BASE_DIR, "data")
RECIPES_JSON_PATH = os.path.join(DATA_DIR, "recipes.json")
SAMPLE_JSON_PATH = os.path.join(DATA_DIR, "sample-recipes.json")
UPLOADS_DIR = os.path.join(PUBLIC_DIR, "recipe-images", "uploads")

DATA_LOCK = threading.Lock()

DEFAULT_CATEGORIES = [
    {"id": "cakes", "name": "עוגות ועוגיות", "icon": "🎂"},
    {"id": "breads", "name": "לחמים ומאפים", "icon": "🥖"},
    {"id": "mains", "name": "עיקריות ובשרים", "icon": "🥩"},
    {"id": "salads", "name": "סלטים, רטבים ומטבלים", "icon": "🥗"},
    {"id": "desserts", "name": "קינוחים, מוסים וגלידות", "icon": "🍨"},
    {"id": "sides", "name": "תוספות", "icon": "🥔"},
    {"id": "pesach", "name": "מתכוני פסח", "icon": "🍷"},
    {"id": "fish", "name": "דגים", "icon": "🐟"},
    {"id": "dairy", "name": "חלבי", "icon": "🧀"},
    {"id": "starters", "name": "מנות ראשונות", "icon": "🥟"},
    {"id": "soups", "name": "מרקים", "icon": "🍲"},
]

CATEGORY_NAME_BY_ID = {c["id"]: c["name"] for c in DEFAULT_CATEGORIES}
CATEGORY_ID_BY_NAME = {c["name"]: c["id"] for c in DEFAULT_CATEGORIES}

# Ensure standard MIME types are registered
mimetypes.init()
mimetypes.add_type("application/javascript; charset=utf-8", ".js")
mimetypes.add_type("text/css; charset=utf-8", ".css")
mimetypes.add_type("text/html; charset=utf-8", ".html")
mimetypes.add_type("application/json; charset=utf-8", ".json")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("application/pdf", ".pdf")


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_recipes_data() -> dict:
    """Reads data/recipes.json if available and valid, else falls back to data/sample-recipes.json."""
    for path in (RECIPES_JSON_PATH, SAMPLE_JSON_PATH):
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "recipes" in data:
                    if not data.get("categories"):
                        data["categories"] = DEFAULT_CATEGORIES
                    if "courseGallery" not in data:
                        data["courseGallery"] = []
                    return data
            except Exception as exc:
                sys.stderr.write(f"[WARN] Failed reading {path}: {exc}\n")
    return {
        "updatedAt": now_iso(),
        "categories": DEFAULT_CATEGORIES,
        "recipes": [],
        "courseGallery": [],
    }


def save_recipes_data(data: dict) -> None:
    """Saves recipe data to data/recipes.json atomically."""
    os.makedirs(DATA_DIR, exist_ok=True)
    data["updatedAt"] = now_iso()
    temp_path = RECIPES_JSON_PATH + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, RECIPES_JSON_PATH)


def normalize_list_field(val) -> list:
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    if isinstance(val, str):
        return [line.strip() for line in val.splitlines() if line.strip()]
    return []


def build_raw_text(recipe: dict) -> str:
    parts = [
        recipe.get("title", ""),
        recipe.get("category", ""),
        recipe.get("subcategory", ""),
        recipe.get("kashrut", ""),
        "\n".join(recipe.get("ingredients", [])),
        "\n".join(recipe.get("steps", [])),
        recipe.get("notes", ""),
    ]
    existing_raw = recipe.get("rawText", "")
    combined = "\n".join(p for p in parts if p).strip()
    if existing_raw and existing_raw not in combined:
        combined = (combined + "\n" + existing_raw).strip()
    return combined


def sanitize_filename(name: str) -> str:
    base = os.path.basename(name or "upload.jpg")
    base = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", base)
    if not base or base in (".", ".."):
        base = "upload.jpg"
    return base


class RecipeRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def log_message(self, fmt, *args):
        # Clean, UTF-8 safe logging
        try:
            sys.stdout.write(f"[{self.log_date_time_string()}] {fmt % args}\n")
            sys.stdout.flush()
        except Exception:
            pass

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def translate_path(self, path: str) -> str:
        """
        Properly resolve URL-encoded Hebrew paths under PUBLIC_DIR.
        """
        parsed = urllib.parse.urlsplit(path)
        rel_path = urllib.parse.unquote(parsed.path)
        rel_path = rel_path.lstrip("/")
        if not rel_path:
            rel_path = "index.html"
        # Normalize slashes and prevent directory traversal
        norm_rel = os.path.normpath(rel_path)
        if norm_rel.startswith("..") or os.path.isabs(norm_rel):
            return os.path.join(PUBLIC_DIR, "index.html")
        full_path = os.path.abspath(os.path.join(PUBLIC_DIR, norm_rel))
        public_abs = os.path.abspath(PUBLIC_DIR)
        if not full_path.startswith(public_abs):
            return os.path.join(PUBLIC_DIR, "index.html")
        return full_path

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        route = urllib.parse.unquote(parsed.path)

        if route == "/api/recipes":
            with DATA_LOCK:
                data = load_recipes_data()
            return self.send_json(data, 200)

        if route == "/api/health":
            return self.send_json({"ok": True, "hasPil": HAS_PIL, "time": now_iso()}, 200)

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlsplit(self.path)
        route = urllib.parse.unquote(parsed.path).rstrip("/")

        try:
            if route == "/api/recipes":
                return self.handle_create_recipe()

            if route.startswith("/api/recipes/") and route.endswith("/favorite"):
                recipe_id = route[len("/api/recipes/") : -len("/favorite")].strip("/")
                return self.handle_toggle_favorite(recipe_id)

            if route == "/api/rotate-image":
                return self.handle_rotate_image()

            if route == "/api/upload":
                return self.handle_upload()

            return self.send_json({"ok": False, "error": f"Unknown endpoint: {route}"}, 404)
        except Exception as exc:
            return self.send_json({"ok": False, "error": str(exc)}, 500)

    def do_PUT(self):
        parsed = urllib.parse.urlsplit(self.path)
        route = urllib.parse.unquote(parsed.path).rstrip("/")

        try:
            if route.startswith("/api/recipes/"):
                recipe_id = route[len("/api/recipes/") :].strip("/")
                return self.handle_update_recipe(recipe_id)
            return self.send_json({"ok": False, "error": f"Unknown endpoint: {route}"}, 404)
        except Exception as exc:
            return self.send_json({"ok": False, "error": str(exc)}, 500)

    def do_DELETE(self):
        parsed = urllib.parse.urlsplit(self.path)
        route = urllib.parse.unquote(parsed.path).rstrip("/")

        try:
            if route.startswith("/api/recipes/"):
                recipe_id = route[len("/api/recipes/") :].strip("/")
                return self.handle_delete_recipe(recipe_id)
            return self.send_json({"ok": False, "error": f"Unknown endpoint: {route}"}, 404)
        except Exception as exc:
            return self.send_json({"ok": False, "error": str(exc)}, 500)

    def handle_create_recipe(self):
        body = self.read_json_body()
        title = str(body.get("title", "")).strip()
        if not title:
            return self.send_json({"ok": False, "error": "חובה להזין שם מתכון"}, 400)

        cat_id = str(body.get("categoryId", "")).strip()
        cat_name = str(body.get("category", "")).strip()
        if cat_id and not cat_name:
            cat_name = CATEGORY_NAME_BY_ID.get(cat_id, "עוגות ועוגיות")
        elif cat_name and not cat_id:
            cat_id = CATEGORY_ID_BY_NAME.get(cat_name, "cakes")
        elif not cat_id and not cat_name:
            cat_id = "cakes"
            cat_name = CATEGORY_NAME_BY_ID["cakes"]

        recipe_id = str(body.get("id", "")).strip() or f"recipe-{int(time.time()*1000)}-{uuid.uuid4().hex[:6]}"
        ingredients = normalize_list_field(body.get("ingredients", []))
        steps = normalize_list_field(body.get("steps", []))
        orig_images = normalize_list_field(body.get("originalImages", []))

        new_recipe = {
            "id": recipe_id,
            "title": title,
            "category": cat_name,
            "categoryId": cat_id,
            "subcategory": str(body.get("subcategory", "")).strip(),
            "kashrut": str(body.get("kashrut", "פרווה")).strip() or "פרווה",
            "prepTime": str(body.get("prepTime", "")).strip(),
            "servings": str(body.get("servings", "")).strip(),
            "difficulty": str(body.get("difficulty", "")).strip(),
            "ingredients": ingredients,
            "steps": steps,
            "notes": str(body.get("notes", "")).strip(),
            "rawText": str(body.get("rawText", "")).strip(),
            "originalImages": orig_images,
            "originalPdf": str(body.get("originalPdf", "")).strip(),
            "sourceType": str(body.get("sourceType", "image" if orig_images else "docx")).strip(),
            "sourceFolder": str(body.get("sourceFolder", cat_name)).strip(),
            "sourceFiles": normalize_list_field(body.get("sourceFiles", [])),
            "favorite": bool(body.get("favorite", False)),
        }
        new_recipe["rawText"] = build_raw_text(new_recipe)

        with DATA_LOCK:
            data = load_recipes_data()
            data.setdefault("recipes", []).insert(0, new_recipe)
            save_recipes_data(data)

        return self.send_json({"ok": True, "recipe": new_recipe}, 201)

    def handle_update_recipe(self, recipe_id: str):
        body = self.read_json_body()
        with DATA_LOCK:
            data = load_recipes_data()
            recipes = data.get("recipes", [])
            target = None
            for r in recipes:
                if str(r.get("id")) == recipe_id:
                    target = r
                    break

            if target is None:
                return self.send_json({"ok": False, "error": f"מתכון לא נמצא: {recipe_id}"}, 404)

            if "title" in body and str(body["title"]).strip():
                target["title"] = str(body["title"]).strip()

            if "categoryId" in body or "category" in body:
                cat_id = str(body.get("categoryId", target.get("categoryId", ""))).strip()
                cat_name = str(body.get("category", target.get("category", ""))).strip()
                if "categoryId" in body and body["categoryId"] in CATEGORY_NAME_BY_ID:
                    cat_id = body["categoryId"]
                    cat_name = CATEGORY_NAME_BY_ID[cat_id]
                elif "category" in body and body["category"] in CATEGORY_ID_BY_NAME:
                    cat_name = body["category"]
                    cat_id = CATEGORY_ID_BY_NAME[cat_name]
                target["categoryId"] = cat_id
                target["category"] = cat_name

            for str_field in ("subcategory", "kashrut", "prepTime", "servings", "difficulty", "notes", "originalPdf", "sourceType"):
                if str_field in body:
                    target[str_field] = str(body[str_field] or "").strip()

            if "ingredients" in body:
                target["ingredients"] = normalize_list_field(body["ingredients"])
            if "steps" in body:
                target["steps"] = normalize_list_field(body["steps"])
            if "originalImages" in body:
                target["originalImages"] = normalize_list_field(body["originalImages"])
            if "favorite" in body:
                target["favorite"] = bool(body["favorite"])
            if "rawText" in body and isinstance(body["rawText"], str):
                target["rawText"] = body["rawText"].strip()

            target["rawText"] = build_raw_text(target)
            save_recipes_data(data)

        return self.send_json({"ok": True, "recipe": target}, 200)

    def handle_delete_recipe(self, recipe_id: str):
        with DATA_LOCK:
            data = load_recipes_data()
            recipes = data.get("recipes", [])
            new_recipes = [r for r in recipes if str(r.get("id")) != recipe_id]
            if len(new_recipes) == len(recipes):
                return self.send_json({"ok": False, "error": f"מתכון לא נמצא: {recipe_id}"}, 404)
            data["recipes"] = new_recipes
            save_recipes_data(data)

        return self.send_json({"ok": True, "deletedId": recipe_id}, 200)

    def handle_toggle_favorite(self, recipe_id: str):
        body = {}
        try:
            body = self.read_json_body()
        except Exception:
            body = {}

        with DATA_LOCK:
            data = load_recipes_data()
            target = None
            for r in data.get("recipes", []):
                if str(r.get("id")) == recipe_id:
                    target = r
                    break

            if target is None:
                return self.send_json({"ok": False, "error": f"מתכון לא נמצא: {recipe_id}"}, 404)

            if "favorite" in body:
                target["favorite"] = bool(body["favorite"])
            else:
                target["favorite"] = not bool(target.get("favorite", False))

            save_recipes_data(data)

        return self.send_json(
            {"ok": True, "id": recipe_id, "favorite": target["favorite"], "recipe": target},
            200,
        )

    def handle_rotate_image(self):
        if not HAS_PIL:
            return self.send_json({"ok": False, "error": "ספריית Pillow אינה מותקנת בשרת"}, 500)

        body = self.read_json_body()
        raw_image_path = str(body.get("imagePath", "")).strip()
        degrees = int(body.get("degrees", 90))

        if not raw_image_path:
            return self.send_json({"ok": False, "error": "חסר נתיב תמונה (imagePath)"}, 400)

        # Strip query params (?t=...) and decode URL encoding
        parsed_img = urllib.parse.urlsplit(raw_image_path)
        clean_web_path = urllib.parse.unquote(parsed_img.path)
        rel_path = clean_web_path.lstrip("/")
        full_path = os.path.abspath(os.path.join(PUBLIC_DIR, os.path.normpath(rel_path)))
        public_abs = os.path.abspath(PUBLIC_DIR)

        if not full_path.startswith(public_abs) or not os.path.isfile(full_path):
            return self.send_json({"ok": False, "error": f"קובץ התמונה לא נמצא: {clean_web_path}"}, 404)

        # Normalize degrees to 90 (clockwise), 270/-90 (counter-clockwise), 180
        norm_deg = degrees % 360
        with Image.open(full_path) as img:
            img_Format = img.format
            img = ImageOps.exif_transpose(img)
            if norm_deg == 90:
                # 90 degrees clockwise = ROTATE_270 in PIL
                rotated = img.transpose(Image.Transpose.ROTATE_270)
            elif norm_deg == 270:
                # 90 degrees counter-clockwise = ROTATE_90 in PIL
                rotated = img.transpose(Image.Transpose.ROTATE_90)
            elif norm_deg == 180:
                rotated = img.transpose(Image.Transpose.ROTATE_180)
            else:
                rotated = img.rotate(-norm_deg, expand=True)

            save_kwargs = {}
            ext = os.path.splitext(full_path)[1].lower()
            if ext in (".jpg", ".jpeg") or img_Format == "JPEG":
                if rotated.mode in ("RGBA", "P"):
                    rotated = rotated.convert("RGB")
                save_kwargs["quality"] = 92
            rotated.save(full_path, **save_kwargs)

        cache_busted = f"{clean_web_path}?t={int(time.time() * 1000)}"
        return self.send_json({"ok": True, "imagePath": clean_web_path, "imageUrl": cache_busted}, 200)

    def handle_upload(self):
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        content_type = self.headers.get("Content-Type", "")

        if "multipart/form-data" in content_type:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw_body = self.rfile.read(length)
            header_bytes = f"Content-Type: {content_type}\r\n\r\n".encode("utf-8")
            msg = email.parser.BytesParser().parsebytes(header_bytes + raw_body)

            for part in msg.walk():
                filename = part.get_filename()
                if filename:
                    safe_name = f"{int(time.time()*1000)}-{sanitize_filename(filename)}"
                    dest_path = os.path.join(UPLOADS_DIR, safe_name)
                    file_bytes = part.get_payload(decode=True)
                    with open(dest_path, "wb") as f:
                        f.write(file_bytes)
                    web_url = f"/recipe-images/uploads/{safe_name}"
                    return self.send_json({"ok": True, "imageUrl": web_url}, 201)

            return self.send_json({"ok": False, "error": "לא נמצא קובץ בהעלאה"}, 400)

        # JSON base64 upload
        body = self.read_json_body()
        filename = sanitize_filename(str(body.get("filename", "recipe-photo.jpg")))
        data_url = str(body.get("dataUrl") or body.get("data") or "").strip()
        if not data_url:
            return self.send_json({"ok": False, "error": "לא התקבל תוכן תמונה"}, 400)

        if "," in data_url and data_url.startswith("data:"):
            _, b64_part = data_url.split(",", 1)
        else:
            b64_part = data_url

        file_bytes = base64.b64decode(b64_part)
        safe_name = f"{int(time.time()*1000)}-{filename}"
        dest_path = os.path.join(UPLOADS_DIR, safe_name)
        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        web_url = f"/recipe-images/uploads/{safe_name}"
        return self.send_json({"ok": True, "imageUrl": web_url}, 201)


def main():
    parser = argparse.ArgumentParser(description="Family Recipe Book Server")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8090")),
        help="Port to run the server on (default: 8090)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host interface to bind (default: 0.0.0.0)",
    )
    args = parser.parse_args()

    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    server = ThreadingHTTPServer((args.host, args.port), RecipeRequestHandler)
    print("=" * 60)
    print(f"  ספר המתכונים המשפחתי פועל בכתובת: http://localhost:{args.port}")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nסוגר את השרת...")
        server.server_close()


if __name__ == "__main__":
    main()
