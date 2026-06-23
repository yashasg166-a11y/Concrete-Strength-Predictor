# 🏗️ Prediction of Concrete Compressive Strength Using Machine Learning

> **4th Semester Civil Engineering — AI/ML Open Elective Mini Project**

---

## 📌 Abstract

This project applies Machine Learning to predict the **compressive strength of concrete** (in MPa) based on its mix design proportions and curing age. Two regression models — **Linear Regression** and **Random Forest Regressor** — are trained, compared, and the best-performing model is automatically saved and deployed via a Flask web application.

---

## 🎯 Objective

- Predict concrete compressive strength from 8 mix design parameters
- Compare Linear Regression vs Random Forest Regressor
- Build an interactive web app using Flask + HTML/CSS/JS
- Deploy to cloud (Render) for online access

---

## 📁 Project Structure

```
project/
│
├── dataset/
│   └── concrete_strength.csv        ← Dataset (auto-detected)
│
├── model/
│   ├── model.pkl                    ← Saved best ML model
│   └── metrics.pkl                  ← Saved performance metrics
│
├── static/
│   ├── css/
│   │   └── style.css                ← Frontend styles
│   ├── js/
│   │   └── script.js                ← Frontend logic
│   └── images/
│       ├── model_comparison.png     ← Actual vs Predicted plot
│       └── feature_importance.png   ← Feature importance plot
│
├── templates/
│   └── index.html                   ← Main HTML page
│
├── app.py                           ← Flask web application
├── train_model.py                   ← ML model training script
├── requirements.txt                 ← Python dependencies
├── Procfile                         ← Render/Heroku deployment
├── render.yaml                      ← Render deployment config
├── runtime.txt                      ← Python version for Render
├── .gitignore                       ← Git ignore rules
└── README.md                        ← This file
```

---

## 🗄️ Dataset

| Property | Value |
|---|---|
| **Name** | Concrete Compressive Strength Dataset |
| **Source** | Yeh, I-C. (1998). *Modeling of strength of HPC using ANN* |
| **Samples** | 1,031 |
| **Features** | 8 input + 1 target |
| **Format** | CSV |

### Input Features

| # | Feature | Unit | Description |
|---|---|---|---|
| 1 | `cement` | kg/m³ | Portland cement content |
| 2 | `slag` | kg/m³ | Blast furnace slag |
| 3 | `ash` | kg/m³ | Fly ash |
| 4 | `water` | kg/m³ | Water content |
| 5 | `superplastic` | kg/m³ | Superplasticizer |
| 6 | `coarseagg` | kg/m³ | Coarse aggregate |
| 7 | `fineagg` | kg/m³ | Fine aggregate |
| 8 | `age` | days | Curing age |

**Target:** `strength` (MPa) — Compressive Strength

---

## ⚙️ Setup & Installation

### Step 1: Open a Terminal in the Project Folder

```bash
# Navigate to project folder
cd "path/to/hementh ai ml prject"
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Train the Model

```bash
python train_model.py
```

This will:
- ✅ Auto-detect the CSV dataset
- ✅ Train Linear Regression + Random Forest
- ✅ Compare and save the best model as `model/model.pkl`
- ✅ Generate comparison plots in `static/images/`

### Step 5: Run the Web Application

```bash
python app.py
```

### Step 6: Open in Browser

```
http://localhost:5000
```

---

## 🔌 API Reference

### `POST /predict`

**Request Body (JSON):**
```json
{
  "cement": 540,
  "slag": 0,
  "ash": 0,
  "water": 162,
  "superplastic": 2.5,
  "coarseagg": 1040,
  "fineagg": 676,
  "age": 28
}
```

**Response (JSON):**
```json
{
  "predicted_strength": 79.99,
  "unit": "MPa",
  "classification": {
    "label": "Very High Strength",
    "grade": "M60+",
    "color": "very-high",
    "icon": "🔴",
    "usage": "Marine structures, nuclear plants, long-span bridges.",
    "recommendation": "🏆 Concrete has VERY HIGH compressive strength..."
  },
  "input_received": { ... }
}
```

### `GET /api/metrics`
Returns saved model performance metrics (R², MAE, RMSE).

### `GET /health`
Health check endpoint — returns `{"status": "ok", "model_loaded": true}`.

---

## 📊 Strength Classification (IS 456:2000)

| Strength Range | Class | Grade |
|---|---|---|
| < 20 MPa | 🟡 Low Strength | M10 / M15 |
| 20 – 40 MPa | 🟢 Normal Strength | M20 / M25 / M30 |
| 40 – 60 MPa | 🔵 High Strength | M40 / M50 |
| > 60 MPa | 🔴 Very High Strength | M60+ |

---

## 🚀 Deployment on Render

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Concrete Strength Predictor"
git remote add origin https://github.com/YOUR_USERNAME/concrete-strength-predictor.git
git push -u origin main
```

### Step 2: Connect to Render

1. Go to [render.com](https://render.com) → Sign up / Log in
2. Click **New → Web Service**
3. Connect your GitHub repository
4. Render auto-detects `render.yaml` settings

### Step 3: Deploy Settings

| Setting | Value |
|---|---|
| **Build Command** | `pip install -r requirements.txt && python train_model.py` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120` |
| **Runtime** | Python 3.11 |

### Step 4: Verify Deployment

- Visit your Render URL: `https://your-app.onrender.com`
- Test API: `https://your-app.onrender.com/health`

---

## 📈 Results

After training on the Concrete Compressive Strength dataset:

| Model | R² Score | MAE (MPa) | RMSE (MPa) |
|---|---|---|---|
| Linear Regression | ~0.62 | ~8.4 | ~10.5 |
| **Random Forest** | **~0.91** | **~4.2** | **~5.8** |

> Random Forest significantly outperforms Linear Regression due to its ability to capture non-linear relationships in the concrete mix design data.

---

## 🎯 Conclusion

This project successfully demonstrates the application of Machine Learning in Civil Engineering. By utilizing a Random Forest Regressor, we achieved an R² score of ~0.91, proving that AI can accurately predict concrete compressive strength based on mix proportions and curing age. This tool can significantly aid engineers in optimizing concrete mixes, reducing physical testing time, and estimating material performance.

---

## 🔮 Future Scope

- **Advanced Modeling:** Implement extreme Gradient Boosting (XGBoost) or Artificial Neural Networks (ANN) to further improve prediction accuracy.
- **Cost Optimization:** Integrate a feature to estimate the cost of the concrete mix and optimize for both cost and strength.
- **Additional Data:** Train the model on larger, more diverse datasets including different types of admixtures and varying environmental conditions.
- **Mobile Application:** Develop a mobile-friendly application for on-site engineers to make quick predictions in the field.

---

## 🔬 Methodology

```
1. Data Loading        → Auto-detect CSV from dataset/ folder
2. EDA                 → Shape, missing values, statistics
3. Feature Selection   → 8 mix design features → 1 target (strength)
4. Train-Test Split    → 80% train, 20% test (random_state=42)
5. Model Training      → Linear Regression + Random Forest (100 trees)
6. Evaluation          → R², MAE, MSE, RMSE
7. Model Selection     → Best model auto-saved as model.pkl
8. Visualization       → Actual vs Predicted + Feature Importance plots
9. Deployment          → Flask REST API + HTML/CSS/JS frontend
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11 |
| **Web Framework** | Flask 3.0 |
| **ML Library** | Scikit-learn 1.5 |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib |
| **Model Saving** | Joblib |
| **Frontend** | HTML5, CSS3, Vanilla JS |
| **Deployment** | Render (gunicorn) |
| **Version Control** | Git + GitHub |

---

## 👤 Author

**Hemanth**  
4th Semester Civil Engineering  
AI/ML Open Elective Mini Project  
Academic Year: 2024–25

---

## 📚 References

1. Yeh, I-C. (1998). *Modeling of strength of high-performance concrete using artificial neural networks.* Cement and Concrete Research, 28(12), 1797–1808.
2. IS 456:2000 — Plain and Reinforced Concrete — Code of Practice (BIS)
3. Scikit-learn Documentation: https://scikit-learn.org
4. Flask Documentation: https://flask.palletsprojects.com
