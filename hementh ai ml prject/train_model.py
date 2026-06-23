"""
=============================================================================
CONCRETE COMPRESSIVE STRENGTH PREDICTION - MODEL TRAINING SCRIPT
=============================================================================
Project    : Prediction of Concrete Compressive Strength Using ML
Course     : AI/ML Open Elective - 4th Semester Civil Engineering
Description: Loads the dataset, trains Linear Regression and Random Forest,
             compares their performance, saves the best model, and generates
             Actual vs Predicted + Feature Importance plots.
=============================================================================
"""

# ─── STEP 1: IMPORT LIBRARIES ────────────────────────────────────────────────
import os
import glob
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')   # non-interactive backend (no display needed)
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# ─── STEP 2: AUTO-DETECT AND LOAD DATASET ────────────────────────────────────
print("=" * 60)
print("  CONCRETE COMPRESSIVE STRENGTH - MODEL TRAINING")
print("=" * 60)

dataset_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
csv_files = glob.glob(os.path.join(dataset_folder, "*.csv"))

if not csv_files:
    raise FileNotFoundError(
        "No CSV file found in the 'dataset/' folder.\n"
        "Please place your CSV dataset file inside the 'dataset/' directory."
    )

dataset_path = csv_files[0]
print("\n[OK] Dataset found:", os.path.basename(dataset_path))

df = pd.read_csv(dataset_path)
print("     Rows:", df.shape[0], " | Columns:", df.shape[1])

# ─── STEP 3: DATA EXPLORATION ────────────────────────────────────────────────
print("\n--- Dataset Preview (First 5 Rows) ---")
print(df.head())

print("\n--- Dataset Statistics ---")
print(df.describe().round(2))

# ─── STEP 4: CHECK FOR MISSING VALUES ────────────────────────────────────────
print("\n--- Missing Values Check ---")
missing = df.isnull().sum()
if missing.sum() == 0:
    print("[OK] No missing values found. Dataset is clean.")
else:
    print(missing[missing > 0])
    print("[WARN] Dropping rows with missing values...")
    df = df.dropna()
    print("      Remaining rows after cleanup:", df.shape[0])

# ─── STEP 5: SELECT FEATURES AND TARGET ──────────────────────────────────────
FEATURE_COLUMNS = [
    "cement",        # kg/m3 - Cement content
    "slag",          # kg/m3 - Blast furnace slag
    "ash",           # kg/m3 - Fly ash
    "water",         # kg/m3 - Water content
    "superplastic",  # kg/m3 - Superplasticizer
    "coarseagg",     # kg/m3 - Coarse aggregate
    "fineagg",       # kg/m3 - Fine aggregate (sand)
    "age"            # days  - Curing age
]

TARGET_COLUMN = "strength"   # MPa - Compressive strength (target)

X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN]

print("\n[OK] Features selected:", FEATURE_COLUMNS)
print("     Target variable  :", TARGET_COLUMN)
print("     X shape          :", X.shape)
print("     y shape          :", y.shape)

# ─── STEP 6: SPLIT INTO TRAIN AND TEST SETS ──────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)
print("\n[OK] Dataset split:")
print("     Training samples :", X_train.shape[0], "(80%)")
print("     Testing samples  :", X_test.shape[0], "(20%)")

# ─── STEP 7: TRAIN MODEL 1 - LINEAR REGRESSION ───────────────────────────────
print("\n--- Training Linear Regression ---")
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
lr_predictions = lr_model.predict(X_test)

lr_r2   = r2_score(y_test, lr_predictions)
lr_mae  = mean_absolute_error(y_test, lr_predictions)
lr_mse  = mean_squared_error(y_test, lr_predictions)
lr_rmse = np.sqrt(lr_mse)

print("     R2 Score :", round(lr_r2, 4))
print("     MAE      :", round(lr_mae, 4), "MPa")
print("     MSE      :", round(lr_mse, 4), "MPa^2")
print("     RMSE     :", round(lr_rmse, 4), "MPa")

# ─── STEP 8: TRAIN MODEL 2 - RANDOM FOREST REGRESSOR ────────────────────────
print("\n--- Training Random Forest Regressor ---")
rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
rf_predictions = rf_model.predict(X_test)

rf_r2   = r2_score(y_test, rf_predictions)
rf_mae  = mean_absolute_error(y_test, rf_predictions)
rf_mse  = mean_squared_error(y_test, rf_predictions)
rf_rmse = np.sqrt(rf_mse)

print("     R2 Score :", round(rf_r2, 4))
print("     MAE      :", round(rf_mae, 4), "MPa")
print("     MSE      :", round(rf_mse, 4), "MPa^2")
print("     RMSE     :", round(rf_rmse, 4), "MPa")

# ─── STEP 9: COMPARE MODELS AND CHOOSE THE BEST ──────────────────────────────
print("\n--- Model Comparison Summary ---")
print(f"{'Metric':<12} {'Linear Regression':>20} {'Random Forest':>20}")
print("-" * 54)
print(f"{'R2 Score':<12} {lr_r2:>20.4f} {rf_r2:>20.4f}")
print(f"{'MAE (MPa)':<12} {lr_mae:>20.4f} {rf_mae:>20.4f}")
print(f"{'RMSE (MPa)':<12} {lr_rmse:>20.4f} {rf_rmse:>20.4f}")

if rf_r2 >= lr_r2:
    best_model        = rf_model
    best_model_name   = "Random Forest Regressor"
    best_r2           = rf_r2
    best_mae          = rf_mae
    best_rmse         = rf_rmse
    best_predictions  = rf_predictions
else:
    best_model        = lr_model
    best_model_name   = "Linear Regression"
    best_r2           = lr_r2
    best_mae          = lr_mae
    best_rmse         = lr_rmse
    best_predictions  = lr_predictions

print("\n[WINNER] Best Model :", best_model_name)
print("         R2 Score   :", round(best_r2, 4))
print("         MAE        :", round(best_mae, 4), "MPa")
print("         RMSE       :", round(best_rmse, 4), "MPa")

# ─── STEP 10: SAVE THE BEST MODEL ────────────────────────────────────────────
model_dir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "model.pkl")
joblib.dump(best_model, model_path)
print("\n[OK] Model saved to:", model_path)

metrics = {
    "model_name" : best_model_name,
    "r2"         : round(best_r2, 4),
    "mae"        : round(best_mae, 4),
    "rmse"       : round(best_rmse, 4),
    "lr_r2"      : round(lr_r2, 4),
    "lr_mae"     : round(lr_mae, 4),
    "lr_rmse"    : round(lr_rmse, 4),
    "rf_r2"      : round(rf_r2, 4),
    "rf_mae"     : round(rf_mae, 4),
    "rf_rmse"    : round(rf_rmse, 4),
    "train_size" : int(X_train.shape[0]),
    "test_size"  : int(X_test.shape[0]),
    "total_rows" : int(df.shape[0]),
    "features"   : FEATURE_COLUMNS,
    "feature_ranges": {col: {"min": float(df[col].min()), "max": float(df[col].max())} for col in FEATURE_COLUMNS}
}
metrics_path = os.path.join(model_dir, "metrics.pkl")
joblib.dump(metrics, metrics_path)
print("[OK] Metrics saved to:", metrics_path)

# ─── STEP 11: PLOT ACTUAL VS PREDICTED VALUES ─────────────────────────────────
print("\n--- Generating Actual vs Predicted Plot ---")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.patch.set_facecolor('#0f172a')

plot_configs = [
    (lr_predictions, lr_r2, "Linear Regression", "#64748b"),
    (rf_predictions, rf_r2, "Random Forest",     "#06b6d4"),
]

for ax, (preds, r2, title, color) in zip(axes, plot_configs):
    ax.set_facecolor('#1e293b')
    ax.scatter(y_test, preds, alpha=0.6, s=25, color=color,
               edgecolors='white', linewidth=0.3, label='Predictions')
    min_val = min(y_test.min(), preds.min())
    max_val = max(y_test.max(), preds.max())
    ax.plot([min_val, max_val], [min_val, max_val],
            'r--', linewidth=2, label='Perfect Fit (y=x)')
    ax.set_xlabel("Actual Strength (MPa)", color='white', fontsize=12)
    ax.set_ylabel("Predicted Strength (MPa)", color='white', fontsize=12)
    ax.set_title(f"{title}\nR2 = {r2:.4f}", color='white', fontsize=13, fontweight='bold')
    ax.legend(facecolor='#334155', edgecolor='white', labelcolor='white')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#475569')
    ax.grid(True, alpha=0.2, color='white')
    ax.text(0.05, 0.93, f"R2={r2:.4f}", transform=ax.transAxes,
            fontsize=11, color='#fbbf24', fontweight='bold')

plt.suptitle("Concrete Compressive Strength - Actual vs Predicted",
             color='white', fontsize=15, fontweight='bold', y=1.01)
plt.tight_layout()

images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images")
os.makedirs(images_dir, exist_ok=True)
plot_path = os.path.join(images_dir, "model_comparison.png")
plt.savefig(plot_path, dpi=130, bbox_inches='tight',
            facecolor='#0f172a', edgecolor='none')
plt.close()
print("[OK] Plot saved to:", plot_path)

# ─── STEP 12: FEATURE IMPORTANCE (Random Forest) ─────────────────────────────
print("--- Generating Feature Importance Plot ---")

fig2, ax2 = plt.subplots(figsize=(10, 5))
fig2.patch.set_facecolor('#0f172a')
ax2.set_facecolor('#1e293b')

importances = rf_model.feature_importances_
indices     = np.argsort(importances)[::-1]
colors_list = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899',
               '#f59e0b', '#10b981', '#ef4444', '#84cc16']

bars = ax2.barh(
    [FEATURE_COLUMNS[i] for i in indices],
    importances[indices],
    color=[colors_list[i % len(colors_list)] for i in range(len(indices))],
    edgecolor='white', linewidth=0.5
)

ax2.set_xlabel("Importance Score", color='white', fontsize=12)
ax2.set_title("Random Forest - Feature Importance", color='white',
              fontsize=13, fontweight='bold')
ax2.tick_params(colors='white')
for spine in ax2.spines.values():
    spine.set_color('#475569')
ax2.grid(True, alpha=0.2, color='white', axis='x')

for bar, val in zip(bars, importances[indices]):
    ax2.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
             f'{val:.3f}', va='center', color='white', fontsize=9)

plt.tight_layout()
feat_plot_path = os.path.join(images_dir, "feature_importance.png")
plt.savefig(feat_plot_path, dpi=130, bbox_inches='tight',
            facecolor='#0f172a', edgecolor='none')
plt.close()
print("[OK] Feature importance plot saved to:", feat_plot_path)

# ─── DONE ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  TRAINING COMPLETE!")
print("  Best Model :", best_model_name)
print("  R2 Score   :", round(best_r2, 4))
print("  MAE        :", round(best_mae, 4), "MPa")
print("  RMSE       :", round(best_rmse, 4), "MPa")
print("=" * 60)
print("\n>> Now run:  python app.py   to start the web application.")
