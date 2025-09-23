# ♻️ Carbon Footprint Calculator ♻️

A web application built for the Youth AI Hackathon 2025 to estimate an individual's monthly carbon emissions based on their lifestyle choices. The project aims to raise awareness about personal environmental impact in a simple and interactive way.

This repository contains two complete versions of the application:
1.  A traditional web application built with **Flask** (on the `main` branch).
2.  A data-centric app built with **Streamlit** (on the `streamlit-version` branch).

---

## 🚀 Live Demos

*   **Streamlit Version is live on Streamlit Cloud:** `https://greentracker.streamlit.app/`

---

## ✨ Features

*   **Interactive Web Form:** An easy-to-use interface for users to input their daily habits.
*   **Machine Learning Prediction:** Utilizes a trained `GradientBoostingRegressor` model to provide an instant carbon emission estimate.
*   **Regional Adjustment:** The model, originally trained on EU data, is scaled to provide a more relevant estimate for users in **Vietnam**.
*   **Dual Implementations:** Showcases the same core model deployed using two different popular Python web frameworks.
*   **Accuracy:** 96%

---

## 🛠️ Tech Stack

*   **Machine Learning**: Python, Scikit-learn, Pandas, Joblib
*   **Web Frameworks**:
    *   Flask (`main` branch)
    *   Streamlit (`streamlit-version` branch)
*   **Frontend**: HTML5, CSS3 (for the Flask version)
*   **Development**: GitHub Codespaces
*   **Deployment**: Render.com, Streamlit Cloud

---

## 🧠 The Model: How It Works

The prediction model is the core of this application. Here's a brief overview:

1.  **Dataset**: The model was trained on [this](https://www.kaggle.com/datasets/dumanmesut/individual-carbon-footprint-calculation) dataset, which contains 10,000 anonymous entries detailing individual habits and their resulting carbon emissions.
2.  **Algorithm**: A **Gradient Boosting Regressor** from the Scikit-learn library was used. This is a powerful ensemble technique that builds multiple decision trees sequentially to achieve high prediction accuracy.
3.  **Features**: The model considers a wide range of features, including:
    *   Dietary habits (omnivore, vegan, etc.)
    *   Transportation methods and frequency
    *   Energy consumption at home (heating, electricity)
    *   Consumer habits (shopping, waste production)
4.  **Localization Adjustment**: Recognizing that the training data is from the EU, a scaling factor was applied to the final prediction. Based on 2022 per capita data ([EU](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20250219-1?utm_source=chatgpt.com): 10.7 tonnes, [Vietnam](https://www.ceicdata.com/en/vietnam/environmental-greenhouse-gas-emissions-co2-emissions-annual): 3.243 tonnes), the final output is divided by 3.29941 to better reflect the context of a user in Vietnam.

---

## 📂 Project Structure

The repository is organized into two main branches.

#### `main` Branch (Flask Version)
```
.
├── 📄 app.py                  # The main Flask application logic
├── 📄 carbon_model_final.pkl  # The trained machine learning model
├── 📄 model_columns.pkl       # The list of columns the model expects
├── 📄 requirements.txt        # Python dependencies for Flask
└── 📂 templates/
    ├── 📄 index.html          # The user input form
    └── 📄 result.html         # The page to display the prediction
```

#### `streamlit-version` Branch (Streamlit Version)
```
.
├── 📄 app.py                  # The single file containing all Streamlit UI and logic
├── 📄 carbon_model_final.pkl  # The trained machine learning model
├── 📄 model_columns.pkl       # The list of columns the model expects
└── 📄 requirements.txt        # Python dependencies for Streamlit
```

---

## ⚙️ Getting Started & How to Run Locally

To run this project in a local or cloud environment like Codespaces:

**Prerequisites:**
*   Git
*   Python 3.10+ and `pip`

#### To Run the Flask Version:
```bash
# 1. Switch to the main branch
git checkout main

# 2. Set up a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# 3. Install the required libraries
pip install -r requirements.txt

# 4. Run the Flask application
python app.py

# 5. Open your browser and go to http://127.0.0.1:5000
```

#### To Run the Streamlit Version:
```bash
# 1. Switch to the streamlit-version branch
git checkout streamlit-version

# 2. Set up a virtual environment and install libraries
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run the Streamlit application
streamlit run app.py

# 5. Your browser should open to the app, or you can go to the URL shown in the terminal.
```

---

## 🔮 Future Improvements

*   **Train on Vietnam-Specific Data:** Collect or find a dataset specific to Vietnam for a more accurate model.
*   **Add Detailed Recommendations:** Provide users with specific, actionable tips on how to reduce their score.
*   **User Accounts & Tracking:** Allow users to save their results and track their progress over time.
*   **Expand Feature Set:** Include more granular questions (e.g., specific food types, public transport duration).

---

Built by ADHDers
