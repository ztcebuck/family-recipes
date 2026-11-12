/**
 * ספר המתכונים המשפחתי — אפליקציית צד-לקוח מלאה
 * Family Recipe Book Frontend Application
 */

(function () {
  "use strict";

  const DEFAULT_CATEGORIES = [
    { id: "cakes", name: "עוגות ועוגיות", icon: "🎂" },
    { id: "breads", name: "לחמים ומאפים", icon: "🥖" },
    { id: "mains", name: "עיקריות ובשרים", icon: "🥩" },
    { id: "salads", name: "סלטים, רטבים ומטבלים", icon: "🥗" },
    { id: "desserts", name: "קינוחים, מוסים וגלידות", icon: "🍨" },
    { id: "sides", name: "תוספות", icon: "🥔" },
    { id: "pesach", name: "מתכוני פסח", icon: "🍷" },
    { id: "fish", name: "דגים", icon: "🐟" },
    { id: "dairy", name: "חלבי", icon: "🧀" },
    { id: "starters", name: "מנות ראשונות", icon: "🥟" },
    { id: "soups", name: "מרקים", icon: "🍲" },
  ];

  // Application State
  const state = {
    categories: [...DEFAULT_CATEGORIES],
    recipes: [],
    courseGallery: [],
    activeCategoryId: "all", // 'all' | 'favorites' | 'course-gallery' | category.id
    searchQuery: "",
    kashrutFilter: "all", // 'all' | 'פרווה' | 'חלבי' | 'בשרי' | 'פסח'
    sourceFilter: "all", // 'all' | 'with-image' | 'typed' | 'pdf'
    sortBy: "alpha", // 'alpha' | 'favorites' | 'category' | 'with-images'

    // Currently open recipe in Detail Modal
    currentRecipeId: null,
    currentMultiplier: 1,
    checkedIngredients: new Set(),
    activeStepIndex: null,
    currentImageIndex: 0,
    imageCacheBusters: {}, // rawPath -> cacheBustedUrl
    kitchenMode: false,
    wakeLockSentinel: null,

    // Lightbox State
    lightboxImages: [], // array of { rawPath, title }
    lightboxIndex: 0,
    lightboxZoom: 1,

    // Form Modal State
    editingRecipeId: null,
    formUploadedImages: [],
  };

  // DOM Elements
  const els = {};

  function cacheElements() {
    els.brandHomeBtn = document.getElementById("brandHomeBtn");
    els.statTotalCount = document.getElementById("statTotalCount");
    els.statFavCount = document.getElementById("statFavCount");
    els.statImageCount = document.getElementById("statImageCount");

    els.randomRecipeBtn = document.getElementById("randomRecipeBtn");
    els.refreshDataBtn = document.getElementById("refreshDataBtn");
    els.addNewRecipeBtn = document.getElementById("addNewRecipeBtn");

    els.searchInput = document.getElementById("searchInput");
    els.clearSearchBtn = document.getElementById("clearSearchBtn");
    els.quickSearchTags = document.getElementById("quickSearchTags");
    els.kashrutFilterGroup = document.getElementById("kashrutFilterGroup");
    els.sourceFilterGroup = document.getElementById("sourceFilterGroup");
    els.sortSelect = document.getElementById("sortSelect");

    els.categoryNav = document.getElementById("categoryNav");
    els.activeCategoryTitle = document.getElementById("activeCategoryTitle");
    els.resultsCountBadge = document.getElementById("resultsCountBadge");
    els.resetFiltersBtn = document.getElementById("resetFiltersBtn");

    els.recipesGrid = document.getElementById("recipesGrid");
    els.courseGallerySection = document.getElementById("courseGallerySection");
    els.courseGalleryGrid = document.getElementById("courseGalleryGrid");
    els.emptyState = document.getElementById("emptyState");
    els.emptyResetBtn = document.getElementById("emptyResetBtn");

    // Detail Modal
    els.recipeDetailModal = document.getElementById("recipeDetailModal");
    els.recipeModalCard = document.getElementById("recipeModalCard");
    els.closeDetailModalBtn = document.getElementById("closeDetailModalBtn");
    els.toggleKitchenModeBtn = document.getElementById("toggleKitchenModeBtn");
    els.kitchenModeBtnLabel = document.getElementById("kitchenModeBtnLabel");
    els.kitchenActiveBanner = document.getElementById("kitchenActiveBanner");
    els.wakeLockStatusText = document.getElementById("wakeLockStatusText");
    els.exitKitchenModeBtn = document.getElementById("exitKitchenModeBtn");

    els.detailFavBtn = document.getElementById("detailFavBtn");
    els.detailFavIcon = document.getElementById("detailFavIcon");
    els.editCurrentRecipeBtn = document.getElementById("editCurrentRecipeBtn");
    els.shareWhatsappBtn = document.getElementById("shareWhatsappBtn");
    els.printRecipeBtn = document.getElementById("printRecipeBtn");

    els.detailBadges = document.getElementById("detailBadges");
    els.detailRecipeTitle = document.getElementById("detailRecipeTitle");
    els.detailMetaRow = document.getElementById("detailMetaRow");
    els.detailHybridGrid = document.getElementById("detailHybridGrid");

    els.detailIngredientsSection = document.getElementById("detailIngredientsSection");
    els.detailIngredientsList = document.getElementById("detailIngredientsList");
    els.resetCheckedIngredientsBtn = document.getElementById("resetCheckedIngredientsBtn");
    els.detailStepsSection = document.getElementById("detailStepsSection");
    els.detailStepsList = document.getElementById("detailStepsList");
    els.detailRawTextSection = document.getElementById("detailRawTextSection");
    els.detailRawTextBox = document.getElementById("detailRawTextBox");
    els.detailNotesSection = document.getElementById("detailNotesSection");
    els.detailNotesContent = document.getElementById("detailNotesContent");

    els.detailMediaCol = document.getElementById("detailMediaCol");
    els.detailImagePageBadge = document.getElementById("detailImagePageBadge");
    els.detailImagePageSwitcher = document.getElementById("detailImagePageSwitcher");
    els.detailImageStage = document.getElementById("detailImageStage");
    els.detailMainImage = document.getElementById("detailMainImage");
    els.detailImageControlsBar = document.getElementById("detailImageControlsBar");
    els.openLightboxBtn = document.getElementById("openLightboxBtn");
    els.rotateRightBtn = document.getElementById("rotateRightBtn");
    els.rotateLeftBtn = document.getElementById("rotateLeftBtn");
    els.detailThumbsStrip = document.getElementById("detailThumbsStrip");

    els.detailPdfBox = document.getElementById("detailPdfBox");
    els.detailPdfLink = document.getElementById("detailPdfLink");
    els.toggleEmbeddedPdfBtn = document.getElementById("toggleEmbeddedPdfBtn");
    els.detailPdfIframe = document.getElementById("detailPdfIframe");
    els.detailSourceProvenance = document.getElementById("detailSourceProvenance");

    // Lightbox
    els.lightboxModal = document.getElementById("lightboxModal");
    els.lightboxTitle = document.getElementById("lightboxTitle");
    els.lightboxCounter = document.getElementById("lightboxCounter");
    els.lightboxImgWrapper = document.getElementById("lightboxImgWrapper");
    els.lightboxImg = document.getElementById("lightboxImg");
    els.lbZoomInBtn = document.getElementById("lbZoomInBtn");
    els.lbZoomOutBtn = document.getElementById("lbZoomOutBtn");
    els.lbZoomResetBtn = document.getElementById("lbZoomResetBtn");
    els.lbRotateRightBtn = document.getElementById("lbRotateRightBtn");
    els.lbRotateLeftBtn = document.getElementById("lbRotateLeftBtn");
    els.lbCloseBtn = document.getElementById("lbCloseBtn");
    els.lbPrevBtn = document.getElementById("lbPrevBtn");
    els.lbNextBtn = document.getElementById("lbNextBtn");

    // Form Modal
    els.recipeFormModal = document.getElementById("recipeFormModal");
    els.formModalTitle = document.getElementById("formModalTitle");
    els.closeFormModalBtn = document.getElementById("closeFormModalBtn");
    els.cancelFormModalBtn = document.getElementById("cancelFormModalBtn");
    els.recipeForm = document.getElementById("recipeForm");
    els.formRecipeId = document.getElementById("formRecipeId");
    els.formTitle = document.getElementById("formTitle");
    els.formCategory = document.getElementById("formCategory");
    els.formKashrut = document.getElementById("formKashrut");
    els.formSubcategory = document.getElementById("formSubcategory");
    els.formPrepTime = document.getElementById("formPrepTime");
    els.formServings = document.getElementById("formServings");
    els.formIngredients = document.getElementById("formIngredients");
    els.formSteps = document.getElementById("formSteps");
    els.formNotes = document.getElementById("formNotes");
    els.formImageUpload = document.getElementById("formImageUpload");
    els.uploadStatusText = document.getElementById("uploadStatusText");
    els.formUploadedImagesList = document.getElementById("formUploadedImagesList");

    els.toastContainer = document.getElementById("toastContainer");
  }

  // =========================================================================
  // HELPERS & ASSET URL ENCODING
  // =========================================================================

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function stripQuery(url) {
    return String(url || "").split("?")[0];
  }

  /**
   * Safely encodes Hebrew characters and spaces in asset URLs without double-encoding.
   * Respects any cache-buster recorded in state.imageCacheBusters.
   */
  function resolveAssetUrl(rawUrl) {
    if (!rawUrl) return "";
    const cleanBase = stripQuery(rawUrl);
    const activeUrl = state.imageCacheBusters[cleanBase] || rawUrl;
    const [pathPart, queryPart] = String(activeUrl).split("?");
    // Remove leading slash so assets resolve relative to current repository/subpath
    const trimmedPath = pathPart.replace(/^\/+/, "");
    const encodedPath = trimmedPath
      .split("/")
      .map((seg) => {
        if (!seg) return "";
        try {
          return encodeURIComponent(decodeURIComponent(seg));
        } catch (_) {
          return encodeURIComponent(seg);
        }
      })
      .join("/");
    return queryPart ? `${encodedPath}?${queryPart}` : encodedPath;
  }

  function showToast(message) {
    if (!els.toastContainer) return;
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    els.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.25s ease";
      setTimeout(() => toast.remove(), 260);
    }, 3200);
  }

  function getCategoryMeta(categoryId, categoryName) {
    const found =
      state.categories.find((c) => c.id === categoryId) ||
      state.categories.find((c) => c.name === categoryName);
    return found || { id: categoryId || "cakes", name: categoryName || "מתכונים", icon: "🍲" };
  }

  function isPesachRecipe(r) {
    if (!r) return false;
    return (
      r.categoryId === "pesach" ||
      (r.category && r.category.includes("פסח")) ||
      (r.kashrut && r.kashrut.includes("פסח")) ||
      (r.subcategory && r.subcategory.includes("פסח")) ||
      (r.sourceFolder && r.sourceFolder.includes("פסח"))
    );
  }

  function hasOriginalImages(r) {
    return Array.isArray(r.originalImages) && r.originalImages.length > 0;
  }

  function hasOriginalPdf(r) {
    return Boolean(r.originalPdf && String(r.originalPdf).trim());
  }

  function isTypedRecipe(r) {
    const hasStructured =
      (Array.isArray(r.ingredients) && r.ingredients.length > 0) ||
      (Array.isArray(r.steps) && r.steps.length > 0);
    return r.sourceType === "docx" || r.sourceType === "txt" || hasStructured;
  }

  // =========================================================================
  // QUANTITY MULTIPLIER & FRACTION SCALING ENGINE
  // =========================================================================

  const UNICODE_FRACTIONS = {
    "½": 0.5,
    "⅓": 1 / 3,
    "⅔": 2 / 3,
    "¼": 0.25,
    "¾": 0.75,
    "⅕": 0.2,
    "⅖": 0.4,
    "⅗": 0.6,
    "⅘": 0.8,
    "⅙": 1 / 6,
    "⅚": 5 / 6,
    "⅛": 0.125,
    "⅜": 0.375,
    "⅝": 0.625,
    "⅞": 0.875,
  };

  function formatCulinaryNumber(val) {
    if (!Number.isFinite(val) || val <= 0) return String(val);
    const rounded = Math.round(val * 100) / 100;
    const whole = Math.floor(rounded + 1e-6);
    const frac = rounded - whole;

    const fracCandidates = [
      { v: 0, s: "" },
      { v: 0.125, s: "1/8" },
      { v: 0.25, s: "1/4" },
      { v: 1 / 3, s: "1/3" },
      { v: 0.375, s: "3/8" },
      { v: 0.5, s: "1/2" },
      { v: 0.625, s: "5/8" },
      { v: 2 / 3, s: "2/3" },
      { v: 0.75, s: "3/4" },
      { v: 0.875, s: "7/8" },
      { v: 1, s: "" },
    ];

    let best = null;
    let minDiff = 0.045;
    for (const c of fracCandidates) {
      const d = Math.abs(frac - c.v);
      if (d < minDiff) {
        minDiff = d;
        best = c;
      }
    }

    if (best) {
      if (best.v === 1) return String(whole + 1);
      if (best.v === 0) return String(whole);
      if (whole === 0) return best.s;
      return `${whole} ו-${best.s}`;
    }

    return Number(rounded.toFixed(2)).toString();
  }

  /**
   * Identifies whether an ingredient line is a section header (e.g. "לבצק:", "למילוי:", "לרוטב:")
   */
  function isIngredientSectionHeader(line) {
    if (!line) return false;
    const clean = String(line).trim();
    if (!clean || clean.length > 50) return false;

    // Must NOT contain digits or fractions (headers never specify quantity)
    if (/[0-9½⅓⅔¼¾]/.test(clean)) return false;

    // Must NOT contain measurement units
    if (/(כוס|כפות|כף|כפיות|כפית|גרם|ג'|ק"ג|קילו|חבילה|חבילות|חב'|קופסה|קופסאות|טיפות|מ"ל|ליטר)/.test(clean)) {
      return false;
    }

    // Explicit ends with colon or full-width colon
    if (clean.endsWith(":") || clean.endsWith("：")) {
      return true;
    }

    // Common section header prefixes or exact titles (even without colon)
    const headerPrefixes = [
      "לבצק", "למילוי", "לרוטב", "לציפוי", "לקרם", "להרכבה", "לפיזור", "להברשה",
      "להגשה", "לקישוט", "לטבילה", "לסירופ", "לבסיס", "לתחתית", "לשכבה", "למוס",
      "למרנג", "לקראמבל", "לקונפי", "לחומרים", "חומרים ל", "מצרכים ל", "מרכיבים ל",
      "שכבה א", "שכבה ב", "שכבה ג", "שכבה ראשונה", "שכבה שנייה", "שכבה שלישית",
      "בצק", "מילוי", "רוטב", "ציפוי", "קרם", "סירופ", "בסיס", "תחתית"
    ];

    for (const prefix of headerPrefixes) {
      if (clean === prefix || clean.startsWith(prefix + " ") || clean.startsWith(prefix + ":")) {
        return true;
      }
    }

    return false;
  }

  function getIngredientHeaderIcon(headerText) {
    const text = String(headerText || "").toLowerCase();
    if (text.includes("בצק") || text.includes("בסיס") || text.includes("תחתית")) return "🥣";
    if (text.includes("מילוי") || text.includes("קרם") || text.includes("מוס") || text.includes("מרנג")) return "🍯";
    if (text.includes("רוטב") || text.includes("סירופ") || text.includes("מרינדה")) return "🫗";
    if (text.includes("ציפוי") || text.includes("גלזורה")) return "✨";
    if (text.includes("הברשה") || text.includes("פיזור") || text.includes("קישוט") || text.includes("הגשה")) return "🌿";
    if (text.includes("שכבה")) return "🥞";
    return "📌";
  }

  /**
   * Scales ingredient line quantities cleanly and highlights modified amounts.
   */
  function scaleIngredientLineHtml(line, mult) {
    const raw = String(line || "").trim();
    if (!raw) return "";
    if (mult === 1) return escapeHtml(raw);

    // Replace unicode fractions with slash fractions first for uniform parsing
    let normalized = raw.replace(/[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]/g, (m) => {
      const map = {
        "½": " 1/2 ",
        "⅓": " 1/3 ",
        "⅔": " 2/3 ",
        "¼": " 1/4 ",
        "¾": " 3/4 ",
        "⅛": " 1/8 ",
        "⅜": " 3/8 ",
        "⅝": " 5/8 ",
        "⅞": " 7/8 ",
      };
      return map[m] || m;
    }).replace(/\s+/g, " ").trim();

    // Matches:
    // 1) "2 ו-1/2" or "2 ו 1/2"
    // 2) "1/2 2" or "2 1/2" (mixed number in either RTL/LTR order)
    // 3) "3/4" (slash fraction)
    // 4) "2.5" or "200" (decimal or integer)
    const tokenRegex =
      /(\d+\s*ו-?\s*\d+\s*\/\s*\d+)|(\d+\s*\/\s*\d+\s+\d+)|(\d+\s+\d+\s*\/\s*\d+)|(\d+\s*\/\s*\d+)|(\d+(?:\.\d+)?)/g;

    let resultHtml = "";
    let lastIndex = 0;
    let match;

    while ((match = tokenRegex.exec(normalized)) !== null) {
      const fullMatch = match[0];
      const idx = match.index;
      const beforeText = normalized.slice(lastIndex, idx);
      const afterSlice = normalized.slice(idx + fullMatch.length, idx + fullMatch.length + 14);

      resultHtml += escapeHtml(beforeText);

      // Don't scale temperatures ("180 מעלות") or percentage ("5%", "3%")
      const isTempOrPercent =
        /^\s*(מעלות|°|%)/.test(afterSlice) || /תבנית\s*$/.test(beforeText);

      if (isTempOrPercent) {
        resultHtml += escapeHtml(fullMatch);
      } else {
        let numericValue = NaN;
        if (match[1]) {
          // e.g. "2 ו-1/2"
          const parts = fullMatch.split(/ו-?/);
          const w = parseFloat(parts[0].trim());
          const [n, d] = parts[1].split("/").map((s) => parseFloat(s.trim()));
          if (d) numericValue = w + n / d;
        } else if (match[2]) {
          // e.g. "1/2 2"
          const parts = fullMatch.trim().split(/\s+/);
          const [n, d] = parts[0].split("/").map((s) => parseFloat(s.trim()));
          const w = parseFloat(parts[1]);
          if (d) numericValue = w + n / d;
        } else if (match[3]) {
          // e.g. "2 1/2"
          const parts = fullMatch.trim().split(/\s+/);
          const w = parseFloat(parts[0]);
          const [n, d] = parts[1].split("/").map((s) => parseFloat(s.trim()));
          if (d) numericValue = w + n / d;
        } else if (match[4]) {
          // e.g. "3/4"
          const [n, d] = fullMatch.split("/").map((s) => parseFloat(s.trim()));
          if (d) numericValue = n / d;
        } else if (match[5]) {
          numericValue = parseFloat(fullMatch);
        }

        if (Number.isFinite(numericValue) && numericValue > 0) {
          const scaled = formatCulinaryNumber(numericValue * mult);
          resultHtml += `<span class="scaled-num">${escapeHtml(scaled)}</span>`;
        } else {
          resultHtml += escapeHtml(fullMatch);
        }
      }

      lastIndex = idx + fullMatch.length;
    }

    resultHtml += escapeHtml(normalized.slice(lastIndex));
    return resultHtml;
  }

  // =========================================================================
  // DATA LOADING & API CALLS
  // =========================================================================

  async function fetchRecipesData(showToastOnComplete = false) {
    try {
      let res = await fetch("/api/recipes", { cache: "no-store" }).catch(() => null);
      if (!res || !res.ok) {
        // Fallback for static hosting (e.g. GitHub Pages)
        res = await fetch("data/recipes.json", { cache: "no-store" }).catch(() => null);
      }
      if (!res || !res.ok) throw new Error(`HTTP ${res ? res.status : "network error"}`);
      const data = await res.json();

      if (Array.isArray(data.categories) && data.categories.length > 0) {
        state.categories = data.categories;
      }
      state.recipes = Array.isArray(data.recipes) ? data.recipes : [];
      state.courseGallery = Array.isArray(data.courseGallery) ? data.courseGallery : [];

      renderAll();

      // Check URL hash for direct recipe link
      handleHashNavigation();

      if (showToastOnComplete) {
        showToast(`נטענו ${state.recipes.length} מתכונים בהצלחה!`);
      }
    } catch (err) {
      console.error("Failed loading recipes:", err);
      showToast("שגיאה בטעינת המתכונים מהשרת");
    }
  }

  async function toggleRecipeFavorite(recipeId, event) {
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }
    const recipe = state.recipes.find((r) => String(r.id) === String(recipeId));
    if (!recipe) return;

    const newFav = !recipe.favorite;
    recipe.favorite = newFav;
    renderHeaderStats();
    renderCategoryNav();
    renderMainContent();
    if (state.currentRecipeId === recipeId) {
      updateDetailFavButton(newFav);
    }

    try {
      const res = await fetch(`/api/recipes/${encodeURIComponent(recipeId)}/favorite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ favorite: newFav }),
      });
      if (res.ok) {
        showToast(newFav ? "נוסף למועדפים ⭐" : "הוסר מהמועדפים");
      }
    } catch (err) {
      console.error("Failed toggling favorite:", err);
    }
  }

  async function rotateImageOnServer(rawImagePath, degrees) {
    if (!rawImagePath) return;
    const cleanPath = stripQuery(rawImagePath);
    try {
      showToast("מסובב ושומר תמונה...");
      const res = await fetch("/api/rotate-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ imagePath: cleanPath, degrees }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data.error || "שגיאה בסיבוב התמונה");
      }

      // Store cache-busted URL so all views immediately reload the rotated image
      state.imageCacheBusters[cleanPath] = data.imageUrl;

      // Refresh current detail modal image if open
      if (state.currentRecipeId) {
        const currentRecipe = getCurrentRecipe();
        if (currentRecipe) {
          renderDetailMediaColumn(currentRecipe);
        }
      }

      // Refresh lightbox image if open
      if (!els.lightboxModal.classList.contains("hidden")) {
        renderLightboxSlide();
      }

      // Refresh grid thumbnails
      renderMainContent();
      showToast("התמונה סובבה ונשמרה לצמיתות ✓");
    } catch (err) {
      console.error("Rotate error:", err);
      showToast("שגיאה בסיבוב התמונה: " + err.message);
    }
  }

  // =========================================================================
  // FILTERING & SORTING
  // =========================================================================

  function matchesActiveFilters(r, ignoreCategory = false) {
    // 1. Category Filter
    if (!ignoreCategory) {
      if (state.activeCategoryId === "favorites") {
        if (!r.favorite) return false;
      } else if (
        state.activeCategoryId !== "all" &&
        state.activeCategoryId !== "course-gallery"
      ) {
        const catMeta = getCategoryMeta(state.activeCategoryId, "");
        const matchCat =
          r.categoryId === state.activeCategoryId || r.category === catMeta.name;
        if (!matchCat) return false;
      }
    }

    // 2. Kashrut Filter
    if (state.kashrutFilter !== "all") {
      if (state.kashrutFilter === "פסח") {
        if (!isPesachRecipe(r)) return false;
      } else {
        if ((r.kashrut || "פרווה") !== state.kashrutFilter) return false;
      }
    }

    // 3. Source Type Filter
    if (state.sourceFilter !== "all") {
      if (state.sourceFilter === "with-image" && !hasOriginalImages(r)) return false;
      if (state.sourceFilter === "typed" && !isTypedRecipe(r)) return false;
      if (state.sourceFilter === "pdf" && !hasOriginalPdf(r) && r.sourceType !== "pdf") {
        return false;
      }
    }

    // 4. Search Query
    if (state.searchQuery.trim()) {
      const terms = state.searchQuery
        .trim()
        .toLowerCase()
        .split(/\s+/)
        .filter(Boolean);

      const haystack = [
        r.title || "",
        r.category || "",
        r.subcategory || "",
        r.kashrut || "",
        (r.ingredients || []).join(" "),
        (r.steps || []).join(" "),
        r.notes || "",
        r.rawText || "",
      ]
        .join(" ")
        .toLowerCase();

      for (const term of terms) {
        if (!haystack.includes(term)) return false;
      }
    }

    return true;
  }

  function getFilteredAndSortedRecipes() {
    const filtered = state.recipes.filter((r) => matchesActiveFilters(r, false));

    filtered.sort((a, b) => {
      if (state.sortBy === "favorites") {
        if (Boolean(a.favorite) !== Boolean(b.favorite)) {
          return a.favorite ? -1 : 1;
        }
      } else if (state.sortBy === "category") {
        const catCmp = String(a.category || "").localeCompare(String(b.category || ""), "he");
        if (catCmp !== 0) return catCmp;
      } else if (state.sortBy === "with-images") {
        const aImg = hasOriginalImages(a);
        const bImg = hasOriginalImages(b);
        if (aImg !== bImg) return aImg ? -1 : 1;
      }
      return String(a.title || "").localeCompare(String(b.title || ""), "he");
    });

    return filtered;
  }

  // =========================================================================
  // RENDERING: HEADER STATS, SIDEBAR & MAIN GRID
  // =========================================================================

  function renderAll() {
    renderHeaderStats();
    renderCategoryNav();
    renderMainContent();
  }

  function renderHeaderStats() {
    const total = state.recipes.length;
    const favs = state.recipes.filter((r) => r.favorite).length;
    const withImages = state.recipes.filter((r) => hasOriginalImages(r)).length;

    els.statTotalCount.textContent = total.toLocaleString("he-IL");
    els.statFavCount.textContent = favs.toLocaleString("he-IL");
    els.statImageCount.textContent = withImages.toLocaleString("he-IL");
  }

  function renderCategoryNav() {
    const totalCount = state.recipes.length;
    const favCount = state.recipes.filter((r) => r.favorite).length;

    // Count per category
    const countsByCatId = {};
    for (const c of state.categories) countsByCatId[c.id] = 0;
    for (const r of state.recipes) {
      const cid = r.categoryId || getCategoryMeta("", r.category).id;
      countsByCatId[cid] = (countsByCatId[cid] || 0) + 1;
    }

    let html = `
      <button type="button" class="cat-nav-btn ${state.activeCategoryId === "all" ? "active" : ""}" data-cat="all">
        <span class="cat-nav-left">
          <span class="cat-nav-icon">📖</span>
          <span class="cat-nav-name">כל המתכונים</span>
        </span>
        <span class="cat-nav-count">${totalCount}</span>
      </button>

      <button type="button" class="cat-nav-btn ${state.activeCategoryId === "favorites" ? "active" : ""}" data-cat="favorites">
        <span class="cat-nav-left">
          <span class="cat-nav-icon">⭐</span>
          <span class="cat-nav-name">מועדפים</span>
        </span>
        <span class="cat-nav-count">${favCount}</span>
      </button>

      <div class="cat-nav-divider"></div>
    `;

    for (const cat of state.categories) {
      const count = countsByCatId[cat.id] || 0;
      const isActive = state.activeCategoryId === cat.id;
      html += `
        <button type="button" class="cat-nav-btn ${isActive ? "active" : ""}" data-cat="${escapeHtml(cat.id)}">
          <span class="cat-nav-left">
            <span class="cat-nav-icon">${escapeHtml(cat.icon || "🍲")}</span>
            <span class="cat-nav-name">${escapeHtml(cat.name)}</span>
          </span>
          <span class="cat-nav-count">${count}</span>
        </button>
      `;
    }

    if (state.courseGallery && state.courseGallery.length > 0) {
      const isGallery = state.activeCategoryId === "course-gallery";
      html += `
        <div class="cat-nav-divider"></div>
        <button type="button" class="cat-nav-btn ${isGallery ? "active" : ""}" data-cat="course-gallery">
          <span class="cat-nav-left">
            <span class="cat-nav-icon">📸</span>
            <span class="cat-nav-name">גלריית קורס תמי פיליפ</span>
          </span>
          <span class="cat-nav-count">${state.courseGallery.length}</span>
        </button>
      `;
    }

    els.categoryNav.innerHTML = html;
  }

  function buildRecipePreviewSnippet(r) {
    if (Array.isArray(r.ingredients) && r.ingredients.length > 0) {
      return "מצרכים: " + r.ingredients.slice(0, 4).join(" • ");
    }
    if (Array.isArray(r.steps) && r.steps.length > 0) {
      return r.steps.slice(0, 2).join(" ");
    }
    if (r.rawText) {
      const cleaned = r.rawText
        .replace(r.title || "", "")
        .replace(/\s+/g, " ")
        .trim();
      if (cleaned) return cleaned.slice(0, 120);
    }
    if (hasOriginalImages(r)) {
      return "מתכון מצולם מקורי — לחצו לצפייה בצילום המלא ובהגדלה";
    }
    return "לחצו לצפייה במתכון המלא";
  }

  function getSourceLabelBadge(r) {
    const imgCount = Array.isArray(r.originalImages) ? r.originalImages.length : 0;
    if (imgCount > 1) return `📷 ${imgCount} עמודים`;
    if (imgCount === 1 && r.sourceType === "image") return "📷 צילום מקורי";
    if (hasOriginalPdf(r) || r.sourceType === "pdf") return "📄 קובץ PDF";
    if (imgCount === 1) return "📝 מתכון + תמונה";
    return "📝 מתכון מוקלד";
  }

  function renderMainContent() {
    const hasNonDefaultFilters =
      state.activeCategoryId !== "all" ||
      state.searchQuery.trim() !== "" ||
      state.kashrutFilter !== "all" ||
      state.sourceFilter !== "all";
    els.resetFiltersBtn.classList.toggle("hidden", !hasNonDefaultFilters);

    // Handle Course Tami Philip Gallery tab
    if (state.activeCategoryId === "course-gallery") {
      els.activeCategoryTitle.textContent = "📸 גלריית קורס תמי פיליפ";
      const q = state.searchQuery.trim().toLowerCase();
      const items = state.courseGallery.filter(
        (g) => !q || String(g.title || "").toLowerCase().includes(q)
      );
      els.resultsCountBadge.textContent = `${items.length} תמונות`;
      els.recipesGrid.classList.add("hidden");
      els.emptyState.classList.add("hidden");
      els.courseGallerySection.classList.remove("hidden");

      els.courseGalleryGrid.innerHTML = items
        .map((item, idx) => {
          const imgUrl = resolveAssetUrl(item.imageUrl);
          return `
            <div class="gallery-photo-card" data-gallery-idx="${idx}">
              <img src="${escapeHtml(imgUrl)}" alt="${escapeHtml(item.title)}" loading="lazy" />
              <div class="gallery-photo-caption">
                <span>${escapeHtml(item.title)}</span>
                <span>🔍</span>
              </div>
            </div>
          `;
        })
        .join("");
      return;
    }

    els.courseGallerySection.classList.add("hidden");

    // Set Category Heading
    if (state.activeCategoryId === "all") {
      els.activeCategoryTitle.textContent = "כל המתכונים";
    } else if (state.activeCategoryId === "favorites") {
      els.activeCategoryTitle.textContent = "⭐ מתכונים מועדפים";
    } else {
      const catMeta = getCategoryMeta(state.activeCategoryId, "");
      els.activeCategoryTitle.textContent = `${catMeta.icon} ${catMeta.name}`;
    }

    const filtered = getFilteredAndSortedRecipes();
    els.resultsCountBadge.textContent = `${filtered.length} מתכונים`;

    if (filtered.length === 0) {
      els.recipesGrid.classList.add("hidden");
      els.emptyState.classList.remove("hidden");
      return;
    }

    els.emptyState.classList.add("hidden");
    els.recipesGrid.classList.remove("hidden");

    els.recipesGrid.innerHTML = filtered
      .map((r) => {
        const catMeta = getCategoryMeta(r.categoryId, r.category);
        const kashrut = r.kashrut || "פרווה";
        const hasImg = hasOriginalImages(r);
        const thumbUrl = hasImg ? resolveAssetUrl(r.originalImages[0]) : "";
        const sourceBadge = getSourceLabelBadge(r);
        const snippet = buildRecipePreviewSnippet(r);
        const pesachBadge =
          isPesachRecipe(r) && kashrut !== "פסח"
            ? `<span class="badge badge-kashrut-פסח">🍷 פסח</span>`
            : "";

        const mediaContent = hasImg
          ? `<img src="${escapeHtml(thumbUrl)}" alt="${escapeHtml(r.title)}" loading="lazy" onerror="this.style.display='none'; this.nextElementSibling.classList.remove('hidden');" />
             <div class="card-media-placeholder hidden">
               <span class="placeholder-icon">${escapeHtml(catMeta.icon)}</span>
               <span class="placeholder-cat-label">${escapeHtml(catMeta.name)}</span>
             </div>`
          : `<div class="card-media-placeholder">
               <span class="placeholder-icon">${escapeHtml(catMeta.icon)}</span>
               <span class="placeholder-cat-label">${escapeHtml(catMeta.name)}</span>
             </div>`;

        return `
          <article class="recipe-card" data-recipe-id="${escapeHtml(r.id)}" tabindex="0" role="button" aria-label="${escapeHtml(r.title)}">
            <div class="card-media">
              ${mediaContent}
              <div class="card-top-overlay">
                <button
                  type="button"
                  class="card-fav-btn ${r.favorite ? "is-fav" : ""}"
                  data-fav-id="${escapeHtml(r.id)}"
                  title="${r.favorite ? "הסר ממועדפים" : "הוסף למועדפים"}"
                  aria-label="מועדף"
                >
                  ${r.favorite ? "★" : "☆"}
                </button>
                <span class="card-source-pill">${escapeHtml(sourceBadge)}</span>
              </div>
            </div>

            <div class="card-body">
              <div class="card-badges-row">
                <span class="badge badge-cat">${escapeHtml(catMeta.icon)} ${escapeHtml(catMeta.name)}</span>
                <span class="badge badge-kashrut-${escapeHtml(kashrut)}">${escapeHtml(kashrut)}</span>
                ${pesachBadge}
              </div>

              <h3 class="card-title">${escapeHtml(r.title)}</h3>
              <p class="card-preview-text">${escapeHtml(snippet)}</p>

              <div class="card-footer">
                <span>${r.prepTime ? `⏱️ ${escapeHtml(r.prepTime)}` : r.subcategory ? escapeHtml(r.subcategory) : "מתכון ביתי"}</span>
                <span class="card-open-cta">פתיחת מתכון ←</span>
              </div>
            </div>
          </article>
        `;
      })
      .join("");
  }

  // =========================================================================
  // HYBRID RECIPE DETAIL VIEW
  // =========================================================================

  function getCurrentRecipe() {
    if (!state.currentRecipeId) return null;
    return state.recipes.find((r) => String(r.id) === String(state.currentRecipeId)) || null;
  }

  function openRecipeDetail(recipeId) {
    const recipe = state.recipes.find((r) => String(r.id) === String(recipeId));
    if (!recipe) return;

    state.currentRecipeId = recipe.id;
    state.currentMultiplier = 1;
    state.checkedIngredients = new Set();
    state.activeStepIndex = null;
    state.currentImageIndex = 0;

    // Reset multiplier buttons UI
    document.querySelectorAll(".mult-btn").forEach((btn) => {
      btn.classList.toggle("active", parseFloat(btn.dataset.mult) === 1);
    });

    // Update URL hash quietly
    if (window.location.hash !== `#recipe=${encodeURIComponent(recipe.id)}`) {
      history.replaceState(null, "", `#recipe=${encodeURIComponent(recipe.id)}`);
    }

    renderRecipeDetailModal(recipe);
    els.recipeDetailModal.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  }

  function closeRecipeDetail() {
    state.currentRecipeId = null;
    if (state.kitchenMode) {
      setKitchenMode(false);
    }
    els.detailPdfIframe.classList.add("hidden");
    els.detailPdfIframe.src = "";
    els.recipeDetailModal.classList.add("hidden");
    document.body.style.overflow = "";
    if (window.location.hash.startsWith("#recipe=")) {
      history.replaceState(null, "", window.location.pathname);
    }
  }

  function updateDetailFavButton(isFav) {
    els.detailFavBtn.classList.toggle("is-fav", Boolean(isFav));
    els.detailFavIcon.textContent = isFav ? "★" : "☆";
  }

  function renderRecipeDetailModal(recipe) {
    const catMeta = getCategoryMeta(recipe.categoryId, recipe.category);
    const kashrut = recipe.kashrut || "פרווה";

    updateDetailFavButton(recipe.favorite);

    // Badges
    let badgesHtml = `
      <span class="badge badge-cat">${escapeHtml(catMeta.icon)} ${escapeHtml(catMeta.name)}</span>
      <span class="badge badge-kashrut-${escapeHtml(kashrut)}">${escapeHtml(kashrut)}</span>
    `;
    if (isPesachRecipe(recipe) && kashrut !== "פסח") {
      badgesHtml += `<span class="badge badge-kashrut-פסח">🍷 כשר לפסח</span>`;
    }
    if (recipe.subcategory) {
      badgesHtml += `<span class="badge badge-cat">${escapeHtml(recipe.subcategory)}</span>`;
    }
    els.detailBadges.innerHTML = badgesHtml;

    els.detailRecipeTitle.textContent = recipe.title;

    // Meta row (prepTime, servings, difficulty)
    const metaItems = [];
    if (recipe.prepTime) metaItems.push(`<span class="meta-item">⏱️ זמן הכנה: <strong>${escapeHtml(recipe.prepTime)}</strong></span>`);
    if (recipe.servings) metaItems.push(`<span class="meta-item">🍽️ כמות: <strong>${escapeHtml(recipe.servings)}</strong></span>`);
    if (recipe.difficulty) metaItems.push(`<span class="meta-item">📊 קושי: <strong>${escapeHtml(recipe.difficulty)}</strong></span>`);
    els.detailMetaRow.innerHTML = metaItems.join("");

    // Render Ingredients, Steps, RawText fallback, Notes
    renderDetailIngredients(recipe);
    renderDetailSteps(recipe);
    renderDetailRawTextAndNotes(recipe);

    // Render Media Column (Original Images & PDF)
    const hasMedia = hasOriginalImages(recipe) || hasOriginalPdf(recipe);
    els.detailMediaCol.classList.toggle("hidden", !hasMedia);
    els.detailHybridGrid.classList.toggle("single-col-text", !hasMedia);
    if (hasMedia) {
      renderDetailMediaColumn(recipe);
    }
  }

  function renderDetailIngredients(recipe) {
    const ingredients = Array.isArray(recipe.ingredients) ? recipe.ingredients : [];
    if (ingredients.length === 0) {
      els.detailIngredientsSection.classList.add("hidden");
      return;
    }

    els.detailIngredientsSection.classList.remove("hidden");
    els.resetCheckedIngredientsBtn.classList.toggle(
      "hidden",
      state.checkedIngredients.size === 0
    );

    els.detailIngredientsList.innerHTML = ingredients
      .map((line, idx) => {
        if (isIngredientSectionHeader(line)) {
          const icon = getIngredientHeaderIcon(line);
          const cleanText = String(line || "").trim();
          return `
            <li class="ingredient-section-header">
              <span class="ingredient-section-icon">${icon}</span>
              <span class="ingredient-section-title">${escapeHtml(cleanText)}</span>
            </li>
          `;
        }

        const isChecked = state.checkedIngredients.has(idx);
        const scaledHtml = scaleIngredientLineHtml(line, state.currentMultiplier);
        return `
          <li class="ingredient-item ${isChecked ? "checked" : ""}" data-ing-idx="${idx}">
            <span class="ingredient-checkbox">✓</span>
            <span class="ingredient-text">${scaledHtml}</span>
          </li>
        `;
      })
      .join("");
  }

  function renderDetailSteps(recipe) {
    const steps = Array.isArray(recipe.steps) ? recipe.steps : [];
    if (steps.length === 0) {
      els.detailStepsSection.classList.add("hidden");
      return;
    }

    els.detailStepsSection.classList.remove("hidden");
    els.detailStepsList.innerHTML = steps
      .map((stepText, idx) => {
        let cls = "step-item";
        if (state.activeStepIndex === idx) cls += " active-step";
        else if (state.activeStepIndex !== null && idx < state.activeStepIndex) {
          cls += " completed-step";
        }
        return `
          <li class="${cls}" data-step-idx="${idx}">
            <span class="step-num">${idx + 1}</span>
            <div class="step-text">${escapeHtml(stepText)}</div>
          </li>
        `;
      })
      .join("");
  }

  function renderDetailRawTextAndNotes(recipe) {
    const hasIngredients = Array.isArray(recipe.ingredients) && recipe.ingredients.length > 0;
    const hasSteps = Array.isArray(recipe.steps) && recipe.steps.length > 0;
    const raw = String(recipe.rawText || "").trim();

    // Show rawText section if ingredients or steps are missing, or if neither exists
    if ((!hasIngredients || !hasSteps) && raw) {
      els.detailRawTextSection.classList.remove("hidden");
      els.detailRawTextBox.textContent = raw;
    } else if (!hasIngredients && !hasSteps && !raw) {
      els.detailRawTextSection.classList.remove("hidden");
      els.detailRawTextBox.textContent =
        "מתכון זה שמור כצילום מקורי — ניתן לצפות בצילום הברור בצד שמאל, להגדיל למסך מלא או לערוך ולהוסיף טקסט.";
    } else {
      els.detailRawTextSection.classList.add("hidden");
    }

    if (recipe.notes && String(recipe.notes).trim()) {
      els.detailNotesSection.classList.remove("hidden");
      els.detailNotesContent.textContent = String(recipe.notes).trim();
    } else {
      els.detailNotesSection.classList.add("hidden");
    }
  }

  function renderDetailMediaColumn(recipe) {
    const images = Array.isArray(recipe.originalImages) ? recipe.originalImages : [];
    const hasImg = images.length > 0;

    if (hasImg) {
      if (state.currentImageIndex >= images.length) {
        state.currentImageIndex = 0;
      }
      const currentRaw = images[state.currentImageIndex];
      const resolvedUrl = resolveAssetUrl(currentRaw);

      els.detailImageStage.classList.remove("hidden");
      els.detailImageControlsBar.classList.remove("hidden");
      els.detailMainImage.src = resolvedUrl;
      els.detailMainImage.alt = `${recipe.title} - עמוד ${state.currentImageIndex + 1}`;

      if (images.length > 1) {
        els.detailImagePageBadge.classList.remove("hidden");
        els.detailImagePageBadge.textContent = `עמוד ${state.currentImageIndex + 1} מתוך ${images.length}`;

        els.detailImagePageSwitcher.classList.remove("hidden");
        els.detailImagePageSwitcher.innerHTML = images
          .map((_, idx) => {
            return `<button type="button" class="page-tab-btn ${idx === state.currentImageIndex ? "active" : ""}" data-page-idx="${idx}">עמוד ${idx + 1}</button>`;
          })
          .join("");

        els.detailThumbsStrip.classList.remove("hidden");
        els.detailThumbsStrip.innerHTML = images
          .map((imgPath, idx) => {
            return `
              <div class="detail-thumb-item ${idx === state.currentImageIndex ? "active" : ""}" data-page-idx="${idx}">
                <img src="${escapeHtml(resolveAssetUrl(imgPath))}" alt="עמוד ${idx + 1}" />
              </div>
            `;
          })
          .join("");
      } else {
        els.detailImagePageBadge.classList.add("hidden");
        els.detailImagePageSwitcher.classList.add("hidden");
        els.detailThumbsStrip.classList.add("hidden");
      }
    } else {
      els.detailImagePageBadge.classList.add("hidden");
      els.detailImagePageSwitcher.classList.add("hidden");
      els.detailImageStage.classList.add("hidden");
      els.detailImageControlsBar.classList.add("hidden");
      els.detailThumbsStrip.classList.add("hidden");
    }

    // PDF Box
    if (hasOriginalPdf(recipe)) {
      const pdfUrl = resolveAssetUrl(recipe.originalPdf);
      els.detailPdfBox.classList.remove("hidden");
      els.detailPdfLink.href = pdfUrl;
      els.detailPdfIframe.dataset.pdfSrc = pdfUrl;
    } else {
      els.detailPdfBox.classList.add("hidden");
    }

    // Source provenance
    const sourceFiles = Array.isArray(recipe.sourceFiles) ? recipe.sourceFiles : [];
    if (sourceFiles.length > 0) {
      els.detailSourceProvenance.textContent = `מקור הקובץ: ${sourceFiles.join(" , ")}`;
    } else {
      els.detailSourceProvenance.textContent = `קטגוריה: ${recipe.category || ""}`;
    }
  }

  // =========================================================================
  // KITCHEN MODE & WAKELOCK
  // =========================================================================

  async function setKitchenMode(enabled) {
    state.kitchenMode = Boolean(enabled);
    els.recipeModalCard.classList.toggle("kitchen-mode-active", state.kitchenMode);
    els.toggleKitchenModeBtn.classList.toggle("active", state.kitchenMode);
    els.kitchenActiveBanner.classList.toggle("hidden", !state.kitchenMode);
    els.kitchenModeBtnLabel.textContent = state.kitchenMode ? "מצב מטבח פעיל" : "מצב מטבח";

    if (state.kitchenMode) {
      if ("wakeLock" in navigator) {
        try {
          state.wakeLockSentinel = await navigator.wakeLock.request("screen");
          els.wakeLockStatusText.textContent = "המסך יישאר דלוק בזמן הבישול";
        } catch (_) {
          els.wakeLockStatusText.textContent = "תצוגה מוגדלת פעילה";
        }
      } else {
        els.wakeLockStatusText.textContent = "תצוגה מוגדלת פעילה";
      }
      showToast("מצב מטבח הופעל 👨‍🍳");
    } else {
      if (state.wakeLockSentinel) {
        try {
          await state.wakeLockSentinel.release();
        } catch (_) {}
        state.wakeLockSentinel = null;
      }
    }
  }

  // =========================================================================
  // WHATSAPP / CLIPBOARD SHARE
  // =========================================================================

  async function copyRecipeForWhatsapp() {
    const recipe = getCurrentRecipe();
    if (!recipe) return;

    const lines = [];
    lines.push(`🍲 *${recipe.title}*`);
    lines.push(`קטגוריה: ${recipe.category || ""} | כשרות: ${recipe.kashrut || "פרווה"}`);
    if (state.currentMultiplier !== 1) {
      lines.push(`_(כמויות מוכפלות ב-×${state.currentMultiplier})_`);
    }
    lines.push("");

    if (Array.isArray(recipe.ingredients) && recipe.ingredients.length > 0) {
      lines.push("*🧺 מצרכים:*");
      for (const ing of recipe.ingredients) {
        if (isIngredientSectionHeader(ing)) {
          const icon = getIngredientHeaderIcon(ing);
          lines.push(`\n${icon} *${ing.trim()}*`);
        } else {
          const tmp = document.createElement("div");
          tmp.innerHTML = scaleIngredientLineHtml(ing, state.currentMultiplier);
          lines.push(`• ${tmp.textContent}`);
        }
      }
      lines.push("");
    }

    if (Array.isArray(recipe.steps) && recipe.steps.length > 0) {
      lines.push("*👩‍🍳 אופן ההכנה:*");
      recipe.steps.forEach((s, i) => {
        lines.push(`${i + 1}. ${s}`);
      });
      lines.push("");
    } else if (recipe.rawText) {
      lines.push(recipe.rawText);
      lines.push("");
    }

    if (recipe.notes) {
      lines.push(`💡 *טיפ:* ${recipe.notes}`);
    }

    const formattedText = lines.join("\n").trim();
    try {
      await navigator.clipboard.writeText(formattedText);
      showToast("המתכון הועתק ללוח! ניתן להדביק בוואטסאפ 💬");
    } catch (_) {
      showToast("הועתק!");
    }
  }

  // =========================================================================
  // FULLSCREEN LIGHTBOX (ZOOM, PAN, ROTATE)
  // =========================================================================

  function openLightbox(imagesList, startIndex = 0) {
    if (!Array.isArray(imagesList) || imagesList.length === 0) return;
    state.lightboxImages = imagesList;
    state.lightboxIndex = Math.max(0, Math.min(startIndex, imagesList.length - 1));
    state.lightboxZoom = 1;

    renderLightboxSlide();
    els.lightboxModal.classList.remove("hidden");
  }

  function closeLightbox() {
    els.lightboxModal.classList.add("hidden");
    state.lightboxZoom = 1;
  }

  function renderLightboxSlide() {
    const item = state.lightboxImages[state.lightboxIndex];
    if (!item) return;

    els.lightboxTitle.textContent = item.title || "צילום מתכון";
    els.lightboxCounter.textContent =
      state.lightboxImages.length > 1
        ? `(${state.lightboxIndex + 1} מתוך ${state.lightboxImages.length})`
        : "";

    els.lightboxImg.src = resolveAssetUrl(item.rawPath);
    applyLightboxZoom();

    els.lbPrevBtn.classList.toggle("hidden", state.lightboxImages.length <= 1);
    els.lbNextBtn.classList.toggle("hidden", state.lightboxImages.length <= 1);
  }

  function applyLightboxZoom() {
    els.lightboxImg.style.transform = `scale(${state.lightboxZoom})`;
    els.lbZoomResetBtn.textContent = `${Math.round(state.lightboxZoom * 100)}%`;
  }

  // =========================================================================
  // ADD / EDIT RECIPE MODAL
  // =========================================================================

  function openRecipeFormModal(recipeToEdit = null) {
    state.editingRecipeId = recipeToEdit ? recipeToEdit.id : null;
    els.uploadStatusText.textContent = "";
    els.formImageUpload.value = "";

    if (recipeToEdit) {
      els.formModalTitle.textContent = `עריכת מתכון: ${recipeToEdit.title}`;
      els.formRecipeId.value = recipeToEdit.id;
      els.formTitle.value = recipeToEdit.title || "";
      els.formCategory.value = recipeToEdit.categoryId || "cakes";
      els.formKashrut.value = recipeToEdit.kashrut || "פרווה";
      els.formSubcategory.value = recipeToEdit.subcategory || "";
      els.formPrepTime.value = recipeToEdit.prepTime || "";
      els.formServings.value = recipeToEdit.servings || "";
      els.formIngredients.value = (recipeToEdit.ingredients || []).join("\n");
      els.formSteps.value = (recipeToEdit.steps || []).join("\n");
      els.formNotes.value = recipeToEdit.notes || "";
      state.formUploadedImages = Array.isArray(recipeToEdit.originalImages)
        ? [...recipeToEdit.originalImages]
        : [];
    } else {
      els.formModalTitle.textContent = "הוספת מתכון חדש לספר המשפחתי";
      els.formRecipeId.value = "";
      els.formTitle.value = "";
      els.formCategory.value =
        state.activeCategoryId !== "all" &&
        state.activeCategoryId !== "favorites" &&
        state.activeCategoryId !== "course-gallery"
          ? state.activeCategoryId
          : "cakes";
      els.formKashrut.value = "פרווה";
      els.formSubcategory.value = "";
      els.formPrepTime.value = "";
      els.formServings.value = "";
      els.formIngredients.value = "";
      els.formSteps.value = "";
      els.formNotes.value = "";
      state.formUploadedImages = [];
    }

    renderFormUploadedImagesPills();
    els.recipeFormModal.classList.remove("hidden");
  }

  function closeRecipeFormModal() {
    els.recipeFormModal.classList.add("hidden");
    state.editingRecipeId = null;
  }

  function renderFormUploadedImagesPills() {
    els.formUploadedImagesList.innerHTML = state.formUploadedImages
      .map((imgPath, idx) => {
        const name = imgPath.split("/").pop();
        return `
          <span class="uploaded-pill">
            <span>📷 ${escapeHtml(name)}</span>
            <button type="button" data-remove-img="${idx}" title="הסר תמונה">✕</button>
          </span>
        `;
      })
      .join("");
  }

  async function handleFileUploadChange(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;

    els.uploadStatusText.textContent = "מעלה תמונה לשרת...";
    try {
      const dataUrl = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      const res = await fetch("/api/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name, dataUrl }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data.error || "שגיאה בהעלאת הקובץ");
      }

      state.formUploadedImages.push(data.imageUrl);
      renderFormUploadedImagesPills();
      els.uploadStatusText.textContent = "התמונה הועלתה בהצלחה ✓";
    } catch (err) {
      console.error("Upload failed:", err);
      els.uploadStatusText.textContent = "שגיאה בהעלאת התמונה";
    }
  }

  async function handleSaveRecipeForm(e) {
    e.preventDefault();
    const title = els.formTitle.value.trim();
    if (!title) {
      showToast("נא להזין שם מתכון");
      return;
    }

    const catId = els.formCategory.value;
    const catMeta = getCategoryMeta(catId, "");
    const payload = {
      title,
      categoryId: catId,
      category: catMeta.name,
      kashrut: els.formKashrut.value,
      subcategory: els.formSubcategory.value.trim(),
      prepTime: els.formPrepTime.value.trim(),
      servings: els.formServings.value.trim(),
      ingredients: els.formIngredients.value
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean),
      steps: els.formSteps.value
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean),
      notes: els.formNotes.value.trim(),
      originalImages: state.formUploadedImages,
    };

    try {
      const isEdit = Boolean(state.editingRecipeId);
      const url = isEdit
        ? `/api/recipes/${encodeURIComponent(state.editingRecipeId)}`
        : "/api/recipes";
      const method = isEdit ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data.error || "שגיאה בשמירת המתכון");
      }

      const savedRecipe = data.recipe;
      if (isEdit) {
        const idx = state.recipes.findIndex((r) => String(r.id) === String(savedRecipe.id));
        if (idx !== -1) state.recipes[idx] = savedRecipe;
      } else {
        state.recipes.unshift(savedRecipe);
      }

      closeRecipeFormModal();
      renderAll();
      openRecipeDetail(savedRecipe.id);
      showToast(isEdit ? "המתכון עודכן ונשמר בהצלחה ✓" : "המתכון החדש נוסף לספר המתכונים ✓");
    } catch (err) {
      console.error("Save error:", err);
      showToast("שגיאה בשמירה: " + err.message);
    }
  }

  // =========================================================================
  // EVENT LISTENERS & INITIALIZATION
  // =========================================================================

  function handleHashNavigation() {
    const hash = window.location.hash || "";
    if (hash.startsWith("#recipe=")) {
      const id = decodeURIComponent(hash.slice("#recipe=".length));
      const found = state.recipes.find((r) => String(r.id) === id);
      if (found) {
        openRecipeDetail(found.id);
      }
    }
  }

  function resetAllFilters() {
    state.activeCategoryId = "all";
    state.searchQuery = "";
    state.kashrutFilter = "all";
    state.sourceFilter = "all";
    els.searchInput.value = "";
    els.clearSearchBtn.classList.add("hidden");

    document.querySelectorAll("#kashrutFilterGroup .filter-pill").forEach((b) => {
      b.classList.toggle("active", b.dataset.kashrut === "all");
    });
    document.querySelectorAll("#sourceFilterGroup .filter-pill").forEach((b) => {
      b.classList.toggle("active", b.dataset.source === "all");
    });
    document.querySelectorAll(".quick-tag").forEach((b) => b.classList.remove("active"));

    renderCategoryNav();
    renderMainContent();
  }

  function bindEvents() {
    // Brand Home click
    els.brandHomeBtn.addEventListener("click", resetAllFilters);

    // Random Recipe button
    els.randomRecipeBtn.addEventListener("click", () => {
      const pool = getFilteredAndSortedRecipes();
      const list = pool.length > 0 ? pool : state.recipes;
      if (list.length === 0) return;
      const pick = list[Math.floor(Math.random() * list.length)];
      openRecipeDetail(pick.id);
      showToast(`🎲 מתכון בהפתעה: ${pick.title}`);
    });

    // Refresh button
    els.refreshDataBtn.addEventListener("click", () => fetchRecipesData(true));

    // Add New Recipe button
    els.addNewRecipeBtn.addEventListener("click", () => openRecipeFormModal(null));

    // Search Input
    els.searchInput.addEventListener("input", (e) => {
      state.searchQuery = e.target.value;
      els.clearSearchBtn.classList.toggle("hidden", !state.searchQuery);
      renderMainContent();
    });

    els.clearSearchBtn.addEventListener("click", () => {
      state.searchQuery = "";
      els.searchInput.value = "";
      els.clearSearchBtn.classList.add("hidden");
      document.querySelectorAll(".quick-tag").forEach((b) => b.classList.remove("active"));
      renderMainContent();
      els.searchInput.focus();
    });

    // Quick Search Ingredient Tags
    els.quickSearchTags.addEventListener("click", (e) => {
      const btn = e.target.closest(".quick-tag");
      if (!btn) return;
      const q = btn.dataset.query;
      if (state.searchQuery === q) {
        state.searchQuery = "";
        els.searchInput.value = "";
        btn.classList.remove("active");
      } else {
        state.searchQuery = q;
        els.searchInput.value = q;
        document.querySelectorAll(".quick-tag").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      }
      els.clearSearchBtn.classList.toggle("hidden", !state.searchQuery);
      renderMainContent();
    });

    // Kashrut Filter Pills
    els.kashrutFilterGroup.addEventListener("click", (e) => {
      const btn = e.target.closest(".filter-pill");
      if (!btn) return;
      state.kashrutFilter = btn.dataset.kashrut;
      els.kashrutFilterGroup.querySelectorAll(".filter-pill").forEach((b) => {
        b.classList.toggle("active", b === btn);
      });
      renderMainContent();
    });

    // Source Filter Pills
    els.sourceFilterGroup.addEventListener("click", (e) => {
      const btn = e.target.closest(".filter-pill");
      if (!btn) return;
      state.sourceFilter = btn.dataset.source;
      els.sourceFilterGroup.querySelectorAll(".filter-pill").forEach((b) => {
        b.classList.toggle("active", b === btn);
      });
      renderMainContent();
    });

    // Sort Select
    els.sortSelect.addEventListener("change", (e) => {
      state.sortBy = e.target.value;
      renderMainContent();
    });

    // Category Sidebar Navigation
    els.categoryNav.addEventListener("click", (e) => {
      const btn = e.target.closest(".cat-nav-btn");
      if (!btn) return;
      state.activeCategoryId = btn.dataset.cat;
      renderCategoryNav();
      renderMainContent();
    });

    // Reset Filters
    els.resetFiltersBtn.addEventListener("click", resetAllFilters);
    els.emptyResetBtn.addEventListener("click", resetAllFilters);

    // Recipe Cards Grid Click (delegated)
    els.recipesGrid.addEventListener("click", (e) => {
      const favBtn = e.target.closest("[data-fav-id]");
      if (favBtn) {
        toggleRecipeFavorite(favBtn.dataset.favId, e);
        return;
      }
      const card = e.target.closest(".recipe-card");
      if (card) {
        openRecipeDetail(card.dataset.recipeId);
      }
    });

    els.recipesGrid.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        const card = e.target.closest(".recipe-card");
        if (card) {
          e.preventDefault();
          openRecipeDetail(card.dataset.recipeId);
        }
      }
    });

    // Course Gallery Grid Click
    els.courseGalleryGrid.addEventListener("click", (e) => {
      const card = e.target.closest("[data-gallery-idx]");
      if (!card) return;
      const idx = parseInt(card.dataset.galleryIdx, 10) || 0;
      const q = state.searchQuery.trim().toLowerCase();
      const filteredGallery = state.courseGallery.filter(
        (g) => !q || String(g.title || "").toLowerCase().includes(q)
      );
      const lbList = filteredGallery.map((g) => ({
        rawPath: g.imageUrl,
        title: g.title,
      }));
      openLightbox(lbList, idx);
    });

    // Detail Modal Events
    els.closeDetailModalBtn.addEventListener("click", closeRecipeDetail);
    els.recipeDetailModal.addEventListener("click", (e) => {
      if (e.target === els.recipeDetailModal) closeRecipeDetail();
    });

    els.toggleKitchenModeBtn.addEventListener("click", () => setKitchenMode(!state.kitchenMode));
    els.exitKitchenModeBtn.addEventListener("click", () => setKitchenMode(false));

    els.detailFavBtn.addEventListener("click", () => {
      if (state.currentRecipeId) toggleRecipeFavorite(state.currentRecipeId);
    });

    els.editCurrentRecipeBtn.addEventListener("click", () => {
      const r = getCurrentRecipe();
      if (r) openRecipeFormModal(r);
    });

    els.shareWhatsappBtn.addEventListener("click", copyRecipeForWhatsapp);
    els.printRecipeBtn.addEventListener("click", () => window.print());

    // Multiplier Buttons
    document.querySelectorAll(".mult-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mult = parseFloat(btn.dataset.mult) || 1;
        state.currentMultiplier = mult;
        document.querySelectorAll(".mult-btn").forEach((b) => {
          b.classList.toggle("active", b === btn);
        });
        const r = getCurrentRecipe();
        if (r) renderDetailIngredients(r);
      });
    });

    // Ingredients Checklist Toggle
    els.detailIngredientsList.addEventListener("click", (e) => {
      const item = e.target.closest(".ingredient-item");
      if (!item) return;
      const idx = parseInt(item.dataset.ingIdx, 10);
      if (state.checkedIngredients.has(idx)) {
        state.checkedIngredients.delete(idx);
      } else {
        state.checkedIngredients.add(idx);
      }
      const r = getCurrentRecipe();
      if (r) renderDetailIngredients(r);
    });

    els.resetCheckedIngredientsBtn.addEventListener("click", () => {
      state.checkedIngredients.clear();
      const r = getCurrentRecipe();
      if (r) renderDetailIngredients(r);
    });

    // Steps Active Highlight Toggle
    els.detailStepsList.addEventListener("click", (e) => {
      const item = e.target.closest(".step-item");
      if (!item) return;
      const idx = parseInt(item.dataset.stepIdx, 10);
      state.activeStepIndex = state.activeStepIndex === idx ? null : idx;
      const r = getCurrentRecipe();
      if (r) renderDetailSteps(r);
    });

    // Multi-Page Image Switcher
    const handlePageSwitch = (e) => {
      const target = e.target.closest("[data-page-idx]");
      if (!target) return;
      state.currentImageIndex = parseInt(target.dataset.pageIdx, 10) || 0;
      const r = getCurrentRecipe();
      if (r) renderDetailMediaColumn(r);
    };
    els.detailImagePageSwitcher.addEventListener("click", handlePageSwitch);
    els.detailThumbsStrip.addEventListener("click", handlePageSwitch);

    // Open Lightbox from Detail Image
    const openCurrentRecipeLightbox = () => {
      const r = getCurrentRecipe();
      if (!r || !hasOriginalImages(r)) return;
      const lbList = r.originalImages.map((imgPath, idx) => ({
        rawPath: imgPath,
        title: `${r.title} — עמוד ${idx + 1}`,
      }));
      openLightbox(lbList, state.currentImageIndex);
    };
    els.detailImageStage.addEventListener("click", openCurrentRecipeLightbox);
    els.openLightboxBtn.addEventListener("click", openCurrentRecipeLightbox);

    // Rotate Image in Detail View
    els.rotateRightBtn.addEventListener("click", () => {
      const r = getCurrentRecipe();
      if (!r || !hasOriginalImages(r)) return;
      rotateImageOnServer(r.originalImages[state.currentImageIndex], 90);
    });

    els.rotateLeftBtn.addEventListener("click", () => {
      const r = getCurrentRecipe();
      if (!r || !hasOriginalImages(r)) return;
      rotateImageOnServer(r.originalImages[state.currentImageIndex], 270);
    });

    // Toggle Embedded PDF Preview
    els.toggleEmbeddedPdfBtn.addEventListener("click", () => {
      const isHidden = els.detailPdfIframe.classList.contains("hidden");
      if (isHidden) {
        els.detailPdfIframe.src = els.detailPdfIframe.dataset.pdfSrc || "";
        els.detailPdfIframe.classList.remove("hidden");
        els.toggleEmbeddedPdfBtn.textContent = "הסתר תצוגה מקדימה";
      } else {
        els.detailPdfIframe.classList.add("hidden");
        els.toggleEmbeddedPdfBtn.textContent = "הצג תצוגה מקדימה כאן";
      }
    });

    // Lightbox Controls
    els.lbCloseBtn.addEventListener("click", closeLightbox);
    els.lbZoomInBtn.addEventListener("click", () => {
      state.lightboxZoom = Math.min(4, +(state.lightboxZoom + 0.35).toFixed(2));
      applyLightboxZoom();
    });
    els.lbZoomOutBtn.addEventListener("click", () => {
      state.lightboxZoom = Math.max(0.5, +(state.lightboxZoom - 0.35).toFixed(2));
      applyLightboxZoom();
    });
    els.lbZoomResetBtn.addEventListener("click", () => {
      state.lightboxZoom = 1;
      applyLightboxZoom();
    });

    els.lbRotateRightBtn.addEventListener("click", () => {
      const item = state.lightboxImages[state.lightboxIndex];
      if (item) rotateImageOnServer(item.rawPath, 90);
    });
    els.lbRotateLeftBtn.addEventListener("click", () => {
      const item = state.lightboxImages[state.lightboxIndex];
      if (item) rotateImageOnServer(item.rawPath, 270);
    });

    els.lbPrevBtn.addEventListener("click", () => {
      if (state.lightboxImages.length <= 1) return;
      state.lightboxIndex =
        (state.lightboxIndex - 1 + state.lightboxImages.length) % state.lightboxImages.length;
      state.lightboxZoom = 1;
      renderLightboxSlide();
    });
    els.lbNextBtn.addEventListener("click", () => {
      if (state.lightboxImages.length <= 1) return;
      state.lightboxIndex = (state.lightboxIndex + 1) % state.lightboxImages.length;
      state.lightboxZoom = 1;
      renderLightboxSlide();
    });

    els.lightboxImgWrapper.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.2 : -0.2;
        state.lightboxZoom = Math.max(0.5, Math.min(4, +(state.lightboxZoom + delta).toFixed(2)));
        applyLightboxZoom();
      },
      { passive: false }
    );

    // Form Modal Events
    els.closeFormModalBtn.addEventListener("click", closeRecipeFormModal);
    els.cancelFormModalBtn.addEventListener("click", closeRecipeFormModal);
    els.formImageUpload.addEventListener("change", handleFileUploadChange);
    els.formUploadedImagesList.addEventListener("click", (e) => {
      const rmBtn = e.target.closest("[data-remove-img]");
      if (!rmBtn) return;
      const idx = parseInt(rmBtn.dataset.removeImg, 10);
      state.formUploadedImages.splice(idx, 1);
      renderFormUploadedImagesPills();
    });
    els.recipeForm.addEventListener("submit", handleSaveRecipeForm);

    // Global Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        if (!els.lightboxModal.classList.contains("hidden")) {
          closeLightbox();
        } else if (!els.recipeFormModal.classList.contains("hidden")) {
          closeRecipeFormModal();
        } else if (!els.recipeDetailModal.classList.contains("hidden")) {
          closeRecipeDetail();
        }
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    cacheElements();
    bindEvents();
    fetchRecipesData(false);
  });
})();
