import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime, timedelta
import random
from statsmodels.tsa.arima.model import ARIMA
from database import daily_log_collection
from utils import DIET_GOALS, calculate_bmi_adjusted_goals

def nutrition_analysis():
    st.title("📊 Nutrition Analysis")
    
    if 'bmi_calculated' not in st.session_state or not st.session_state.bmi_calculated:
        st.warning("Please calculate your BMI on the Home page first!")
        if st.button("Go to Home Page"):
            st.session_state.page = "Home"
            st.rerun()
        st.stop()
    
    st.subheader("Personalize Your Analysis")
    st.info(f"Current BMI: {st.session_state.last_bmi:.1f}")
    diet_type = st.selectbox("Select Diet Type", list(DIET_GOALS.keys()))
    adjusted_goals = calculate_bmi_adjusted_goals(st.session_state.last_bmi, DIET_GOALS[diet_type])
    st.session_state.adjusted_goals = adjusted_goals
    st.info(f"Your BMI-adjusted daily goals: {adjusted_goals['calories']} calories, "
            f"{adjusted_goals['protein']}g protein, {adjusted_goals['carbs']}g carbs, {adjusted_goals['fat']}g fat")
    
    today_logs = list(daily_log_collection.find({"date": {"$gte": datetime.now() - timedelta(days=1)}}))
    if not today_logs:
        st.warning("No food logs for today.")
        return
    
    total_nutrients = {"Calories": 0, "Protein": 0, "Carbohydrates": 0, "Fat": 0}
    food_breakdown = {}
    for log in today_logs:
        nutrients = log.get('nutrients', {})
        food_name = log.get('food_name', 'Unknown')
        total_nutrients["Calories"] += nutrients.get('energy-kcal', 0)
        total_nutrients["Protein"] += nutrients.get('proteins', 0)
        total_nutrients["Carbohydrates"] += nutrients.get('carbohydrates', 0)
        total_nutrients["Fat"] += nutrients.get('fat', 0)
        food_breakdown[food_name] = nutrients.get('energy-kcal', 0)
    
    top_col1, top_col2 = st.columns(2)
    with top_col1:
        pie_df = pd.DataFrame.from_dict(total_nutrients, orient='index', columns=['Value'])
        pie_df = pie_df[pie_df['Value'] > 0]
        fig_pie = px.pie(pie_df, values='Value', names=pie_df.index, title='Macronutrient Distribution')
        st.plotly_chart(fig_pie)
    with top_col2:
        fig_bar = px.bar(x=list(food_breakdown.keys()), y=list(food_breakdown.values()), title='Calorie Contribution by Food')
        fig_bar.update_xaxes(title='Foods')
        fig_bar.update_yaxes(title='Calories')
        st.plotly_chart(fig_bar)
    
    historical_logs = list(daily_log_collection.find({"date": {"$gte": datetime.now() - timedelta(days=7)}}))
    if not historical_logs:
        st.warning("No historical data available for the past 7 days.")
        hist_df = pd.DataFrame(columns=['Date', 'Calories', 'Protein', 'Carbohydrates'])
    else:
        hist_data = {}
        for log in historical_logs:
            date = log['date'].strftime('%Y-%m-%d')
            nutrients = log.get('nutrients', {})
            if date not in hist_data:
                hist_data[date] = {'Calories': 0, 'Protein': 0, 'Carbohydrates': 0}
            hist_data[date]['Calories'] += nutrients.get('energy-kcal', 0)
            hist_data[date]['Protein'] += nutrients.get('proteins', 0)
            hist_data[date]['Carbohydrates'] += nutrients.get('carbohydrates', 0)
        hist_df = pd.DataFrame.from_dict(hist_data, orient='index').reset_index()
        hist_df.columns = ['Date', 'Calories', 'Protein', 'Carbohydrates']
        hist_df = hist_df.sort_values('Date')
        
        fig_line = go.Figure()
        for nutrient in ['Calories', 'Protein', 'Carbohydrates']:
            fig_line.add_trace(go.Scatter(x=hist_df['Date'], y=hist_df[nutrient], mode='lines+markers', name=nutrient))
        fig_line.update_layout(title='7-Day Nutrient Trend', xaxis_title='Date', yaxis_title='Amount')
        st.plotly_chart(fig_line)
    
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    
    st.subheader("Nutritional Status")
    goal_cols = st.columns(4)
    goal_key_map = {"Calories": "calories", "Protein": "protein", "Carbohydrates": "carbs", "Fat": "fat"}
    for i, (nutrient, actual) in enumerate(total_nutrients.items()):
        goal_key = goal_key_map.get(nutrient, nutrient.lower())
        goal = adjusted_goals.get(goal_key, 0)
        percentage = (actual / goal) * 100 if goal > 0 else 0
        goal_cols[i].metric(nutrient, f"{actual:.1f} / {goal}", f"{percentage:.1f}%")
    
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    
    st.subheader("Daily Progress")
    progress_cols = st.columns(4)
    nutrient_values = {
        "Calories": (total_nutrients["Calories"], adjusted_goals["calories"]),
        "Protein": (total_nutrients["Protein"], adjusted_goals["protein"]),
        "Carbohydrates": (total_nutrients["Carbohydrates"], adjusted_goals["carbs"]),
        "Fat": (total_nutrients["Fat"], adjusted_goals["fat"])
    }
    for i, (nutrient, (current, goal)) in enumerate(nutrient_values.items()):
        with progress_cols[i]:
            st.write(nutrient)
            current_progress = min(1.0, current / goal) if goal > 0 else 0
            progress_html = f"""
            <div style="position: relative; width: 100%; height: 20px;">
                <div style="position: absolute; width: 100%; height: 100%; background-color: #4e8cff; border-radius: 5px; z-index: 1; opacity: 0.7;" title="Goal: {goal:.1f}"></div>
                <div style="position: absolute; width: {current_progress * 100}%; height: 100%; background-color: #ffeb3b; border-radius: 5px; z-index: 2; opacity: 0.9;" title="Current: {current:.1f}"></div>
            </div>
            <div style="text-align: center; margin-top: 5px;">
                <span style="color: #ffeb3b;">{current:.1f}</span> / <span style="color: #4e8cff;">{goal:.1f}</span>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
    st.markdown("""
    <small style="color: #666;">
        <span style="color: #ffeb3b;">Yellow</span> = Amount taken | 
        <span style="color: #4e8cff;">Blue</span> = Adjusted goal
    </small>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    
    st.subheader("Personal Insights")
    col_score, col_predict = st.columns(2)
    with col_score:
        score = sum(max(0, 100 - abs(current - goal) / goal * 100) for _, (current, goal) in nutrient_values.items() if goal > 0) / 4
        score = round(score)
        label, color = ("Good", "green") if score >= 75 else ("Fair", "orange") if score >= 50 else ("Needs Improvement", "red")
        st.metric("Daily Nutrition Score", f"{score}/100", label, delta_color="off")
        st.markdown(f"<small style='color: {color};'>Your nutrition balance: {label}</small>", unsafe_allow_html=True)
    
    with col_predict:
        st.markdown("<u>Tomorrow's Predicted Calorie Intake:</u>", unsafe_allow_html=True)
        if len(hist_df) >= 3:
            try:
                hist_df['Calories'] = pd.to_numeric(hist_df['Calories'], errors='coerce').fillna(0)
                hist_df['DayOfWeek'] = pd.to_datetime(hist_df['Date']).dt.dayofweek
                hist_df['Rolling_Mean'] = hist_df['Calories'].rolling(window=3, min_periods=1).mean()
                hist_df['Rolling_Std'] = hist_df['Calories'].rolling(window=3, min_periods=1).std().fillna(0)
                
                tomorrow = datetime.now() + timedelta(days=1)
                tomorrow_day = tomorrow.weekday()
                
                if hist_df['Calories'].std() < 10:
                    forecast = hist_df['Calories'].mean() * random.uniform(0.95, 1.05)
                else:
                    try:
                        model = ARIMA(hist_df['Calories'], order=(1, 0, 1))
                        forecast = model.fit().forecast(steps=1)[0]
                    except:
                        model = ARIMA(hist_df['Calories'], order=(1, 0, 0))
                        forecast = model.fit().forecast(steps=1)[0]
                    if forecast < 500 or forecast > 5000:
                        forecast = hist_df['Calories'].mean()
                    if len(hist_df) >= 5:
                        same_day_data = hist_df[pd.to_datetime(hist_df['Date']).dt.dayofweek == tomorrow_day]
                        if not same_day_data.empty:
                            forecast = 0.7 * forecast + 0.3 * same_day_data['Calories'].mean()
                
                st.write(f"**{forecast:.0f} calories** (prediction for {tomorrow.strftime('%A')})")
                std_dev = hist_df['Calories'].std() if len(hist_df) > 1 else hist_df['Calories'].mean() * 0.1
                st.write(f"Range: {max(0, forecast - 1.5 * std_dev):.0f} - {forecast + 1.5 * std_dev:.0f} calories")
                last_value = hist_df['Calories'].iloc[-1]
                trend = "📈 Trending up" if forecast > last_value * 1.1 else "📉 Trending down" if forecast < last_value * 0.9 else "➡️ Stable"
                st.markdown(f"{trend} compared to today")
            except Exception:
                forecast = hist_df['Calories'].mean() * random.uniform(0.9, 1.1)
                st.write(f"{forecast:.0f} calories (simplified estimate)")
        else:
            st.write("Not enough data for prediction (minimum 3 days required)")
            if 'adjusted_goals' in st.session_state:
                st.write(f"Suggested target: {st.session_state.adjusted_goals.get('calories', 2000)} calories")
    
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    
    st.subheader("BMI-Based Recommendations")
    bmi_value = st.session_state.last_bmi
    if bmi_value < 18.5:
        st.info("💡 Increase calorie intake with nutrient-dense foods. Include more protein and healthy fats.")
    elif 18.5 <= bmi_value < 25:
        st.success("💡 Maintain balanced nutrition and regular physical activity.")
    elif 25 <= bmi_value < 30:
        st.warning("💡 Moderately reduce calorie intake and increase activity. Focus on whole foods.")
    else:
        st.warning("💡 Gradual weight loss through reduced calories and exercise. Prioritize nutrient-dense foods.")