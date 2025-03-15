import streamlit as st
import random
import time
from components.home import home_page
from components.daily_log import daily_food_log
from components.analysis import nutrition_analysis
from components.history import food_history
from components.settings import settings

def main():
    st.sidebar.title("🍽️ Nutrition Tracker")
    
    # Initialize session state for tip and page navigation
    if 'show_tip' not in st.session_state:
        st.session_state.show_tip = False
        st.session_state.tip_text = ""
        st.session_state.tip_time = 0
    if 'page' not in st.session_state:
        st.session_state.page = "Home"

    # Define pages
    pages = {
        "Home": home_page,
        "Daily Food Log": daily_food_log,
        "Nutrition Analysis": nutrition_analysis,
        "Food History": food_history,
        "Settings": settings
    }

    # Navigation callback
    def on_page_change():
        st.session_state.page = st.session_state.page_selection

    # Sidebar navigation
    current_index = list(pages.keys()).index(st.session_state.page)
    st.sidebar.radio(
        "Navigate",
        list(pages.keys()),
        index=current_index,
        key="page_selection",
        on_change=on_page_change
    )

    # Daily Tip Button
    if st.sidebar.button("🌟 Daily Nutrition Tip"):
        nutrition_tips = [
            "Drink 8 glasses of water daily!",
            "Include protein in every meal.",
            "Eat more colorful vegetables.",
            "Balance your macronutrients.",
            "Avoid processed foods."
        ]
        st.session_state.show_tip = True
        st.session_state.tip_text = random.choice(nutrition_tips)
        st.session_state.tip_time = time.time()

    # Display tip with fade effect
    if st.session_state.show_tip:
        elapsed_time = time.time() - st.session_state.tip_time
        if elapsed_time < 6:
            opacity = min(1.0, elapsed_time / 0.3) if elapsed_time < 0.3 else max(0, 6 - elapsed_time) if elapsed_time >= 5 else 1.0
            tip_html = f"""
            <div style="padding: 10px; background-color: #e8f4f8; border-left: 4px solid #4e8cff; border-radius: 4px; margin: 10px 0; opacity: {opacity}; transition: opacity 0.2s ease;">
                <p style="margin: 0; color: #1f618d;"><strong>Tip:</strong> {st.session_state.tip_text}</p>
            </div>
            """
            st.sidebar.markdown(tip_html, unsafe_allow_html=True)
            time.sleep(0.1)
            st.rerun()
        else:
            st.session_state.show_tip = False

    # Render selected page
    pages[st.session_state.page]()

if __name__ == "__main__":
    main()