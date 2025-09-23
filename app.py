import streamlit as st
import joblib
import pandas as pd
import numpy as np

# --- Page Configuration ---
# This sets the title and icon that appear in the browser tab.
st.set_page_config(
    page_title="Carbon Emission Calculator",
    page_icon="♻️",
    layout="centered"
)

# --- Model and Column Loading ---
# We use a caching decorator so the model is loaded only once, making the app faster.
@st.cache_resource
def load_model():
    """Load the trained model and the list of feature columns."""
    try:
        model = joblib.load('carbon_model_final.pkl')
        model_columns = joblib.load('model_columns.pkl')
        return model, model_columns
    except FileNotFoundError:
        # This will display an error in the app if the files are missing.
        st.error("Model files not found! Please make sure 'carbon_model_final.pkl' and 'model_columns.pkl' are in your repository.")
        return None, None

model, model_columns = load_model()

# --- App UI ---
st.title("🌍 Personal Carbon Footprint Calculator")
st.write("Answer the questions below to estimate your monthly carbon emissions. This model is adjusted for a Vietnamese context.")

# Only show the form if the model loaded successfully
if model and model_columns:
    # st.form creates a container for all the inputs. The app only reruns when the user clicks the submit button.
    with st.form("carbon_form"):
        st.header("Your Habits")

        # We'll use columns to make the layout cleaner.
        col1, col2 = st.columns(2)

        with col1:
            body_type = st.selectbox("Body Type", ['underweight', 'normal', 'overweight', 'obese'])
            sex = st.selectbox("Sex", ['male', 'female'])
            diet = st.selectbox("Diet", ['omnivore', 'pescatarian', 'vegetarian', 'vegan'])
            shower_freq = st.selectbox("Shower Frequency", ['daily', 'twice a day', 'more frequently', 'less frequently'], key='How Often Shower')
            heating_source = st.selectbox("Heating Energy Source", ['natural gas', 'electricity', 'wood', 'coal'])
            transport = st.selectbox("Main Mode of Transport", ['walk/bicycle', 'public', 'private'])
            social_activity = st.selectbox("Social Activity", ['never', 'sometimes', 'often'])
            air_travel_freq = st.selectbox("Air Travel Frequency", ['never', 'rarely', 'frequently', 'very frequently'], key='Frequency of Traveling by Air')
        
        with col2:
            waste_bag_size = st.selectbox("Waste Bag Size", ['small', 'medium', 'large', 'extra large'])
            energy_efficiency = st.selectbox("Energy Efficiency Focus", ['No', 'Sometimes', 'Yes'], key='Energy efficiency')
            monthly_grocery = st.number_input("Monthly Grocery Bill ($)", min_value=0.0, value=150.0, step=1.0, key='Monthly Grocery Bill')
            vehicle_dist = st.number_input("Monthly Vehicle Distance (Km)", min_value=0.0, value=0.0, step=10.0, key='Vehicle Monthly Distance Km')
            waste_bag_count = st.number_input("Weekly Waste Bags", min_value=0, value=3, step=1, key='Waste Bag Weekly Count')
            tv_pc_hours = st.number_input("Daily TV/PC Hours", min_value=0, value=5, step=1, key='How Long TV PC Daily Hour')
            new_clothes = st.number_input("Monthly New Clothes", min_value=0, value=3, step=1, key='How Many New Clothes Monthly')
            internet_hours = st.number_input("Daily Internet Hours", min_value=0, value=8, step=1, key='How Long Internet Daily Hour')
        
        # This input is conditional: it only appears if the user selects "private" transport.
        vehicle_type = " "
        if transport == 'private':
            vehicle_type = st.selectbox("Vehicle Type", ['petrol', 'diesel', 'lpg', 'electric', 'hybrid'])

        st.header("Additional Details")
        recycling_options = st.multiselect("What do you recycle?", ['Glass', 'Metal', 'Paper', 'Plastic'])
        cooking_options = st.multiselect("What cooking methods do you use?", ['Airfryer', 'Grill', 'Microwave', 'Oven', 'Stove'])

        # The submit button for the form
        submitted = st.form_submit_button("Calculate My Carbon Emission")

    # This block of code runs ONLY after the user clicks the submit button.
    if submitted:
        # Create a dictionary to hold all the input data, initialized to 0
        input_data = {col: 0 for col in model_columns}

        # Populate the dictionary with the user's selections
        input_data.update({
            'Body Type': body_type, 'Sex': sex, 'Diet': diet, 'How Often Shower': shower_freq,
            'Heating Energy Source': heating_source, 'Transport': transport, 'Vehicle Type': vehicle_type,
            'Social Activity': social_activity, 'Monthly Grocery Bill': monthly_grocery,
            'Frequency of Traveling by Air': air_travel_freq, 'Vehicle Monthly Distance Km': vehicle_dist,
            'Waste Bag Size': waste_bag_size, 'Waste Bag Weekly Count': waste_bag_count,
            'How Long TV PC Daily Hour': tv_pc_hours, 'How Many New Clothes Monthly': new_clothes,
            'How Long Internet Daily Hour': internet_hours, 'Energy efficiency': energy_efficiency
        })
        
        # Handle the multi-select options
        for item in recycling_options: input_data[f"Recycles_{item}"] = 1
        for item in cooking_options: input_data[f"Cooks_with_{item}"] = 1
            
        # Create a DataFrame in the correct order for the model
        input_df = pd.DataFrame([input_data])[model_columns]

        # --- Make Prediction and Adjust for Vietnam ---
        eu_prediction = model.predict(input_df)[0]
        VIETNAM_ADJUSTMENT_FACTOR = 3.243/10.7
        vietnam_prediction = eu_prediction * VIETNAM_ADJUSTMENT_FACTOR

        # --- Display the Result ---
        st.subheader("Your Estimated Monthly Carbon Footprint:")
        # st.metric is a special Streamlit component for displaying a key number
        st.metric(label="Emission", value=f"{vietnam_prediction:.2f} kg CO₂e")
        st.info("This is an estimate based on your inputs. Small lifestyle changes can make a big difference!")