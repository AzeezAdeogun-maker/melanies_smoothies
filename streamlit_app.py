# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# ----------------------------
# App UI
# ----------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# ----------------------------
# Inputs
# ----------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# ----------------------------
# Snowflake session
# ----------------------------
session = get_active_session()

# ----------------------------
# Fruit options
# ----------------------------
fruit_df = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df
    ,max_selections=5
)

# ----------------------------
# Submit order
# ----------------------------
time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not name_on_order:
        st.error("Please enter a name on the smoothie.")
    elif not ingredients_list:
        st.error("Please choose at least 1 ingredient.")
    else:
        # Build ingredients string
        ingredients_string = ""
        for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + " "

        # Insert into Snowflake
        my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """

        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")



