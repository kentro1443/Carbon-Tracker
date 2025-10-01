import streamlit as st
import joblib
import pandas as pd
import numpy as np
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Carbon Footprint Calculator",
    page_icon="♻️",
    layout="centered"
)

# --- 2. API AND MODEL LOADING ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Gemini API Key not found. Please add it to your Streamlit secrets.", icon="🔑")

@st.cache_resource
def load_model():
    """Load the prediction model and column list."""
    try:
        model = joblib.load('carbon_model_final.pkl')
        model_columns = joblib.load('model_columns.pkl')
        return model, model_columns
    except FileNotFoundError:
        st.error("Model files not found! Ensure 'carbon_model_final.pkl' and 'model_columns.pkl' are in the repository.")
        return None, None

model, model_columns = load_model()

# --- 3. REVISED LLM HELPER FUNCTIONS ---
def get_initial_recommendations(user_input, carbon_score):
    """Generates CONCISE, English tips."""
    llm = genai.GenerativeModel('gemini-2.5-flash')
    vietnam_average = 270.25
    prompt = f"""
    A user in Vietnam has a monthly carbon score of {carbon_score:.2f} kg CO₂e. The average is {vietnam_average} kg.
    Based on their habits: {user_input}
    Your task:
    1. Provide exactly  short, actionable tips to reduce their score.
    2. Each tip must be a single sentence.
    3. Be encouraging and direct.
    4. CRITICAL: Your entire response must be in English.
    Format the response with a title and two bullet points ONLY.
    """
    try:
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Could not generate recommendations: {e}")
        return "Sorry, recommendations could not be generated at this time."

def get_chat_response(chat_history, user_question, user_context):
    """Generates a CONCISE, English chat response."""
    llm = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    You are an AI environmental assistant chatting with a user in Vietnam.
    Original user data for context: {user_context}
    Chat history: {chat_history}
    User's new question: "{user_question}"
    CRITICAL: Answer in English and keep your response to a maximum of 4 concise sentences.
    """
    try:
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Could not get a chat response: {e}")
        return "Sorry, I'm having trouble responding right now."

# --- 4. SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "carbon_score" not in st.session_state:
    st.session_state.carbon_score = None

# --- 5. APP UI AND LOGIC ---
st.title("🌍 Personal Carbon Footprint Calculator")
st.write("Answer the questions below to estimate your monthly carbon emissions, with advice tailored for Vietnam.")

if model and model_columns:
    with st.form("carbon_form"):
        st.header("👤 Your Habits")
        col1, col2 = st.columns(2)
        
        with col1:
            body_type = st.selectbox("Body Type", ['underweight', 'normal', 'overweight', 'obese'])
            sex = st.selectbox("Sex", ['male', 'female'])
            diet = st.selectbox("Diet", ['omnivore', 'pescatarian', 'vegetarian', 'vegan'])
            shower_freq = st.selectbox("Shower Frequency", ['daily', 'twice a day', 'more frequently', 'less frequently'], key='How Often Shower')
            heating_source = st.selectbox("Heating Energy Source", ['natural gas', 'electricity', 'wood', 'coal'])
            transport = st.selectbox("Main Mode of Transport", ['walk/bicycle', 'public', 'private'])
        
        with col2:
            social_activity = st.selectbox("Social Activity", ['never', 'sometimes', 'often'])
            air_travel_freq = st.selectbox("Air Travel Frequency", ['never', 'rarely', 'frequently', 'very frequently'], key='Frequency of Traveling by Air')
            waste_bag_size = st.selectbox("Waste Bag Size", ['small', 'medium', 'large', 'extra large'])
            energy_efficiency = st.selectbox("Energy Efficiency Focus", ['No', 'Sometimes', 'Yes'], key='Energy efficiency')
            monthly_grocery = st.number_input("Monthly Grocery Bill ($)", min_value=0.0, value=150.0, step=1.0, key='Monthly Grocery Bill')

        st.header("⚙️ Other Details")
        col3, col4 = st.columns(2)
        with col3:
            vehicle_dist = st.number_input("Monthly Vehicle Distance (Km)", min_value=0.0, value=0.0, step=10.0, key='Vehicle Monthly Distance Km')
            waste_bag_count = st.number_input("Weekly Waste Bags", min_value=0, value=3, step=1, key='Waste Bag Weekly Count')
            tv_pc_hours = st.number_input("Daily TV/PC Hours", min_value=0, value=5, step=1, key='How Long TV PC Daily Hour')
        with col4:
            new_clothes = st.number_input("Monthly New Clothes", min_value=0, value=3, step=1, key='How Many New Clothes Monthly')
            internet_hours = st.number_input("Daily Internet Hours", min_value=0, value=8, step=1, key='How Long Internet Daily Hour')
            vehicle_type = " "
            if transport == 'private':
                vehicle_type = st.selectbox("Vehicle Type", ['petrol', 'diesel', 'lpg', 'electric', 'hybrid'])

        recycling_options = st.multiselect("What do you recycle?", ['Glass', 'Metal', 'Paper', 'Plastic'])
        cooking_options = st.multiselect("What cooking methods do you use?", ['Airfryer', 'Grill', 'Microwave', 'Oven', 'Stove'])

        submitted = st.form_submit_button("Calculate & Get Tips")

    if submitted:
        st.session_state.user_data = {
            'Diet': diet, 'Transport': transport, 'Vehicle Distance': vehicle_dist, 'Air Travel': air_travel_freq,
            'Recycling': recycling_options, 'Energy Efficiency': energy_efficiency
        }
        
        model_input_data = {col: 0 for col in model_columns}
        model_input_data.update({
            'Body Type': body_type, 'Sex': sex, 'Diet': diet, 'How Often Shower': shower_freq,
            'Heating Energy Source': heating_source, 'Transport': transport, 'Vehicle Type': vehicle_type,
            'Social Activity': social_activity, 'Monthly Grocery Bill': monthly_grocery,
            'Frequency of Traveling by Air': air_travel_freq, 'Vehicle Monthly Distance Km': vehicle_dist,
            'Waste Bag Size': waste_bag_size, 'Waste Bag Weekly Count': waste_bag_count,
            'How Long TV PC Daily Hour': tv_pc_hours, 'How Many New Clothes Monthly': new_clothes,
            'How Long Internet Daily Hour': internet_hours, 'Energy efficiency': energy_efficiency
        })
        for item in recycling_options: model_input_data[f"Recycles_{item}"] = 1
        for item in cooking_options: model_input_data[f"Cooks_with_{item}"] = 1
        
        input_df = pd.DataFrame([model_input_data])[model_columns]

        eu_prediction = model.predict(input_df)[0]
        vietnam_prediction = eu_prediction * (3.243/10.7)
        st.session_state.carbon_score = vietnam_prediction

        with st.spinner("Analyzing your results..."):
            initial_recs = get_initial_recommendations(st.session_state.user_data, st.session_state.carbon_score)
            st.session_state.messages = [{"role": "assistant", "content": initial_recs}]
            st.rerun()

    # --- 6. DISPLAY RESULTS AND CHAT INTERFACE ---
    if st.session_state.carbon_score is not None:
        st.markdown("---")
        st.subheader("📊 Your Results")
        
        vietnam_average = 270.25
        delta = st.session_state.carbon_score - vietnam_average
        
        st.metric(
            label="Your Estimated Monthly Carbon Emission", 
            value=f"{st.session_state.carbon_score:.2f} kg CO₂e",
            delta=f"{delta:.2f} kg vs. Vietnam Average",
            delta_color="inverse"
        )

        st.subheader("💬 Chat with your AI Assistant")
        
        # Display existing chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # *** NEW LOGIC BLOCK TO FIX THE BUG ***
        # If the last message is from the user, generate a new response
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_chat_response(
                        chat_history=st.session_state.messages,
                        user_question=st.session_state.messages[-1]["content"], # Use the last user message
                        user_context=st.session_state.user_data
                    )
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        # *** END OF NEW LOGIC BLOCK ***

        # Display FAQ buttons only if there's no ongoing chat after the initial recommendation
        if len(st.session_state.messages) == 1:
            st.write("---")
            st.write("**Or, ask a common question:**")
            faq_col1, faq_col2 = st.columns(2)
            faq_questions = [
                "Which habit has the biggest impact?",
                "How does my diet affect my score?",
                "Tell me more about transportation.",
                "How can I save energy at home?"
            ]
            if faq_col1.button(faq_questions[0]):
                st.session_state.messages.append({"role": "user", "content": faq_questions[0]})
                st.rerun()
            if faq_col1.button(faq_questions[1]):
                st.session_state.messages.append({"role": "user", "content": faq_questions[1]})
                st.rerun()
            if faq_col2.button(faq_questions[2]):
                st.session_state.messages.append({"role": "user", "content": faq_questions[2]})
                st.rerun()
            if faq_col2.button(faq_questions[3]):
                st.session_state.messages.append({"role": "user", "content": faq_questions[3]})
                st.rerun()
        
        # Get new user input via the chat box
        if prompt := st.chat_input("Ask a follow-up question!"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun() # Rerun to trigger the new logic block above
else:
    st.warning("Could not load the prediction model. Please check the application logs.")
