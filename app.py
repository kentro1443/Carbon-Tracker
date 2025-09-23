import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request

# Initialize the Flask app
app = Flask(__name__)

# --- Load the Model and Column List ---
# Load the trained pipeline and the list of column names from your .pkl files.
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
        # Start with all expected model columns, initialized to 0
        input_data = {col: 0 for col in model_columns}

        # --- Collect Basic Form Data ---
        form_data = request.form
        for key, value in form_data.items():
            # Standardize the key to match column names (replace space with underscore)
            # This makes it more robust if form names differ slightly
            processed_key = key.replace(' ', '_')
            
            # Find the actual column name that this form key might match
            # This is to handle cases like "Body_Type" vs "Body Type"
            for col in input_data:
                if processed_key.lower() == col.lower().replace(' ', '_'):
                    # Convert numerical fields from string to float
                    if col in ['Monthly Grocery Bill', 'Vehicle Monthly Distance Km', 'Waste Bag Weekly Count', 'How Long TV PC Daily Hour', 'How Many New Clothes Monthly', 'How Long Internet Daily Hour']:
                         input_data[col] = float(value)
                    else: # This is for regular categorical dropdowns
                         input_data[col] = value
                    break

        # --- Handle Multi-Select Data ---
        # Get list of selected items from the form for 'Recycling'
        recycling_options = request.form.getlist('Recycling')
        for item in recycling_options:
            col_name = f"Recycles_{item}"
            if col_name in input_data:
                input_data[col_name] = 1

        # Get list of selected items from the form for 'Cooking_With'
        cooking_options = request.form.getlist('Cooking_With')
        for item in cooking_options:
            # Handle potential space in "Air fryer"
            col_name = f"Cooks_with_{item.replace(' ', '')}"
            if col_name in input_data:
                input_data[col_name] = 1
        
        # --- Create DataFrame for Prediction ---
        # Convert the dictionary into a pandas DataFrame
        # Ensure the column order is exactly as the model expects
        input_df = pd.DataFrame([input_data])
        input_df = input_df[model_columns]
        
        # --- Make Prediction ---
        prediction = model.predict(input_df)
        
        # Format the output
        output = f"{prediction[0]:.2f}"

        return render_template('result.html', prediction=output)

    except Exception as e:
        # Print the error to the console for debugging
        print(f"An error occurred: {e}")
        return f"An error occurred during prediction: {e}", 500

# --- Run the App ---
if __name__ == '__main__':
    # Using host='0.0.0.0' makes the app accessible in Codespaces
    app.run(host='0.0.0.0', port=5000, debug=True)