import os
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "model.pkl")
model = joblib.load(MODEL_PATH)

FEATURE_ORDER = ["cement", "slag", "ash", "water", "superplastic", "coarseagg", "fineagg", "age"]

def predict(d):
    df = pd.DataFrame([[d["cement"], d["slag"], d["ash"], d["water"], d["superplastic"], d["coarseagg"], d["fineagg"], d["age"]]], columns=FEATURE_ORDER)
    return model.predict(df)[0]

# First: probe what the current presets actually predict
current_presets = {
    "M20_cur": {"cement": 250, "slag": 0, "ash": 0, "water": 150, "superplastic": 0, "coarseagg": 1100, "fineagg": 800, "age": 28},
    "M25_cur": {"cement": 320, "slag": 0, "ash": 0, "water": 160, "superplastic": 2.0, "coarseagg": 1050, "fineagg": 750, "age": 28},
    "M30_cur": {"cement": 380, "slag": 50, "ash": 0, "water": 165, "superplastic": 3.5, "coarseagg": 1000, "fineagg": 720, "age": 28},
    "M40_cur": {"cement": 450, "slag": 0, "ash": 100, "water": 155, "superplastic": 5.0, "coarseagg": 950, "fineagg": 680, "age": 28},
}
print("=== CURRENT PRESET PREDICTIONS ===")
for name, d in current_presets.items():
    print(f"  {name}: {predict(d):.2f} MPa")

print("\n=== SYSTEMATIC SEARCH ===")

# Systematic grid search - vary cement and water primarily
# Target: M20 -> 20-25, M25 -> 25-30, M30 -> 30-40, M40 -> 40-50
# age=28, fix agg, vary cement/water

results = {}
for cement in range(150, 550, 10):
    for water in range(120, 250, 5):
        d = {"cement": cement, "slag": 0, "ash": 0, "water": water, "superplastic": 0, "coarseagg": 1050, "fineagg": 750, "age": 28}
        s = predict(d)
        wc = water / cement
        if wc < 0.3 or wc > 0.9: continue
        for grade, (lo, hi) in [("M20", (20, 25)), ("M25", (25, 30)), ("M30", (30, 40)), ("M40", (40, 50))]:
            if lo <= s <= hi and grade not in results:
                results[grade] = {**d, "strength": round(s, 2)}

for grade, d in results.items():
    print(f"  {grade}: {d}")

# Fill in M30 and M40 with SP if not found yet
if "M30" not in results or "M40" not in results:
    print("\n=== SP-ENHANCED SEARCH ===")
    for cement in range(300, 550, 10):
        for water in range(120, 200, 5):
            for sp in [2.0, 3.5, 5.0, 7.0]:
                d = {"cement": cement, "slag": 0, "ash": 0, "water": water, "superplastic": sp, "coarseagg": 1000, "fineagg": 700, "age": 28}
                s = predict(d)
                wc = water / cement
                if wc < 0.25: continue
                for grade, (lo, hi) in [("M30", (30, 40)), ("M40", (40, 50))]:
                    if lo <= s <= hi and grade not in results:
                        results[grade] = {**d, "strength": round(s, 2)}
                        print(f"  Found {grade}: {results[grade]}")

print("\n=== FINAL RESULTS ===")
for g in ["M20", "M25", "M30", "M40"]:
    print(f"  {g}: {results.get(g, 'NOT FOUND')}")
