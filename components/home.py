import streamlit as st
import time

def home_page():
    st.title("🥗 Nutrition Tracker Pro")
    st.write("Track your daily nutrition with ease and precision!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://img.freepik.com/free-vector/chicken-products-flat-set-square-compositions-with-served-food-made-with-poultry-eggs-fastfood-vector-illustration_1284-80268.jpg", 
                 caption="Healthy Eating Starts Here!", width=300)
    with col2:
        st.markdown("""
        ### Features:
        - 📊 Comprehensive Nutrition Tracking
        - 🍽️ Daily Food Logging
        - 📈 Detailed Nutrition Analysis
        - 🧮 Integrated BMI Calculator 
        - 🗂️ Historical Data Management
        """)
    
    st.subheader("📏 Calculate Your BMI")
    st.write("Please enter your BMI information for accurate nutrition tracking.")
    
    if 'last_bmi' not in st.session_state:
        st.session_state.last_bmi = 22.0
    if 'bmi_calculated' not in st.session_state:
        st.session_state.bmi_calculated = False
    
    bmi_col1, bmi_col2, bmi_col3 = st.columns([2, 2, 3])
    with bmi_col1:
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.1, key="weight_input")
    with bmi_col2:
        height = st.number_input("Height (m)", min_value=1.0, max_value=2.5, value=1.7, step=0.01, key="height_input")
    
    if bmi_col3.button("Calculate BMI", key="calculate_bmi"):
        if height > 0:
            calculated_bmi = weight / (height * height)
            st.session_state.last_bmi = round(calculated_bmi, 1)
            st.session_state.height = height
            st.session_state.weight = weight
            st.session_state.bmi_calculated = True
            
            bmi_value = st.session_state.last_bmi
            category = "Underweight" if bmi_value < 18.5 else "Normal weight" if bmi_value < 25 else "Overweight" if bmi_value < 30 else "Obese"
            color = "blue" if bmi_value < 18.5 else "green" if bmi_value < 25 else "orange" if bmi_value < 30 else "red"
            
            st.markdown(f"""
            <div style='background-color: #f0f0f0; padding: 15px; border-radius: 10px; margin-top: 10px;'>
                <h3 style='text-align: center; margin-bottom: 10px; color: black;'>Your BMI Result:</h3>
                <h2 style='text-align: center; color: {color};'>{bmi_value:.1f}</h2>
                <p style='text-align: center; font-weight: bold; color: {color};'>{category}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("BMI Information"):
                st.markdown("""
                **BMI Categories:**
                - Underweight: BMI less than 18.5
                - Normal weight: BMI 18.5 to 24.9
                - Overweight: BMI 25 to 29.9
                - Obese: BMI 30 or greater
                *BMI is a useful screening tool but does not diagnose body fatness or health.*
                """)
    
    elif 'last_bmi' in st.session_state:
        st.info(f"Your current BMI: {st.session_state.last_bmi:.1f}")
        with st.expander("Update BMI Manually"):
            new_bmi = st.number_input(
                "Enter BMI directly", 
                min_value=10.0, 
                max_value=50.0, 
                value=float(st.session_state.last_bmi),
                step=0.1,
                format="%.1f",
                key="manual_bmi_input"
            )
            if st.button("Update", key="update_manual_bmi"):
                st.session_state.last_bmi = round(new_bmi, 1)
                st.session_state.bmi_calculated = True
                st.success(f"BMI updated to {st.session_state.last_bmi:.1f}")
                time.sleep(1)
                st.rerun()