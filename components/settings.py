import streamlit as st
import time
from database import food_collection, safe_mongodb_operation

def settings():
    st.title("⚙️ Settings")
    
    st.subheader("Add New Food")
    with st.form("add_food_form"):
        product_name = st.text_input("Product Name")
        brand = st.text_input("Brand")
        nutrients = {
            "energy-kcal": st.number_input("Calories"),
            "proteins": st.number_input("Protein (g)"),
            "carbohydrates": st.number_input("Carbohydrates (g)"),
            "fat": st.number_input("Fat (g)")
        }
        submitted = st.form_submit_button("Add Food")
        if submitted:
            def add_food_operation():
                food_collection.insert_one({"product_name": product_name, "brands": brand, "nutriments": nutrients})
                st.success("Food added successfully!")
                time.sleep(1)
                st.rerun()
            safe_mongodb_operation(add_food_operation, "Failed to add food")
    
    st.subheader("Delete Food")
    if 'delete_confirmed' not in st.session_state:
        st.session_state.delete_confirmed = False
    if 'food_to_delete' not in st.session_state:
        st.session_state.food_to_delete = None
    if 'deletion_message' not in st.session_state:
        st.session_state.deletion_message = None
    if 'show_done_button' not in st.session_state:
        st.session_state.show_done_button = False
    
    foods = safe_mongodb_operation(
        lambda: list(food_collection.find({"product_name": {"$exists": True, "$ne": "", "$ne": "Unknown"}, "brands": {"$exists": True, "$ne": ""}}, {"product_name": 1, "brands": 1, "_id": 0})),
        "Failed to retrieve foods"
    ) or []
    
    food_options = [{"display": f"{food['product_name']} ({food['brands']})", "product": food['product_name'], "brand": food['brands']} for food in foods if food.get('product_name') and food.get('brands')]
    
    with st.container():
        if food_options:
            selected_food_index = st.selectbox("Select Food to Delete", range(len(food_options)), format_func=lambda i: food_options[i]["display"])
            selected_food = food_options[selected_food_index]
            
            if st.button("Delete Selected Food"):
                st.session_state.food_to_delete = selected_food
                st.session_state.delete_confirmed = False
                st.session_state.deletion_message = ("info", f"Please confirm you want to delete '{selected_food['display']}'")
                st.rerun()
            
            if st.session_state.deletion_message:
                message_type, message_text = st.session_state.deletion_message
                if message_type == "success":
                    st.success(message_text)
                    st.session_state.show_done_button = True
                elif message_type == "warning":
                    st.warning(message_text)
                    st.session_state.show_done_button = True
                elif message_type == "info":
                    st.info(message_text)
            
            if st.session_state.show_done_button and st.button("Done"):
                st.session_state.deletion_message = None
                st.session_state.show_done_button = False
                st.session_state.food_to_delete = None
                st.session_state.delete_confirmed = False
                st.rerun()
            
            if st.session_state.food_to_delete:
                confirm_delete = st.checkbox(f"Yes, I want to delete '{st.session_state.food_to_delete['display']}'", key="confirm_delete")
                if confirm_delete and not st.session_state.delete_confirmed:
                    st.session_state.delete_confirmed = True
                    def delete_food_operation():
                        food_to_delete = st.session_state.food_to_delete
                        result = food_collection.delete_one({"product_name": food_to_delete["product"], "brands": food_to_delete["brand"]})
                        st.session_state.deletion_message = ("success", f"{food_to_delete['display']} deleted!") if result.deleted_count > 0 else ("warning", "Food item not found or could not be deleted.")
                    safe_mongodb_operation(delete_food_operation, "Failed to delete food")
                    st.session_state.food_to_delete = None
                    st.session_state.delete_confirmed = False
                    st.rerun()
                if st.button("Cancel Deletion"):
                    st.session_state.food_to_delete = None
                    st.session_state.delete_confirmed = False
                    st.session_state.deletion_message = ("info", "Deletion cancelled.")
                    st.rerun()
        else:
            st.info("No foods with valid product names and brands available to delete.")