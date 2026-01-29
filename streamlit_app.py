# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

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
cnx = st.connection("snowflake")
session = cnx.session()

# ----------------------------
# Fruit options (now includes SEARCH_ON)
# ----------------------------
fruit_df = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert Snowpark DataFrame to Pandas so we can look up SEARCH_ON for each fruit chosen
pd_df = fruit_df.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
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

            # Get the SEARCH_ON value for the chosen fruit
            search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]

            st.subheader(fruit_chosen + " Nutrition Information")

            # Call the API using SEARCH_ON (not the GUI label)
            try:
                smoothiefroot_response = requests.get(
                    "https://my.smoothiefroot.com/api/fruit/" + str(search_on),
                    timeout=10
                )

                if smoothiefroot_response.status_code == 200:
                    st.dataframe(
                        data=smoothiefroot_response.json(),
                        use_container_width=True
                    )
                else:
                    st.error(
                        f"API request failed for {fruit_chosen} (SEARCH_ON={search_on}). "
                        f"Status: {smoothiefroot_response.status_code}"
                    )
            except requests.RequestException as e:
                st.error(f"API request error for {fruit_chosen} (SEARCH_ON={search_on}): {e}")

        # Insert into Snowflake
        my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """

        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

        



