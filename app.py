import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request

# Initialize the Flask app
app = Flask(__name__)

# --- Load the Model and Column List ---
try:
    model = joblib.load('carbon_model_final.pkl')
    model_columns = joblib.load('model_columns.pkl')
    print("Model and column list loaded successfully!")
except FileNotFoundError as e:
    print(f"Error loading model files: {e}")
    print("Make sure 'carbon_model_final.pkl' and 'model_columns.pkl' are in the same directory as app.py.")
    model = None
    model_columns = None

# --- Define Routes ---
@app.route('/')
def home():
    """Renders the main input form page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handles the form submission, processes the input, and returns the prediction."""
    if not model or not model_columns:
        return "Model or columns not loaded. Please check the server logs.", 500

    try:
        # --- Create a Dictionary to Hold User Input ---
        input_data = {col: 0 for col in model_columns}

        # --- Collect Basic Form Data ---
        form_data = request.form
        for key, value in form_data.items():
            processed_key = key.replace(' ', '_')
            for col in input_data:
                if processed_key.lower() == col.lower().replace(' ', '_'):
                    if col in ['Monthly Grocery Bill', 'Vehicle Monthly Distance Km', 'Waste Bag Weekly Count', 'How Long TV PC Daily Hour', 'How Many New Clothes Monthly', 'How Long Internet Daily Hour']:
                         input_data[col] = float(value)
                    else:
                         input_data[col] = value
                    break

        # --- Handle Multi-Select Data ---
        recycling_options = request.form.getlist('Recycling')
        for item in recycling_options:
            col_name = f"Recycles_{item}"
            if col_name in input_data:
                input_data[col_name] = 1

        cooking_options = request.form.getlist('Cooking_With')
        for item in cooking_options:
            col_name = f"Cooks_with_{item.replace(' ', '')}"
            if col_name in input_data:
                input_data[col_name] = 1
        
        # --- Create DataFrame for Prediction ---
        input_df = pd.DataFrame([input_data])
        input_df = input_df[model_columns]
        
        # --- Make Prediction and Adjust for Vietnam ---
        eu_prediction = model.predict(input_df)[0]
        VIETNAM_ADJUSTMENT_FACTOR = 3.243/10.7
        vietnam_prediction = eu_prediction * VIETNAM_ADJUSTMENT_FACTOR
        
        # Format the output
        output = f"{vietnam_prediction:.2f}"

        return render_template('result.html', prediction=output)

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred during prediction: {e}", 500

# --- Run the App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)