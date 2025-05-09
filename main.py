import streamlit as st
import datetime
from ingredients import add_ingredient_to_db
from database import get_ingredients, create_db, insert_grocery_item, get_grocery_list, remove_ingredient_from_db
from groceries import insert_grocery_item_to_db
# import requests 

create_db()

st.set_page_config(layout="wide")
left_col, right_col = st.columns([1,1])

# Inilializing where we'll store items and if they are ticked to be in the recipe or not
if 'items' not in st.session_state:
    st.session_state['items'] = []
    db_ingredients = get_ingredients()
    for ing in db_ingredients:
        st.session_state['items'].append({
            'name': ing[1],
            'amount': str(ing[2]),
            'unit': ing[3],
            'expiry': ing[4],
            'checked': False
        })

if 'groceries' not in st.session_state:
    st.session_state['groceries'] = []
    db_groceries = get_grocery_list()
    for groc in db_groceries:
        st.session_state['groceries'].append({
            'name': groc[1],
            'checked': False
        })

with left_col: 
    ingred_tab, cart_tab, create_tab = st.tabs(["Ingredients", "Shopping Cart", "Create Recipe"])
    with ingred_tab:
        ingred_tab.subheader("Ingredients")

        # Input field for the ingridient + add button

        product_name = st.text_input("Add the product:", placeholder = 'Milk')
        am_col, unit_col, expiry_col = st.columns([1, 1, 1])
        with am_col:
            product_amount = st.text_input("Amount", placeholder = '2')
        with unit_col:
            product_unit = st.selectbox("Unit", ['litres', 'grams', 'items'])
        with expiry_col:
            expiry_date = st.date_input("Expiry date", value = datetime.date.today())
        if st.button("Add", key = "add_ingredient"):
            if product_name:
                st.session_state['items'].append({
                    'name': product_name, 
                    'amount': product_amount,
                    'unit': product_unit,
                    'expiry': expiry_date,
                    'checked': False
                })
                add_ingredient_to_db(product_name, product_amount, product_unit, expiry_date)
            else:
                st.warning("Please add a product name.")

            
        st.write("##### Products:")
        for i, item in enumerate(st.session_state['items']):
            check_name_col, details_col, remove_col = st.columns([1, 4.5, 1])
            with check_name_col:
                checked = st.checkbox(f"{item['name']}", value = item['checked'], key = f'item{i}')
            with details_col:
                st.markdown('<p style="padding-top: 7px; color: grey;">' + f"{item['amount']} {item['unit']}, {item['expiry']}" + '</p>', unsafe_allow_html=True)
            with remove_col:
                st.button("Remove", key=f"remove_ingredient{i}")
            st.session_state['items'][i]['checked'] = checked

    with cart_tab:
        cart_tab.subheader("Your Shopping Cart")
        product_name_buy = st.text_input("Add the product you plan to buy:", placeholder = 'Carrots')

        if st.button("Add", key = "add_grocery"):
            if product_name_buy:
                st.session_state['groceries'].append({
                    'name': product_name_buy, 
                    'checked': False
                })
                insert_grocery_item_to_db(product_name_buy)
            else:
                st.warning("Please add a product name.")

        st.write("##### Shopping List:")
        for i, item in enumerate(st.session_state['groceries']):
            checked = st.checkbox(f"{item['name']}", value = item['checked'], key = f'grocery{i}')
            st.session_state['groceries'][i]['checked'] = checked

    with create_tab:
        create_tab.subheader("Create Recipe")
        st.write("The ingredients you chose:")
        checked_items = []
        line = ''
        for i, item in enumerate(st.session_state['items']):
            if item['checked']:
                checked_items.append(item)
        for item in checked_items:
            line = ', '.join(f"{item['name']}" for item in checked_items)
        
        st.write(line)


        num_col, type_col, empty1 = st.columns([1, 1, 1])
        with num_col:
            num_recipes = st.text_input("Number of recipes to create:", placeholder = "1")
        with type_col:
            type_recipy = st.selectbox("Type of meal:", ["Any", "Breakfast", "Lunch", "Dinner", "Dessert"])

with right_col: 
    st.write("### Recipes Output")