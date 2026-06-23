/**
 * ============================================================
 * CONCRETE STRENGTH PREDICTOR — FRONTEND JAVASCRIPT
 * Civil Engineering AI/ML Mini Project
 * ============================================================
 * Handles:
 *  - Form submission and validation
 *  - Fetch API call to Flask /predict endpoint
 *  - Dynamic result display (strength, gauge, classification)
 *  - Model metrics loading from /api/metrics
 *  - Quick-fill example buttons
 *  - Viva card toggle
 *  - Navbar scroll effect
 * ============================================================
 */

// Global storage for last prediction (used by PDF generator)
let lastPredictionData = null;

/* ── Quick Example Data ──────────────────────────────────── */
const EXAMPLES = {
  M20: {
    // Calibrated: model predicts ~22 MPa (20–25 range)
    cement: 265, slag: 0, ash: 0, water: 198,
    superplastic: 0, coarseagg: 1100, fineagg: 800, age: 28,
    label: "M20"
  },
  M25: {
    // Calibrated: model predicts ~29.5 MPa (25–30 range)
    cement: 300, slag: 0, ash: 0, water: 180,
    superplastic: 0, coarseagg: 1050, fineagg: 750, age: 28,
    label: "M25"
  },
  M30: {
    // Calibrated: model predicts ~39.7 MPa (30–40 range)
    cement: 340, slag: 0, ash: 0, water: 180,
    superplastic: 1.0, coarseagg: 1000, fineagg: 700, age: 28,
    label: "M30"
  },
  M40: {
    // Calibrated: model predicts ~47.3 MPa (40–50 range)
    cement: 330, slag: 0, ash: 0, water: 160,
    superplastic: 1.0, coarseagg: 1000, fineagg: 700, age: 28,
    label: "M40"
  }
};


/* ── DOM References ──────────────────────────────────────── */
const form         = document.getElementById("predictionForm");
const predictBtn   = document.getElementById("predictBtn");
const btnText      = predictBtn.querySelector(".btn-text");
const btnLoader    = document.getElementById("btnLoader");
const resetBtn     = document.getElementById("resetBtn");

const panelLoading = document.getElementById("resultLoading");
const panelSuccess = document.getElementById("resultSuccess");
const panelError   = document.getElementById("resultError");

/* ── Utility: Show/Hide result panel states ─────────────── */
function showPanel(panel) {
  document.getElementById("resultsSection").style.display = "block";
  [panelLoading, panelSuccess, panelError].forEach(p => {
    p.style.display = "none";
  });
  panel.style.display = "flex";
  if (panel === panelSuccess || panel === panelError) {
    panel.style.display = "block";
  }
}

/* ── Utility: Set loading state on button ───────────────── */
function setLoading(isLoading) {
  predictBtn.disabled = isLoading;
  btnText.textContent = isLoading ? "Predicting..." : "Predict Strength";
  btnLoader.style.display = isLoading ? "inline" : "none";
}

/* ── Utility: Validate individual field ─────────────────── */
function validateField(input) {
  const val = parseFloat(input.value);
  const min = parseFloat(input.min);
  const max = parseFloat(input.max);
  let valid = true;

  if (input.value.trim() === "" || isNaN(val)) {
    valid = false;
  } else if (!isNaN(min) && val < min) {
    valid = false;
  } else if (!isNaN(max) && val > max) {
    valid = false;
  }

  input.classList.toggle("error", !valid);
  return valid;
}

/* ── Utility: Validate all fields ──────────────────────── */
function validateForm() {
  const inputs = form.querySelectorAll(".input-field");
  let allValid = true;
  inputs.forEach(input => {
    if (!validateField(input)) allValid = false;
  });
  return allValid;
}

/* ── Add live validation on each input ─────────────────── */
document.querySelectorAll(".input-field").forEach(input => {
  input.addEventListener("input", () => validateField(input));
  input.addEventListener("blur",  () => validateField(input));
});

/* ── Fill example data ──────────────────────────────────── */
function fillExample(type) {
  const data = EXAMPLES[type];
  if (!data) return;

  // Fill each field
  Object.keys(data).forEach(key => {
    const el = document.getElementById(key);
    if (el) {
      el.value = data[key];
      el.classList.remove("error");
    }
  });

  // Animate fields
  document.querySelectorAll(".input-field").forEach((el, i) => {
    el.style.transition = `background 0.4s ease ${i * 0.05}s`;
    el.style.background = "rgba(14,165,233,0.1)";
    setTimeout(() => { el.style.background = ""; }, 800 + i * 50);
  });
}

/* ── Update strength gauge ──────────────────────────────── */
function updateGauge(strength) {
  const maxStrength = 80;                          // 80 MPa = 100% on gauge
  const pct = Math.min((strength / maxStrength) * 100, 100);

  const fill   = document.getElementById("gaugeFill");
  const marker = document.getElementById("gaugeMarker");

  // Use timeout so CSS transition fires after display is set
  setTimeout(() => {
    fill.style.width     = pct + "%";
    marker.style.left    = pct + "%";
  }, 100);

  // Colour gradient based on strength
  let colour;
  if      (strength < 20) colour = "linear-gradient(90deg, #f59e0b, #fbbf24)";
  else if (strength < 40) colour = "linear-gradient(90deg, #10b981, #34d399)";
  else if (strength < 60) colour = "linear-gradient(90deg, #0ea5e9, #38bdf8)";
  else                    colour = "linear-gradient(90deg, #f43f5e, #fb7185)";

  fill.style.background = colour;
  fill.style.boxShadow  = colour.includes("f43f5e") ? "0 0 10px rgba(244,63,94,.5)"
                        : colour.includes("10b981") ? "0 0 10px rgba(16,185,129,.5)"
                        : colour.includes("f59e0b") ? "0 0 10px rgba(245,158,11,.5)"
                        : "0 0 10px rgba(14,165,233,.5)";
}

/* ── Display prediction result ──────────────────────────── */
function displayResult(data) {
  const strength = data.predicted_strength;
  const cls      = data.classification;

  // Strength value with animated count-up
  const strengthEl = document.getElementById("strengthValue");
  animateNumber(strengthEl, 0, strength, 900);

  // Gauge
  updateGauge(strength);

  // Classification card
  document.getElementById("classIcon").textContent  = cls.icon;
  document.getElementById("classLabel").textContent = cls.label;
  document.getElementById("classGrade").textContent = cls.grade;
  document.getElementById("classUsage").textContent = "📍 Use: " + cls.usage;
  document.getElementById("classRec").textContent   = cls.recommendation;

  // Mix Validation Alert + W/C Ratio
  if (data.validation) {
    const valCard = document.getElementById("validationCard");
    const valIcon = document.getElementById("valIcon");
    const valStatus = document.getElementById("valStatus");
    const valMsgs = document.getElementById("valMessages");
    const v = data.validation;
    
    valCard.className = "validation-card " + v.status.toLowerCase();
    if(v.status === "VALID") valIcon.textContent = "✅";
    else if(v.status === "WARNING" || v.status === "HIGH_WARNING") valIcon.textContent = "⚠️";
    else valIcon.textContent = "❌";
    valStatus.textContent = v.status.replace(/_/g, " ");
    
    valMsgs.innerHTML = "";
    v.messages.forEach(m => {
      let li = document.createElement("li");
      li.textContent = m;
      valMsgs.appendChild(li);
    });

    // W/C Ratio display with color-coded badge
    const wcRatioEl  = document.getElementById("wcRatioValue");
    const wcBadgeEl  = document.getElementById("wcRatioBadge");
    if (wcRatioEl && v.wc_ratio !== undefined) {
      wcRatioEl.textContent  = v.wc_ratio;
      wcBadgeEl.textContent  = v.status.replace(/_/g, " ");
      wcBadgeEl.className    = "wc-badge " + v.status.toLowerCase();
    }
  }

  // Quality & Confidence
  if (data.quality_score !== undefined) {
    document.getElementById("qualityScore").textContent = data.quality_score + "/100";
    document.getElementById("confidenceScore").textContent = data.confidence.percentage + "%";
    document.getElementById("confidenceLevel").textContent = data.confidence.level;
    
    // Out of Dataset Warnings
    const oodContainer = document.getElementById("oodWarningsContainer");
    const oodList = document.getElementById("oodWarningsList");
    if (data.confidence.out_of_bounds_warnings && data.confidence.out_of_bounds_warnings.length > 0) {
      oodList.innerHTML = "";
      data.confidence.out_of_bounds_warnings.forEach(w => {
        let li = document.createElement("li");
        li.textContent = w;
        oodList.appendChild(li);
      });
      oodContainer.style.display = "block";
    } else {
      oodContainer.style.display = "none";
    }
  }

  // Insights
  if (data.insights) {
    const insightsList = document.getElementById("insightsList");
    insightsList.innerHTML = "";
    data.insights.forEach(m => {
      let li = document.createElement("li");
      li.textContent = m;
      insightsList.appendChild(li);
    });
  }

  // Set result panel colour class based on strength class
  const panel = document.querySelector(".result-panel");
  panel.className = "result-panel strength-" + cls.color;

  // Input summary
  const summaryGrid = document.getElementById("summaryGrid");
  const labels = {
    cement: "Cement", slag: "Slag", ash: "Fly Ash", water: "Water",
    superplastic: "Superpl.", coarseagg: "Coarse Agg.", fineagg: "Fine Agg.", age: "Age (days)"
  };
  summaryGrid.innerHTML = "";
  const inputs = data.input_received;
  Object.keys(inputs).forEach(key => {
    const div = document.createElement("div");
    div.className = "summary-item";
    div.innerHTML = `<span class="sum-key">${labels[key] || key}</span>
                     <span class="sum-val">${inputs[key]}</span>`;
    summaryGrid.appendChild(div);
  });

  updateMaterials();
  saveHistory(data);

  // Store for PDF generation
  lastPredictionData = data;
  const pdfBtn = document.getElementById("pdfBtn");
  if (pdfBtn) pdfBtn.style.display = "inline-flex";

  showPanel(panelSuccess);
}

/* ── Material Calculator ────────────────────────────────── */
const volumeInput = document.getElementById("volume");
if (volumeInput) {
  volumeInput.addEventListener("input", updateMaterials);
}

function updateMaterials() {
  const vol = parseFloat(document.getElementById("volume").value) || 1;
  const matVolume = document.getElementById("matVolume");
  if (matVolume) matVolume.textContent = vol;
  
  const cement = parseFloat(document.getElementById("cement").value) || 0;
  const water = parseFloat(document.getElementById("water").value) || 0;
  const fine = parseFloat(document.getElementById("fineagg").value) || 0;
  const coarse = parseFloat(document.getElementById("coarseagg").value) || 0;

  const matCement = document.getElementById("matCement");
  if (matCement) matCement.textContent = ((cement * vol) / 50).toFixed(1);
  const matWater = document.getElementById("matWater");
  if (matWater) matWater.textContent = (water * vol).toFixed(1);
  const matFine = document.getElementById("matFine");
  if (matFine) matFine.textContent = (fine * vol).toFixed(0);
  const matCoarse = document.getElementById("matCoarse");
  if (matCoarse) matCoarse.textContent = (coarse * vol).toFixed(0);
}

/* ── Prediction History ─────────────────────────────────── */
let historyArray = JSON.parse(localStorage.getItem("concreteHistory")) || [];

function saveHistory(data) {
  historyArray.unshift({
    strength: data.predicted_strength,
    grade: data.classification.grade,
    cement: data.input_received.cement,
    water: data.input_received.water,
    timestamp: new Date().toLocaleTimeString()
  });
  if(historyArray.length > 5) historyArray.pop();
  localStorage.setItem("concreteHistory", JSON.stringify(historyArray));
  renderHistory();
}

function renderHistory() {
  const list = document.getElementById("historyList");
  const clearBtn = document.getElementById("clearHistoryBtn");
  if (!list) return;
  
  if(historyArray.length === 0) {
    list.innerHTML = '<div class="history-empty">No predictions yet. Run a prediction to save history.</div>';
    if(clearBtn) clearBtn.style.display = "none";
    return;
  }
  
  list.innerHTML = "";
  historyArray.forEach(h => {
    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML = `
      <div>
        <div class="history-item-str">${h.strength} MPa</div>
        <div class="history-item-details">${h.grade} | C: ${h.cement} kg | W: ${h.water} L</div>
      </div>
      <div style="font-size:0.7rem; color:var(--text-muted);">${h.timestamp}</div>
    `;
    list.appendChild(div);
  });
  if(clearBtn) clearBtn.style.display = "inline-block";
}

window.clearHistory = function() {
  historyArray = [];
  localStorage.setItem("concreteHistory", "[]");
  renderHistory();
};

/* ── Animated number count-up ───────────────────────────── */
function animateNumber(el, from, to, duration) {
  const start = performance.now();
  function step(ts) {
    const elapsed = ts - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 4);    // ease-out-quart
    const current = from + (to - from) * eased;
    el.textContent = current.toFixed(2);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ── Form Submit Handler ────────────────────────────────── */
form.addEventListener("submit", async function (e) {
  e.preventDefault();   // Prevent default page reload

  // Validate all inputs first
  if (!validateForm()) {
    // Flash red border on invalid fields
    document.querySelectorAll(".input-field.error")[0]?.focus();
    return;
  }

  // Collect form data as a plain object
  const formData = new FormData(form);
  const payload  = {};
  formData.forEach((value, key) => {
    payload[key] = parseFloat(value);   // Flask expects numbers
  });

  // Show loading state
  setLoading(true);
  showPanel(panelLoading);

  try {
    // ── Send POST request to Flask API ──
    const response = await fetch("/predict", {
      method : "POST",
      headers: { "Content-Type": "application/json" },
      body   : JSON.stringify(payload)
    });

    // Parse JSON response
    const data = await response.json();

    if (!response.ok) {
      if (data.validation && data.validation.status === "INVALID") {
        throw new Error(data.error + ": " + data.validation.messages.join(" "));
      }
      throw new Error(data.error || `Server error: ${response.status}`);
    }

    // Display the result
    displayResult(data);

  } catch (err) {
    // Show error state
    document.getElementById("errorMessage").textContent =
      err.message || "Could not connect to the prediction server. Make sure Flask is running.";
    showPanel(panelError);
    console.error("Prediction error:", err);

  } finally {
    // Always re-enable button
    setLoading(false);
  }
});

/* ── Reset Button ───────────────────────────────────────── */
resetBtn.addEventListener("click", function () {
  form.reset();
  document.querySelectorAll(".input-field").forEach(el => {
    el.classList.remove("error");
    el.style.background = "";
  });

  // Reset gauge
  const fill = document.getElementById("gaugeFill");
  const marker = document.getElementById("gaugeMarker");
  if (fill)   { fill.style.width = "0%"; fill.style.background = ""; }
  if (marker) { marker.style.left = "0%"; }

  // Reset result panel class
  document.querySelector(".result-panel").className = "result-panel";

  showPanel(panelDefault);
});

/* ── Load Model Metrics from API ────────────────────────── */
async function loadMetrics() {
  try {
    const res = await fetch("/api/metrics");
    if (!res.ok) return;
    const m = await res.json();

    // Hero stats
    const heroR2 = document.getElementById("hero-r2");
    const heroTotal = document.getElementById("hero-total");
    if (heroR2)    heroR2.textContent    = m.r2 || "—";
    if (heroTotal) heroTotal.textContent = m.total_rows || "1031";

    // Winner card
    setText("winnerName", m.model_name || "—");
    setText("wm-r2",      m.r2   !== undefined ? m.r2   : "—");
    setText("wm-mae",     m.mae  !== undefined ? m.mae  : "—");
    setText("wm-rmse",    m.rmse !== undefined ? m.rmse : "—");
    setText("wm-total",   m.total_rows || "—");
    setText("wm-train",   m.train_size  || "—");
    setText("wm-test",    m.test_size   || "—");

    // Comparison table
    setText("ct-lr-r2",   m.lr_r2   !== undefined ? m.lr_r2   : "—");
    setText("ct-lr-mae",  m.lr_mae  !== undefined ? m.lr_mae  : "—");
    setText("ct-lr-rmse", m.lr_rmse !== undefined ? m.lr_rmse : "—");
    setText("ct-rf-r2",   m.rf_r2   !== undefined ? m.rf_r2   : "—");
    setText("ct-rf-mae",  m.rf_mae  !== undefined ? m.rf_mae  : "—");
    setText("ct-rf-rmse", m.rf_rmse !== undefined ? m.rf_rmse : "—");

    // Highlight the winning column in the comparison table
    highlightWinner(m.model_name);

    // ── Populate Dataset Range Panel ──
    const featureLabels = {
      cement: "kg/m³", slag: "kg/m³", ash: "kg/m³", water: "L/m³",
      superplastic: "kg/m³", coarseagg: "kg/m³", fineagg: "kg/m³", age: "Days"
    };
    if (m.feature_ranges) {
      Object.keys(m.feature_ranges).forEach(key => {
        const el = document.getElementById("r-" + key);
        if (el) {
          const r = m.feature_ranges[key];
          el.textContent = `${r.min.toFixed(0)} – ${r.max.toFixed(0)} ${featureLabels[key] || ""}`;
        }
      });
    }

  } catch (err) {
    console.warn("Could not load metrics (run train_model.py first):", err.message);
  }
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function highlightWinner(modelName) {
  if (!modelName) return;
  const isRF = modelName.toLowerCase().includes("random");
  const col  = isRF ? 3 : 2;   // column 3 = RF, column 2 = LR
  document.querySelectorAll(".comp-table tbody tr").forEach(row => {
    const cell = row.cells[col - 1];
    if (cell) {
      cell.style.color      = "#10b981";
      cell.style.fontWeight = "700";
    }
  });
}

/* ── Viva Card Toggle ───────────────────────────────────── */
function toggleViva(card) {
  card.classList.toggle("open");
}

/* ── Navbar scroll effect ───────────────────────────────── */
window.addEventListener("scroll", function () {
  const navbar = document.getElementById("navbar");
  if (window.scrollY > 40) {
    navbar.style.background = "rgba(6, 13, 26, 0.97)";
    navbar.style.boxShadow  = "0 2px 20px rgba(0,0,0,0.5)";
  } else {
    navbar.style.background = "rgba(6, 13, 26, 0.85)";
    navbar.style.boxShadow  = "none";
  }
});

/* ── Smooth scroll for nav links ────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      const offset = 80;   // navbar height
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: "smooth" });
    }
  });
});

/* ── Intersection Observer: animate elements on scroll ─── */
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.animation = "fadeUp 0.6s ease forwards";
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll(".overview-card, .viva-card, .cref, .plot-card").forEach(el => {
  el.style.opacity = "0";
  observer.observe(el);
});

/* ── Initialize ────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  loadMetrics();
  renderHistory();
  updateMaterials();

  // Hide PDF button until after first prediction
  const pdfBtn = document.getElementById("pdfBtn");
  if (pdfBtn) pdfBtn.style.display = "none";

  // Show placeholder images if model plots don't exist
  document.querySelectorAll(".plot-img").forEach(img => {
    img.addEventListener("error", function () {
      this.parentElement.innerHTML = `
        <div class="plot-placeholder">
          📊 Run <code>python train_model.py</code> first to generate this plot
        </div>`;
    });
  });
});

/* ── Generate PDF Report ─────────────────────────────── */
window.generatePDF = function() {
  if (!lastPredictionData) {
    alert("Please run a prediction first before generating a report.");
    return;
  }

  const d = lastPredictionData;
  const cls = d.classification;
  const val = d.validation;
  const vol = parseFloat(document.getElementById("volume").value) || 1;

  // Set date-time
  document.getElementById("pdfDateTime").textContent = new Date().toLocaleString();

  // Input parameters table
  const inputLabels = [
    ["Cement",           d.input_received.cement,      "kg/m³"],
    ["Water",            d.input_received.water,       "L/m³"],
    ["Blast Furnace Slag",d.input_received.slag,       "kg/m³"],
    ["Fly Ash",          d.input_received.ash,         "kg/m³"],
    ["Superplasticizer", d.input_received.superplastic,"kg/m³"],
    ["Fine Aggregate",   d.input_received.fineagg,     "kg/m³"],
    ["Coarse Aggregate", d.input_received.coarseagg,   "kg/m³"],
    ["Curing Age",       d.input_received.age,         "days"],
    ["Concrete Volume",  vol,                          "m³"]
  ];

  const inputTbody = document.getElementById("pdfInputTableBody");
  inputTbody.innerHTML = "";
  inputLabels.forEach(([label, val, unit], i) => {
    inputTbody.innerHTML += `<tr style="${i%2===0?'background:#f8fafc;':''}"><td style="padding:6px 10px;border:1px solid #ddd;font-weight:600;">${label}</td><td style="padding:6px 10px;border:1px solid #ddd;text-align:right;font-family:monospace;">${val}</td><td style="padding:6px 10px;border:1px solid #ddd;text-align:center;color:#666;">${unit}</td></tr>`;
  });

  // Prediction results
  document.getElementById("pdfStrength").textContent  = d.predicted_strength + " MPa";
  document.getElementById("pdfClass").textContent     = cls.label;
  document.getElementById("pdfGrade").textContent     = cls.grade;
  document.getElementById("pdfConfidence").textContent= d.confidence.percentage + "% (" + d.confidence.level + ")";
  document.getElementById("pdfQuality").textContent   = d.quality_score + "/100";
  document.getElementById("pdfWCRatio").textContent   = val.wc_ratio;
  document.getElementById("pdfValidation").textContent= val.status.replace(/_/g, " ");

  // Insights
  const insightsList = document.getElementById("pdfInsightsList");
  insightsList.innerHTML = "";
  (d.insights || []).forEach(ins => {
    insightsList.innerHTML += `<li style="margin-bottom:4px;">✓ ${ins}</li>`;
  });
  if (!d.insights || d.insights.length === 0) {
    insightsList.innerHTML = "<li>No specific insights generated for this mix.</li>";
  }

  // Recommendations
  document.getElementById("pdfRecommendation").textContent = cls.recommendation.replace(/[✅⚠️🏆]/g, "").trim();

  // Material estimation
  const cement  = parseFloat(d.input_received.cement)  || 0;
  const water   = parseFloat(d.input_received.water)   || 0;
  const fine    = parseFloat(d.input_received.fineagg)  || 0;
  const coarse  = parseFloat(d.input_received.coarseagg)|| 0;
  const cementKg   = (cement * vol).toFixed(0);
  const cementBags = (cement * vol / 50).toFixed(1);
  const waterL     = (water  * vol).toFixed(1);
  const fineKg     = (fine   * vol).toFixed(0);
  const coarseKg   = (coarse * vol).toFixed(0);

  const matTbody = document.getElementById("pdfMaterialTableBody");
  const matRows = [
    ["Cement",           `${cementKg} kg  (≈ ${cementBags} bags)`, `${vol} m³`],
    ["Water",            `${waterL} Liters`,                         `${vol} m³`],
    ["Fine Aggregate (Sand)",  `${fineKg} kg`,                       `${vol} m³`],
    ["Coarse Aggregate (Gravel)",`${coarseKg} kg`,                    `${vol} m³`]
  ];
  matTbody.innerHTML = "";
  matRows.forEach(([label, qty, v], i) => {
    matTbody.innerHTML += `<tr style="${i%2===0?'background:#fdf4ff;':''}"><td style="padding:6px 10px;border:1px solid #ddd;font-weight:600;">${label}</td><td style="padding:6px 10px;border:1px solid #ddd;text-align:right;font-family:monospace;">${qty}</td><td style="padding:6px 10px;border:1px solid #ddd;text-align:right;color:#666;">${v}</td></tr>`;
  });

  // Reveal hidden template and render
  const template = document.getElementById("pdfReportTemplate");
  template.style.display = "block";
  const element = document.getElementById("pdfContent");

  const opt = {
    margin:       [10, 10, 10, 10],
    filename:     `Concrete_Report_${new Date().toISOString().slice(0,10)}.pdf`,
    image:        { type: "jpeg", quality: 0.98 },
    html2canvas:  { scale: 2, useCORS: true, backgroundColor: "#ffffff" },
    jsPDF:        { unit: "mm", format: "a4", orientation: "portrait" }
  };

  html2pdf()
    .set(opt)
    .from(element)
    .save()
    .then(() => {
      template.style.display = "none";
    })
    .catch(err => {
      template.style.display = "none";
      console.error("PDF generation failed:", err);
    });
};
