import streamlit as st
import datetime
from database import create_db, insert_ingredient, insert_grocery_item, get_grocery_list, get_ingredients, remove_ingredient_from_db, remove_grocery_from_db
from meal_plans import generate_meal_plan
import re
from datetime import datetime
from datetime import date
import json

# Taking the current date - needed to check the expired items
today_str = str(date.today())
curr_date = datetime.strptime(today_str, "%Y-%m-%d")

create_db()  # Creat *three* databases from database.py: ingredients, meal_plans (for recipes), shopping_list (cart)

# Diving the page in two sides
st.set_page_config(layout="wide")
left_col, right_col = st.columns([1,1])

# Inilializing where we'll store items and if they are ticked to be in the recipe or not
if 'items' not in st.session_state:
    st.session_state['items'] = []  # 'items' - name for what's in the FRIDGE (what you own)
    db_ingredients = get_ingredients()  # Getting from database - to have everything stored after reloading the page
    for ing in db_ingredients:
        st.session_state['items'].append({
            'name': ing[1],
            'amount': str(ing[2]),
            'unit': ing[3],
            'expiry': ing[4],
            'checked': False
        })

# Same for items in the SHOPPING LIST
if 'groceries' not in st.session_state:
    st.session_state['groceries'] = []  # 'groceries' - name for items in the shopping list
    db_groceries = get_grocery_list()
    for groc in db_groceries:
        st.session_state['groceries'].append({
            'name': groc[1]
        })

with left_col: 
    ingred_tab, cart_tab, create_tab = st.tabs(["Ingredients", "Shopping Cart", "Create Recipe"])  # 3 separate tabs
    with ingred_tab:
        ingred_tab.subheader("Ingredients You Have")

        # Input field for the ingridient + Add button
        product_name = st.text_input("Add the product:", placeholder = 'Milk')
        am_col, unit_col, expiry_col = st.columns([1, 1, 1])
        with am_col:
            product_amount = st.text_input("Amount", placeholder = '2')
        with unit_col:
            product_unit = st.selectbox("Unit", ['litres', 'kilograms', 'grams', 'items'])
        with expiry_col:
            expiry_date = st.date_input("Expiry date", value = curr_date)

        add_col, show_exp_col = st.columns([3.5, 1])
        with add_col:
            if st.button("Add", key = "add_ingredient"):  # Adding the item with all the entered parameters
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
                    st.warning("Please add a product name.")  # Must enter a product name
        with show_exp_col:
            if st.button("Show Expired", key = "show_expired"):
                expired_state = st.session_state.get('expired_list', False)
                st.session_state['expired_list'] = not expired_state  # Toggling
        
        # Creating an array of the expired items only, KEEPING THEIR INDEX (idx) FROM THE ORIGINAL FRIDGE LIST - to delete correctly
        expired_items = [(idx, item) for idx, item in enumerate(st.session_state['items'])
        if (datetime.strptime(str(item['expiry']), "%Y-%m-%d") - curr_date).days < 0]

        if st.session_state.get('expired_list', False):
            if expired_items:  # Checking if there are any expired items at all
                st.write("##### Expired products:")
                for idx, item in expired_items:
                    check_name_col, details_col, remove_col = st.columns([2, 3, 1])
                    with check_name_col:
                        st.checkbox(f"{item['name']}", value=item['checked'], key=f'item{idx}')
                    with details_col:
                        st.markdown(
                            f"<span style='color: grey; position: relative; top: 7px;'>{item['amount']} {item['unit']}, </span>"
                            f"<span style='color: orange; position: relative; top: 7px;'>{item['expiry']}</span>",
                            unsafe_allow_html=True
                        )
                    with remove_col:
                        if st.button("Remove", key=f"remove_ingredient{idx}"):
                            remove_ingredient_from_db(item['name'])
                            st.session_state['items'].pop(idx)
                            st.rerun()
            else:
                st.write("You don't have any expired groceries!")
        else:
            # Displaying the list of products in the fridge
            st.write("##### Products:")
            for i, item in enumerate(st.session_state['items']):
                check_name_col, details_col, remove_col = st.columns([2, 3, 1])  # All in line
                with check_name_col:
                    st.checkbox(f"{item['name']}", value = item['checked'], key = f'item{i}')
                with details_col:
                    st.markdown('<p style="padding-top: 7px; color: grey;">' + f"{item['amount']} {item['unit']}, {item['expiry']}" + '</p>', unsafe_allow_html=True)
                with remove_col:
                    if st.button("Remove", key=f"remove_ingredient{i}"):
                        remove_ingredient_from_db(item['name'])  # Removing from database
                        st.session_state['items'].pop(i)  # Removing from the list in the UI
                        # st.rerun()  # Instantly updating the list without having to refresh the page


    with cart_tab:
        cart_tab.subheader("Your Shopping Cart")
        product_name_buy = st.text_input("Add the product you plan to buy:", placeholder = 'Carrots')

        if st.button("Add", key = "add_grocery"):
            if product_name_buy:
                st.session_state['groceries'].append({  # Adding to the list in the UI
                    'name': product_name_buy
                })
                insert_grocery_item(product_name_buy)  # Adding to the groceries database
            else:
                st.warning("Please add a product name.")

        st.write("##### Shopping List:")
        for i, item in enumerate(st.session_state['groceries']):
            name_col_shop, add_to_fridge_col, remove_col_shop = st.columns([4, 1, 1])
            with name_col_shop:
                st.markdown(f"<div style='padding-top: 6px;'>{item['name']}</div>", unsafe_allow_html=True)
            with add_to_fridge_col:
                if st.button("Prepare", key=f"prepare_grocery{i}"):  # Button to enter details of the product you bought
                    # Tracking the current state of the button so that we can toggle it on and off
                    current_state = st.session_state.get(f'show_inputs_{i}', False)
                    st.session_state[f'show_inputs_{i}'] = not current_state  # Toggling
            with remove_col_shop:
                if st.button("Remove", key=f"remove_grocery{i}"):  # In case you decided not to buy the item - remove from shopping list
                    remove_grocery_from_db(item['name'])  # Remove from db
                    st.session_state['groceries'].pop(i)  # Remove from list in the UI
                    st.rerun()
                
            if st.session_state.get(f'show_inputs_{i}', False):  # Showing the details drop-down if "Prepare" button was clicked
                amount_shop, unit_col, expiry_shop = st.columns([1, 1, 1])
                with amount_shop:
                    amount = st.text_input(f"Amount {item['name']}", key=f"amount_{i}", placeholder = "1")
                with unit_col:
                    unit = st.selectbox(f"Unit {item['name']}", ['litres', 'kilograms', 'grams', 'items'], key=f"unit_{i}")
                with expiry_shop:
                    expiry = st.date_input(f"Expiry date {item['name']}", key=f"expiry_{i}")
                if st.button("Confirm", key=f"confirm_grocery{i}"):  # Adding from list to the fridge
                    if amount:
                        insert_ingredient(item['name'], amount, unit, expiry)  # Adding item to FRIDGE database
                        # Updating the fridge list so that we don't have to reaload the table to see it 
                        db_ingredients = get_ingredients()
                        st.session_state['items'] = []  # Clearing the prev list firstly to avoiding doubling the items
                        for ing in db_ingredients:
                            st.session_state['items'].append({
                                'name': ing[1],
                                'amount': str(ing[2]),
                                'unit': ing[3],
                                'expiry': ing[4],
                                'checked': False
                            })
                        remove_grocery_from_db(item['name'])  # Removing item fromshopping list DATABASE
                        st.session_state.pop(f'show_inputs_{i}', None)  # Removing the state of the "Prepare" button - ensure the "Prepare" tab of the next item won't open after we delete the current one
                        st.session_state['groceries'].pop(i)  # Removing item from the shopping list
                        st.rerun()
                    else:
                        st.warning("Please enter an amount before confirming.")

    with create_tab:
        create_tab.subheader("Create Recipe")
        st.write("The ingredients you chose:")
        checked_items = []
        line = ''
        for i, item in enumerate(st.session_state['items']):  # Checking which items are checked, creating a separate array for them to later pass into the prompt
            if st.session_state.get(f'item{i}', False):
                checked_items.append(item)
        if len(checked_items) == 0:
            st.write("You haven't chosen any ingredients yet.")
        for item in checked_items:
            line = ', '.join(f"{item['name']}" for item in checked_items)  # Line to display
        st.write(line)

        num_col, type_col, empty1 = st.columns([1, 1, 1])
        with num_col:
            num_recipes = st.text_input("Number of recipes to create:", placeholder = "1")  # Passed to the prompt
        with type_col:
            meal_type = st.selectbox("Type of meal:", ["Any", "Breakfast", "Lunch", "Dinner", "Dessert"])  # Passed to the prompt
        personal_preferences = st.text_input("Specify any preferences (e.g. allergies, preferred preparation methods, temperature):")  # Passed to the prompt

        # important = sort_ingredients_by_expiration(st.session_state['items'])
        response = ''
        if st.button("Create the recipe", key = "create"):  # Receiving the answer from AI
            response = generate_meal_plan(st.session_state['items'], meal_type, num_recipes, checked_items, personal_preferences)
            
            # st.markdown(response)


with right_col: 
    st.subheader("Recipes Output")
    if response:
        # response = response["message"]["content"]
        # cleaned_content = re.sub(r"<think>.*?</think>\n?", "", response)
        # st.markdown(response)
        cleaned = response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned)
        cleaned = cleaned.replace("END", "").strip()

        # 2) Grab just the JSON array
        m = re.search(r"(\[.*\])", cleaned, flags=re.DOTALL)
        if not m:
            st.error("⚠️ Couldn't find a JSON array in the AI output:")
            st.code(response)
        else:
            payload = m.group(1)
            # 3) Safe JSON parsing
            try:
                recipes = json.loads(payload)
            except json.JSONDecodeError:
                st.error("⚠️ AI returned invalid JSON; here’s the raw output:")
                st.code(response)
            else:
                # 4) Render each recipe
                for r in recipes:
                    st.header(r["name"])
                    st.subheader("Ingredients")
                    for ing in r["ingredients"]:
                        st.write(f"- {ing}")
                    st.subheader("Instructions")
                    for i, step in enumerate(r["instructions"], 1):
                        st.write(f"{i}. {step}")
    else:
        st.write("Click “Create the recipe” to see your meal plan.")

        