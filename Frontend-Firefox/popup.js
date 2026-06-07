const urlInput = document.getElementById("url-input-field");
const maxActiveFetches = document.getElementById(
  "maxactivefetches-input-field"
);
const showOriginalCheckbox = document.getElementById("showoriginal-checkbox");
const showColorizedCheckbox = document.getElementById("showcolorized-checkbox");
const sideBySideCheckbox = document.getElementById("sidebyside-checkbox");
const cacheCheckbox = document.getElementById("cache-checkbox");
const denoiseCheckbox = document.getElementById("denoiser-checkbox");
const colorizeCheckbox = document.getElementById("colorizer-checkbox");
const upscaleCheckbox = document.getElementById("upscaler-checkbox");
const upscaleFactorSelector = document.querySelectorAll(
  "input[name='upscale-factor']"
);
const upscaleFactorSelector2 = document.getElementById("upscale-factor-2");
const upscaleFactorSelector4 = document.getElementById("upscale-factor-4");
const toneSelector = document.getElementById("tone-selector");
const referenceImageUrlInput = document.getElementById(
  "reference-image-url-field"
);
const brightnessSlider = document.getElementById("brightness-slider");
const brightnessValue = document.getElementById("brightness-value");
const contrastSlider = document.getElementById("contrast-slider");
const contrastValue = document.getElementById("contrast-value");
const saturationSlider = document.getElementById("saturation-slider");
const saturationValue = document.getElementById("saturation-value");
const hueRotateSlider = document.getElementById("hue-rotate-slider");
const hueRotateValue = document.getElementById("hue-rotate-value");
const presetSelector = document.getElementById("preset-selector");
const savePresetBtn = document.getElementById("save-preset-btn");
const deletePresetBtn = document.getElementById("delete-preset-btn");
const resetFiltersBtn = document.getElementById("reset-filters-btn");
const presetNameContainer = document.getElementById("preset-name-container");
const presetNameInput = document.getElementById("preset-name-input");
const confirmSavePresetBtn = document.getElementById("confirm-save-preset-btn");
const cancelSavePresetBtn = document.getElementById("cancel-save-preset-btn");
const denoiseSigmaInput = document.getElementById("denoisesigma-input-field");
const colorToleranceInput = document.getElementById(
  "colortolerance-input-field"
);
const colorStrideInput = document.getElementById("colorstride-input-field");
const websitesInput = document.getElementById("websites-input-field");
const addSiteButton = document.getElementById("addsite");
const runButton = document.getElementById("run");
const testApiButton = document.getElementById("test-api");
const forceRunButton = document.getElementById("force-run");
// Function to load available tones from the API
function loadAvailableTones(apiURL) {
  if (!apiURL) return;

  fetch(`${apiURL}/tones`)
    .then((response) => response.json())
    .then((data) => {
      if (data.tones && Array.isArray(data.tones)) {
        const currentValue = toneSelector.value;

        // Clear existing options except custom
        toneSelector.innerHTML = "";

        // Add all tones from API
        data.tones.forEach((tone) => {
          const option = document.createElement("option");
          option.value = tone;
          option.textContent = tone.charAt(0).toUpperCase() + tone.slice(1);
          toneSelector.appendChild(option);
        });

        // Always add 'custom' option at the end
        const customOption = document.createElement("option");
        customOption.value = "custom";
        customOption.textContent = "Custom Image";
        toneSelector.appendChild(customOption);

        // Restore previous selection if it still exists
        if (
          [...toneSelector.options].some((opt) => opt.value === currentValue)
        ) {
          toneSelector.value = currentValue;
        } else {
          toneSelector.value = "neutral";
        }
      }
    })
    .catch((error) => {
      console.log("[MC] Failed to load tones from API:", error);
    });
}
browser.storage.local.get(
  [
    "apiURL",
    "maxActiveFetches",
    "showOriginal",
    "showColorized",
    "sideBySide",
    "cache",
    "denoise",
    "colorize",
    "upscale",
    "denoiseSigma",
    "upscaleFactor",
    "tone",
    "referenceImageURL",
    "brightness",
    "contrast",
    "saturation",
    "hueRotate",
    "colorTolerance",
    "colorStride",
    "websites",
    "categoryStates",
  ],
  (result) => {
    urlInput.value = result.apiURL || "";
    maxActiveFetches.value = result.maxActiveFetches || "1";
    showOriginalCheckbox.checked =
      result.showOriginal !== undefined ? result.showOriginal : false;
    showColorizedCheckbox.checked =
      result.showColorized !== undefined ? result.showColorized : true;
    sideBySideCheckbox.checked =
      result.sideBySide !== undefined ? result.sideBySide : false;
    cacheCheckbox.checked = result.cache !== undefined ? result.cache : false;
    denoiseCheckbox.checked =
      result.denoise !== undefined ? result.denoise : true;
    colorizeCheckbox.checked =
      result.colorize !== undefined ? result.colorize : true;
    upscaleCheckbox.checked =
      result.upscale !== undefined ? result.upscale : true;
    if (result.upscaleFactor === "2") {
      upscaleFactorSelector2.checked = true;
    } else if (result.upscaleFactor === "4") {
      upscaleFactorSelector4.checked = true;
    } else {
      upscaleFactorSelector4.checked = true;
    }

    // Load available tones from API
    if (result.apiURL) {
      loadAvailableTones(result.apiURL);
    }

    toneSelector.value = result.tone || "neutral";
    referenceImageUrlInput.value = result.referenceImageURL || "";
    brightnessSlider.value = result.brightness || "1.0";
    brightnessValue.textContent = brightnessSlider.value;
    contrastSlider.value = result.contrast || "1.0";
    contrastValue.textContent = contrastSlider.value;
    saturationSlider.value = result.saturation || "1.0";
    saturationValue.textContent = saturationSlider.value;
    hueRotateSlider.value = result.hueRotate || "0";
    hueRotateValue.textContent = hueRotateSlider.value;

    // Show/hide reference image input based on tone selection
    const referenceImageContainer = document.getElementById(
      "reference-image-container"
    );
    if (toneSelector.value === "custom") {
      referenceImageContainer.style.display = "flex";
    } else {
      referenceImageContainer.style.display = "none";
    }
    denoiseSigmaInput.value = result.denoiseSigma || "25";
    colorToleranceInput.value = result.colorTolerance || "30";
    colorStrideInput.value = result.colorStride || "4";
    websitesInput.value =
      result.websites ||
      "mangadex.org/chapter\nchapmanganelo.com\nfanfox.net" +
        "\nmangakakalot.com\nsenkuro.com\nreadmanga.io\nmanhuatop.org";
    const sitesArray = websitesInput.value.split("\n");
    websitesInput.rows = sitesArray.length + 1;
    websitesInput.cols = sitesArray.reduce((len, str) => {
      return Math.max(len, str.length);
    }, 25);
    addSiteButton.style.display = "none";
    browser.tabs.query({ currentWindow: true, active: true }, (tabs) => {
      if (tabs[0]?.url?.startsWith("http")) {
        const hostname = new URL(tabs[0].url).hostname;
        if (hostname && !websitesInput.value.includes(hostname)) {
          addSiteButton.innerText = "Add " + hostname;
          addSiteButton.removeAttribute("style");
          addSiteButton.addEventListener("click", () => {
            addSiteButton.style.display = "none";
            if (
              websitesInput.value.length > 0 &&
              !websitesInput.value.endsWith("\n")
            )
              websitesInput.value += "\n";
            websitesInput.value += hostname;
            browser.storage.local.set({ websites: websitesInput.value.trim() });
          });
        }
      }
    });

    // Initialize category states (default all expanded)
    const categoryStates = result.categoryStates || {
      connection: true,
      processing: true,
      colorization: true,
      advanced: true,
    };
    initializeCategories(categoryStates);

    // Load presets
    loadPresets();
  }
);

// Category toggle functionality
function initializeCategories(categoryStates) {
  const categoryHeaders = document.querySelectorAll(".category-header");

  categoryHeaders.forEach((header) => {
    const categoryName = header.getAttribute("data-category");
    const content = document.querySelector(
      `.category-content[data-category="${categoryName}"]`
    );
    const arrow = header.querySelector(".category-arrow");

    // Set initial state
    const isExpanded = categoryStates[categoryName] !== false; // Default true
    if (!isExpanded) {
      content.classList.add("collapsed");
      arrow.textContent = "▶";
    } else {
      content.classList.remove("collapsed");
      arrow.textContent = "▼";
    }

    // Add click handler
    header.addEventListener("click", () => {
      const isCurrentlyExpanded = !content.classList.contains("collapsed");

      if (isCurrentlyExpanded) {
        content.classList.add("collapsed");
        arrow.textContent = "▶";
      } else {
        content.classList.remove("collapsed");
        arrow.textContent = "▼";
      }

      // Save state
      categoryStates[categoryName] = !isCurrentlyExpanded;
      browser.storage.local.set({ categoryStates });
    });
  });
}

// Preset management functions
function loadPresets() {
  browser.storage.local.get(["filterPresets", "activePresetId"], (result) => {
    const presets = result.filterPresets || [];
    presetSelector.innerHTML = '<option value="">-- Select Preset --</option>';

    presets.forEach((preset) => {
      const option = document.createElement("option");
      option.value = preset.id;
      option.textContent = preset.name;
      if (preset.id === result.activePresetId) {
        option.selected = true;
      }
      presetSelector.appendChild(option);
    });

    // Enable/disable delete button
    deletePresetBtn.disabled = !presetSelector.value;
  });
}

function savePreset(name) {
  browser.storage.local.get(["filterPresets"], (result) => {
    const presets = result.filterPresets || [];

    // Check preset limit
    if (presets.length >= 20) {
      alert("Preset limit reached (20). Please delete some presets first.");
      return;
    }

    const newPreset = {
      id: `preset_${Date.now()}`,
      name: name.trim() || `Preset ${presets.length + 1}`,
      filters: {
        brightness: brightnessSlider.value,
        contrast: contrastSlider.value,
        saturation: saturationSlider.value,
        hueRotate: hueRotateSlider.value,
      },
      tone: toneSelector.value,
      referenceImageURL: referenceImageUrlInput.value.trim(),
      createdAt: Date.now(),
    };

    presets.push(newPreset);
    browser.storage.local.set(
      {
        filterPresets: presets,
        activePresetId: newPreset.id,
      },
      () => {
        loadPresets();
        presetSelector.value = newPreset.id;
      }
    );
  });
}

function loadPreset(presetId) {
  browser.storage.local.get(["filterPresets"], (result) => {
    const preset = result.filterPresets?.find((p) => p.id === presetId);
    if (preset) {
      // Update UI sliders
      brightnessSlider.value = preset.filters.brightness;
      brightnessValue.textContent = preset.filters.brightness;
      contrastSlider.value = preset.filters.contrast;
      contrastValue.textContent = preset.filters.contrast;
      saturationSlider.value = preset.filters.saturation;
      saturationValue.textContent = preset.filters.saturation;
      hueRotateSlider.value = preset.filters.hueRotate;
      hueRotateValue.textContent = preset.filters.hueRotate;

      // Update tone and reference image
      if (preset.tone) {
        toneSelector.value = preset.tone;
        referenceImageUrlInput.value = preset.referenceImageURL || "";

        // Show/hide reference image input based on tone
        const referenceImageContainer = document.getElementById(
          "reference-image-container"
        );
        if (preset.tone === "custom") {
          referenceImageContainer.style.display = "flex";
        } else {
          referenceImageContainer.style.display = "none";
        }
      }

      // Update storage
      browser.storage.local.set({
        brightness: preset.filters.brightness,
        contrast: preset.filters.contrast,
        saturation: preset.filters.saturation,
        hueRotate: preset.filters.hueRotate,
        tone: preset.tone || toneSelector.value,
        referenceImageURL: preset.referenceImageURL || "",
        activePresetId: presetId,
      });

      // Send to content script
      browser.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        browser.tabs.sendMessage(tabs[0].id, {
          action: "updateFilters",
          filters: {
            brightness: parseFloat(preset.filters.brightness),
            contrast: parseFloat(preset.filters.contrast),
            saturation: parseFloat(preset.filters.saturation),
            hueRotate: parseInt(preset.filters.hueRotate),
          },
        });
      });
    }
  });
}

function deletePreset(presetId) {
  if (!confirm("Delete this preset?")) return;

  browser.storage.local.get(["filterPresets", "activePresetId"], (result) => {
    const presets =
      result.filterPresets?.filter((p) => p.id !== presetId) || [];
    const updates = { filterPresets: presets };

    if (result.activePresetId === presetId) {
      updates.activePresetId = null;
    }

    browser.storage.local.set(updates, () => {
      loadPresets();
    });
  });
}

function resetFilters() {
  brightnessSlider.value = "1.0";
  brightnessValue.textContent = "1.0";
  contrastSlider.value = "1.0";
  contrastValue.textContent = "1.0";
  saturationSlider.value = "1.0";
  saturationValue.textContent = "1.0";
  hueRotateSlider.value = "0";
  hueRotateValue.textContent = "0";

  browser.storage.local.set({
    brightness: "1.0",
    contrast: "1.0",
    saturation: "1.0",
    hueRotate: "0",
    activePresetId: null,
  });

  browser.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    browser.tabs.sendMessage(tabs[0].id, {
      action: "updateFilters",
      filters: {
        brightness: 1.0,
        contrast: 1.0,
        saturation: 1.0,
        hueRotate: 0,
      },
    });
  });

  presetSelector.value = "";
  deletePresetBtn.disabled = true;
}

// Filter slider event listeners
function updateFilter(filterName, value, displayValue) {
  browser.storage.local.set({ [filterName]: value });

  browser.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    browser.storage.local.get(
      ["brightness", "contrast", "saturation", "hueRotate"],
      (result) => {
        browser.tabs.sendMessage(tabs[0].id, {
          action: "updateFilters",
          filters: {
            brightness: parseFloat(result.brightness || 1.0),
            contrast: parseFloat(result.contrast || 1.0),
            saturation: parseFloat(result.saturation || 1.0),
            hueRotate: parseInt(result.hueRotate || 0),
          },
        });
      }
    );
  });

  // Clear active preset when manually adjusting
  browser.storage.local.set({ activePresetId: null });
  presetSelector.value = "";
  deletePresetBtn.disabled = true;
}

brightnessSlider.addEventListener("input", () => {
  brightnessValue.textContent = brightnessSlider.value;
  updateFilter("brightness", brightnessSlider.value, brightnessSlider.value);
});

contrastSlider.addEventListener("input", () => {
  contrastValue.textContent = contrastSlider.value;
  updateFilter("contrast", contrastSlider.value, contrastSlider.value);
});

saturationSlider.addEventListener("input", () => {
  saturationValue.textContent = saturationSlider.value;
  updateFilter("saturation", saturationSlider.value, saturationSlider.value);
});

hueRotateSlider.addEventListener("input", () => {
  hueRotateValue.textContent = hueRotateSlider.value;
  updateFilter("hueRotate", hueRotateSlider.value, hueRotateSlider.value);
});

// Preset button event listeners
presetSelector.addEventListener("change", () => {
  const presetId = presetSelector.value;
  deletePresetBtn.disabled = !presetId;

  if (presetId) {
    loadPreset(presetId);
  }
});

savePresetBtn.addEventListener("click", () => {
  presetNameContainer.style.display = "flex";
  presetNameInput.value = "";
  presetNameInput.focus();
});

confirmSavePresetBtn.addEventListener("click", () => {
  const name = presetNameInput.value.trim();
  if (name || confirm("Save preset without a name?")) {
    savePreset(name);
    presetNameContainer.style.display = "none";
  }
});

cancelSavePresetBtn.addEventListener("click", () => {
  presetNameContainer.style.display = "none";
  presetNameInput.value = "";
});

presetNameInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    confirmSavePresetBtn.click();
  } else if (e.key === "Escape") {
    cancelSavePresetBtn.click();
  }
});

deletePresetBtn.addEventListener("click", () => {
  const presetId = presetSelector.value;
  if (presetId) {
    deletePreset(presetId);
  }
});

resetFiltersBtn.addEventListener("click", () => {
  resetFilters();
});

function updateVisibility() {
  const showOriginal = showOriginalCheckbox.checked;
  const showColorized = showColorizedCheckbox.checked;
  const sideBySide = sideBySideCheckbox.checked;

  browser.storage.local.set({
    showOriginal: showOriginalCheckbox.checked,
    showColorized: showColorizedCheckbox.checked,
    sideBySide: sideBySideCheckbox.checked,
  });

  browser.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    browser.tabs.sendMessage(tabs[0].id, {
      action: "toggleVisibility",
      showOriginal: showOriginal,
      showColorized: showColorized,
      sideBySide: sideBySide,
    });
  });
}

testApiButton.addEventListener("click", () => {
  browser.tabs.create({ url: urlInput.value, active: true });
  browser.storage.local.set({
    apiURL: urlInput.value.trim(),
  });
});

runButton.addEventListener("click", () => {
  let selectedUpscaleFactor;
  upscaleFactorSelector.forEach((radio) => {
    if (radio.checked) {
      selectedUpscaleFactor = radio.value;
    }
  });

  browser.storage.local.set({
    apiURL: urlInput.value.trim(),
    maxActiveFetches: maxActiveFetches.value.trim(),
    showOriginal: showOriginalCheckbox.checked,
    showColorized: showColorizedCheckbox.checked,
    sideBySide: sideBySideCheckbox.checked,
    cache: cacheCheckbox.checked,
    denoise: denoiseCheckbox.checked,
    colorize: colorizeCheckbox.checked,
    upscale: upscaleCheckbox.checked,
    upscaleFactor: selectedUpscaleFactor,
    tone: toneSelector.value,
    referenceImageURL: referenceImageUrlInput.value.trim(),
    brightness: brightnessSlider.value,
    contrast: contrastSlider.value,
    saturation: saturationSlider.value,
    hueRotate: hueRotateSlider.value,
    denoiseSigma: denoiseSigmaInput.value.trim(),
    colorTolerance: colorToleranceInput.value.trim(),
    colorStride: colorStrideInput.value.trim(),
    websites: websitesInput.value.trim(),
    currentTab: true,
  });

  browser.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    browser.tabs.sendMessage(tabs[0].id, {
      action: "runColorizer",
    });
  });
});

forceRunButton.addEventListener("click", () => {
  forceRunButton.textContent = "Select an Image";
  forceRunButton.disabled = true;
  browser.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.tabs.sendMessage(tabs[0].id, { action: "startSelectMode" });
  });
});

browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "exitSelectMode") {
    forceRunButton.textContent = "Force Colorize!";
    forceRunButton.disabled = false;
  }
});

showOriginalCheckbox.addEventListener("change", updateVisibility);
showColorizedCheckbox.addEventListener("change", updateVisibility);
sideBySideCheckbox.addEventListener("change", updateVisibility);

toneSelector.addEventListener("change", () => {
  const referenceImageContainer = document.getElementById(
    "reference-image-container"
  );
  if (toneSelector.value === "custom") {
    referenceImageContainer.style.display = "flex";
  } else {
    referenceImageContainer.style.display = "none";
  }
  browser.storage.local.set({ tone: toneSelector.value, activePresetId: null });

  // Clear active preset
  presetSelector.value = "";
  deletePresetBtn.disabled = true;
});

referenceImageUrlInput.addEventListener("input", () => {
  browser.storage.local.set({
    referenceImageURL: referenceImageUrlInput.value.trim(),
    activePresetId: null,
  });

  // Clear active preset
  presetSelector.value = "";
  deletePresetBtn.disabled = true;
});
