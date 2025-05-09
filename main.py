import streamlit as st
import datetime
from database import create_db, insert_ingredient, insert_grocery_item, get_grocery_list, get_ingredients, remove_ingredient_from_db, remove_grocery_from_db
from meal_plans import generate_meal_plan
import re

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
        ingred_tab.subheader("Ingredients You Have")

        # Input field for the ingridient + add button

        product_name = st.text_input("Add the product:", placeholder = 'Milk')
        am_col, unit_col, expiry_col = st.columns([1, 1, 1])
        with am_col:
            product_amount = st.text_input("Amount", placeholder = '2')
        with unit_col:
            product_unit = st.selectbox("Unit", ['litres', 'kilograms', 'grams', 'items'])
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
                insert_ingredient(product_name, product_amount, product_unit, expiry_date)
            else:
                st.warning("Please add a product name.")

            
        st.write("##### Products:")
        for i, item in enumerate(st.session_state['items']):
            check_name_col, details_col, remove_col = st.columns([2, 3, 1])
            with check_name_col:
                checked = st.checkbox(f"{item['name']}", value = item['checked'], key = f'item{i}')
            with details_col:
                st.markdown('<p style="padding-top: 7px; color: grey;">' + f"{item['amount']} {item['unit']}, {item['expiry']}" + '</p>', unsafe_allow_html=True)
            with remove_col:
                if st.button("Remove", key=f"remove_ingredient{i}"):
                    remove_ingredient_from_db(item['name'])
                    st.session_state['items'].pop(i)
                    st.rerun()
            st.session_state['items'][i]['checked'] = checked

    with cart_tab:
        cart_tab.subheader("Your Shopping Cart")
        product_name_buy = st.text_input("Add the product you plan to buy:", placeholder = 'Carrots')

        if st.button("Add", key = "add_grocery"):
            if product_name_buy:
                st.session_state['groceries'].append({
                    'name': product_name_buy
                })
                insert_grocery_item(product_name_buy)
            else:
                st.warning("Please add a product name.")

        st.write("##### Shopping List:")
        for i, item in enumerate(st.session_state['groceries']):
            name_col_shop, add_to_fridge_col, remove_col_shop = st.columns([3, 1, 1])
            with name_col_shop:
                st.markdown(f"<div style='padding-top: 6px;'>{item['name']}</div>", unsafe_allow_html=True)
            with add_to_fridge_col:
                if st.button("Prepare", key=f"prepare_grocery{i}"):
                    st.session_state[f'show_inputs_{i}'] = True
            with remove_col_shop:
                if st.button("Remove", key=f"remove_grocery{i}"):
                    remove_grocery_from_db(item['name'])
                    st.session_state['groceries'].pop(i)
                    st.rerun()
                
            if st.session_state.get(f'show_inputs_{i}', False):
                amount_shop, unit_col, expiry_shop = st.columns([1, 1, 1])
                with amount_shop:
                    amount = st.text_input(f"Amount {item['name']}", key=f"amount_{i}", placeholder = "1")
                with unit_col:
                    unit = st.selectbox(f"Unit {item['name']}", ['litres', 'kilograms', 'grams', 'items'], key=f"unit_{i}")
                with expiry_shop:
                    expiry = st.date_input(f"Expiry date {item['name']}", key=f"expiry_{i}")
                if st.button("Confirm", key=f"confirm_grocery{i}"):
                    if amount:
                        insert_ingredient(item['name'], amount, unit, expiry)
                        # Updating the fridge list so that we don't have to reaload the table to see it 
                        db_ingredients = get_ingredients()
                        for ing in db_ingredients:
                            st.session_state['items'].append({
                                'name': ing[1],
                                'amount': str(ing[2]),
                                'unit': ing[3],
                                'expiry': ing[4],
                                'checked': False
                            })
                        remove_grocery_from_db(item['name'])
                        st.session_state['groceries'].pop(i)
                        st.rerun()
                    else:
                        st.warning("Please enter an amount before confirming.")

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
            meal_type = st.selectbox("Type of meal:", ["Any", "Breakfast", "Lunch", "Dinner", "Dessert"])
        personal_preferences = st.text_input("Specify any preferences (e.g. allergies, preferred preparation methods, temperature):")

        # important = sort_ingredients_by_expiration(st.session_state['items'])
        response = ''
        if st.button("Create the recipe", key = "create"):
            response = generate_meal_plan(st.session_state['items'], meal_type, num_recipes, checked_items, personal_preferences)
            # st.markdown(response)

with right_col: 
    st.subheader("Recipes Output")
    if response != '':
        # response = response["message"]["content"]
        # cleaned_content = re.sub(r"<think>.*?</think>\n?", "", response)
        st.markdown(response)
    else:
        st.write("Click “Create the recipe” to see your meal plan.")