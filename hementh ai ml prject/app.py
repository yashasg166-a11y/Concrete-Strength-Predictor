"""
=============================================================================
CONCRETE COMPRESSIVE STRENGTH PREDICTION — FLASK WEB APPLICATION
=============================================================================
Project    : Prediction of Concrete Compressive Strength Using ML
Course     : AI/ML Open Elective - 4th Semester Civil Engineering
Description: This Flask app serves the frontend HTML page, loads the trained
             ML model, and exposes a REST API endpoint for prediction.
=============================================================================
"""

# ─── IMPORTS ─────────────────────────────────────────────────────────────────
import os
import glob
import joblib
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# ─── FLASK APP INITIALIZATION ─────────────────────────────────────────────────
# Create Flask app instance
# template_folder — where HTML files live
# static_folder   — where CSS/JS/images live
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # Allow Cross-Origin Resource Sharing (needed for fetch() calls)

# ─── LOAD TRAINED MODEL ───────────────────────────────────────────────────────
MODEL_PATH   = os.path.join(os.path.dirname(__file__), "model", "model.pkl")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "model", "metrics.pkl")

# Try to load the model; if not found, guide user to train first
try:
    model = joblib.load(MODEL_PATH)
    print(f"[OK] Model loaded successfully from: {MODEL_PATH}")
except FileNotFoundError:
    model = None
    print("[WARN] model.pkl not found. Please run: python train_model.py")

# Load saved metrics (R², MAE, RMSE, etc.) for the dashboard display
try:
    metrics = joblib.load(METRICS_PATH)
    print(f"[OK] Metrics loaded successfully.")
except FileNotFoundError:
    metrics = {
        "model_name": "Not Trained",
        "r2": 0, "mae": 0, "rmse": 0,
        "lr_r2": 0, "lr_mae": 0, "lr_rmse": 0,
        "rf_r2": 0, "rf_mae": 0, "rf_rmse": 0,
        "train_size": 0, "test_size": 0, "total_rows": 0,
        "features": []
    }
    print("[WARN] metrics.pkl not found. Default metrics loaded.")

# ─── INPUT FEATURES (must match training order exactly) ───────────────────────
FEATURE_ORDER = [
    "cement",       # kg/m³
    "slag",         # kg/m³
    "ash",          # kg/m³
    "water",        # kg/m³
    "superplastic", # kg/m³
    "coarseagg",    # kg/m³
    "fineagg",      # kg/m³
    "age"           # days
]

# ─── HELPER: CLASSIFY STRENGTH ────────────────────────────────────────────────
def classify_strength(strength_mpa: float) -> dict:
    """
    Returns a strength classification label, grade, and engineering
    recommendation based on IS 456:2000 standard.
    """
    if strength_mpa < 20:
        return {
            "label"     : "Low Strength",
            "grade"     : "Below M20",
            "color"     : "low",
            "icon"      : "🟡",
            "usage"     : "Plain concrete, leveling courses, mass concrete fills.",
            "recommendation" : "⚠️ Concrete has LOW compressive strength. Increase cement content or reduce water-cement ratio. Suitable only for non-structural applications."
        }
    elif strength_mpa < 25:
        return {
            "label"     : "Normal Strength",
            "grade"     : "M20",
            "color"     : "normal",
            "icon"      : "🟢",
            "usage"     : "Slabs, beams, columns for mild exposure.",
            "recommendation" : "✅ Meets IS 456 M20 requirements. Suitable for standard indoor RCC structural elements."
        }
    elif strength_mpa < 30:
        return {
            "label"     : "Normal Strength",
            "grade"     : "M25",
            "color"     : "normal",
            "icon"      : "🟢",
            "usage"     : "Foundations, retaining walls, residential buildings.",
            "recommendation" : "✅ Meets IS 456 M25 requirements. Good for moderate exposure structural applications."
        }
    elif strength_mpa < 40:
        return {
            "label"     : "Normal Strength",
            "grade"     : "M30",
            "color"     : "normal",
            "icon"      : "🟢",
            "usage"     : "Heavy structural members, commercial buildings.",
            "recommendation" : "✅ Meets IS 456 M30 requirements. Suitable for severe exposure and heavy loads."
        }
    elif strength_mpa < 50:
        return {
            "label"     : "High Strength",
            "grade"     : "M40",
            "color"     : "high",
            "icon"      : "🔵",
            "usage"     : "Bridges, prestressed concrete, high-rise buildings.",
            "recommendation" : "✅ High strength concrete (M40). Ideal for prestressed members and structural elements in extreme exposure."
        }
    elif strength_mpa < 60:
        return {
            "label"     : "High Strength",
            "grade"     : "M50",
            "color"     : "high",
            "icon"      : "🔵",
            "usage"     : "Pre-cast girders, heavy duty industrial floors.",
            "recommendation" : "✅ High strength concrete (M50). Suitable for heavily loaded columns and long-span bridges."
        }
    else:
        return {
            "label"     : "Very High Strength",
            "grade"     : "M60+",
            "color"     : "very-high",
            "icon"      : "🔴",
            "usage"     : "Marine structures, nuclear plants, skyscrapers.",
            "recommendation" : "🏆 VERY HIGH strength concrete (M60+). Used in special structures requiring exceptional durability and load capacity."
        }

# ─── HELPER: MIX VALIDATION ───────────────────────────────────────────────────
def validate_mix(data) -> dict:
    water = float(data.get("water", 0))
    cement = float(data.get("cement", 0))
    slag = float(data.get("slag", 0))
    ash = float(data.get("ash", 0))
    superplastic = float(data.get("superplastic", 0))
    fineagg = float(data.get("fineagg", 0))
    coarseagg = float(data.get("coarseagg", 0))
    age = float(data.get("age", 0))

    if cement == 0:
        return {"status": "INVALID", "messages": ["Cement content cannot be zero."]}

    total_binder = cement + slag + ash
    wc_ratio = water / total_binder if total_binder > 0 else water / cement
    total_agg = fineagg + coarseagg
    fine_pct = (fineagg / total_agg * 100) if total_agg > 0 else 0

    messages = []
    status = "VALID"

    # W/B Ratio Validation
    if wc_ratio > 1.0:
        status = "INVALID"
        messages.append(f"Water-Binder Ratio ({wc_ratio:.2f}) is extremely high (> 1.0). This mix will not set properly.")
    elif wc_ratio > 0.8:
        if status != "INVALID": status = "HIGH_WARNING"
        messages.append(f"Water-Binder Ratio ({wc_ratio:.2f}) is very high (> 0.8). Severe risk of segregation and bleeding.")
    elif wc_ratio > 0.6:
        if status not in ["INVALID", "HIGH_WARNING"]: status = "WARNING"
        messages.append(f"Water-Binder Ratio ({wc_ratio:.2f}) is high (> 0.6). Strength and durability may be compromised.")
    elif wc_ratio < 0.25:
        if status not in ["INVALID", "HIGH_WARNING"]: status = "WARNING"
        messages.append(f"Water-Binder Ratio ({wc_ratio:.2f}) is very low (< 0.25). The mix will be extremely harsh and unworkable without high superplasticizer dosage.")
    else:
        messages.append(f"Water-Binder Ratio ({wc_ratio:.2f}) is within standard acceptable limits.")

    # Binder Content Validation
    if total_binder < 250:
        if status not in ["INVALID", "HIGH_WARNING"]: status = "WARNING"
        messages.append(f"Total Binder content ({total_binder} kg/m³) is very low. Structural integrity may be compromised.")
    elif total_binder > 600:
        if status not in ["INVALID", "HIGH_WARNING"]: status = "WARNING"
        messages.append(f"Total Binder content ({total_binder} kg/m³) is very high. High risk of thermal cracking and shrinkage.")

    # Aggregate Balance Validation
    if fine_pct < 25:
        if status not in ["INVALID", "HIGH_WARNING"]: status = "WARNING"
        messages.append(f"Fine aggregate is only {fine_pct:.1f}% of total aggregate. Mix may be too harsh and prone to bleeding.")
    elif fine_pct > 55:
        if status not in ["INVALID", "HIGH_WARNING"]: status = "WARNING"
        messages.append(f"Fine aggregate is {fine_pct:.1f}% of total aggregate. High sand content increases water demand and drying shrinkage.")

    # Superplasticizer Validation
    sp_pct = (superplastic / total_binder * 100) if total_binder > 0 else 0
    if sp_pct > 4.0:
        if status not in ["INVALID", "HIGH_WARNING"]: status = "WARNING"
        messages.append(f"Superplasticizer dosage ({sp_pct:.1f}% of binder) is unusually high. Risk of severe retardation and segregation.")

    # Age Bounds
    if age < 1:
        status = "INVALID"
        messages.append("Age must be at least 1 day.")
    elif age > 365:
        if status not in ["INVALID", "HIGH_WARNING"]: status = "WARNING"
        messages.append(f"Age ({age} days) is unusually high for standard testing (typically 28-90 days).")

    return {"status": status, "messages": messages, "wc_ratio": round(wc_ratio, 2)}


# ─── HELPER: SCORES & INSIGHTS ───────────────────────────────────────────────
def calculate_quality_score(wc_ratio, cement) -> int:
    score = 100
    # Deduct for W/C ratio deviation from ideal (0.40)
    ideal_wc = 0.40
    wc_diff = abs(wc_ratio - ideal_wc)
    score -= (wc_diff * 100) # e.g. if wc is 0.6, diff = 0.2 -> -20 points
    
    # Deduct for cement extreme values
    if cement < 250:
        score -= (250 - cement) * 0.2
    elif cement > 450:
        score -= (cement - 450) * 0.1
        
    return max(0, min(100, int(score)))


def calculate_confidence(data) -> dict:
    # Get base R2 from metrics
    base_r2 = metrics.get('r2', 0.90)
    confidence_pct = base_r2 * 100
    
    # Out of dataset detection heuristic
    out_of_bounds = 0
    warnings = []
    
    cement = float(data.get("cement", 0))
    water = float(data.get("water", 0))
    age = float(data.get("age", 0))
    
    # Typical dataset bounds
    if cement < 100 or cement > 540:
        out_of_bounds += 1
        warnings.append("Cement is outside the training dataset range (100-540 kg/m³).")
    if water < 120 or water > 250:
        out_of_bounds += 1
        warnings.append("Water is outside the training dataset range (120-250 kg/m³).")
    if age > 365:
        out_of_bounds += 1
        warnings.append("Age is outside standard training bounds (> 365 days).")
        
    confidence_pct -= (out_of_bounds * 15)
    confidence_pct = max(10, min(99, confidence_pct))
    
    if confidence_pct >= 85: level = "High"
    elif confidence_pct >= 60: level = "Medium"
    else: level = "Low"
    
    return {
        "percentage": int(confidence_pct),
        "level": level,
        "out_of_bounds_warnings": warnings
    }


def generate_engineering_insights(data, wc_ratio, strength) -> list:
    insights = []
    age = float(data.get("age", 0))
    superplastic = float(data.get("superplastic", 0))
    
    if 0.35 <= wc_ratio <= 0.50:
        insights.append("Good water-cement ratio for balanced workability and strength.")
    elif wc_ratio > 0.6:
        insights.append("High water content reduces predicted compressive strength.")
        
    if age == 28:
        insights.append("Standard 28-day curing age provides a reliable strength baseline.")
    elif age < 7:
        insights.append("Early age prediction; concrete is still actively gaining strength.")
    elif age > 90:
        insights.append("Late-age concrete; most strength gain has already occurred.")
        
    if superplastic > 5 and wc_ratio < 0.4:
        insights.append("High superplasticizer dosage compensates for low water content, improving workability.")
        
    return insights

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """
    Returns saved model performance metrics as JSON.
    The frontend calls this on page load to display the Model Statistics card.
    """
    return jsonify(metrics)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Main prediction endpoint.

    Receives a JSON body with concrete mix inputs,
    validates the values, runs the model, and returns the
    predicted compressive strength along with classification.

    Request  (JSON): { "cement": 540, "slag": 0, ... "age": 28 }
    Response (JSON): { "predicted_strength": 79.99, "classification": {...} }
    """
    # ── 1. Check if model is loaded ──
    if model is None:
        return jsonify({
            "error": "Model not found. Please run 'python train_model.py' first."
        }), 503

    # ── 2. Parse request JSON ──
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No JSON data received in request body."}), 400

    # ── 3. Validate all required fields exist ──
    missing_fields = [f for f in FEATURE_ORDER if f not in data]
    if missing_fields:
        return jsonify({
            "error"         : "Missing required input fields.",
            "missing_fields": missing_fields
        }), 400

    # ── 4. Extract and validate numeric values ──
    try:
        input_values = []
        for feature in FEATURE_ORDER:
            val = float(data[feature])

            # Basic sanity checks per feature
            if feature == "age" and val <= 0:
                return jsonify({"error": "Age must be a positive number (days)."}), 400
            if feature == "water" and (val < 100 or val > 300):
                return jsonify({"error": "Water content should be between 100–300 kg/m³."}), 400
            if feature in ("cement", "coarseagg", "fineagg") and val <= 0:
                return jsonify({"error": f"{feature} must be a positive value."}), 400
            if val < 0:
                return jsonify({"error": f"{feature} cannot be negative."}), 400

            input_values.append(val)

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid numeric value: {str(e)}"}), 400

    # ── 5. Run Mix Validation ──
    validation = validate_mix(data)
    if validation["status"] == "INVALID":
        return jsonify({
            "error": "Invalid Concrete Mix",
            "validation": validation,
            "input_received": {f: data[f] for f in FEATURE_ORDER}
        }), 400

    # ── 6. Create feature array and predict ──
    # Reshape to 2D array as sklearn expects [[f1, f2, ..., f8]]
    X_input = np.array(input_values).reshape(1, -1)
    predicted_strength = float(model.predict(X_input)[0])

    # Round to 2 decimal places for cleaner output
    predicted_strength = round(predicted_strength, 2)

    # ── 7. Get classifications, scores, and insights ──
    classification = classify_strength(predicted_strength)
    quality_score = calculate_quality_score(validation["wc_ratio"], float(data["cement"]))
    confidence = calculate_confidence(data)
    insights = generate_engineering_insights(data, validation["wc_ratio"], predicted_strength)

    # ── 8. Return JSON response ──
    return jsonify({
        "predicted_strength" : predicted_strength,
        "unit"               : "MPa",
        "classification"     : classification,
        "validation"         : validation,
        "quality_score"      : quality_score,
        "confidence"         : confidence,
        "insights"           : insights,
        "input_received"     : {f: data[f] for f in FEATURE_ORDER}
    })


@app.route("/api/plot/<filename>")
def serve_plot(filename):
    """Serve generated plot images from static/images."""
    images_dir = os.path.join(app.static_folder, "images")
    return send_from_directory(images_dir, filename)


@app.route("/health")
def health():
    """Health check endpoint — useful for Render deployment monitoring."""
    return jsonify({
        "status"      : "ok",
        "model_loaded": model is not None
    })


# ─── RUN THE APP ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # host='0.0.0.0'  → accessible from outside localhost (required for Render)
    # PORT env var    → Render sets this automatically; defaults to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"

    print("\n" + "=" * 55)
    print("  [STARTING] Concrete Strength Prediction App")
    print(f"  [RUNNING] on: http://localhost:{port}")
    print("=" * 55 + "\n")

    app.run(host="0.0.0.0", port=port, debug=debug)
