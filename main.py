import streamlit as st
import datetime
from database import create_db, insert_ingredient, insert_grocery_item, get_grocery_list, get_ingredients, remove_ingredient_from_db, remove_grocery_from_db, save_recipes_to_db, get_recipes_from_db, remove_recipe_from_db
from recipe_gen import generate_meal_plan
import re
from datetime import datetime
from datetime import date
import json
import urllib.parse

# Taking the current date - needed to check the expired items
today_str = str(date.today())
curr_date = datetime.strptime(today_str, "%Y-%m-%d")

create_db()  # Create *three* databases from database.py: ingredients, meal_plans (for recipes), shopping_list (cart)

# Diving the page in two sides
st.set_page_config(layout="wide")

st.title("Chefmate")
st.caption("*Your kitchen mate, always ready.*")

left_col, right_col = st.columns([1,1])

# Inilializing where we'll store items and if they are ticked to be in the recipe or not
if 'items' not in st.session_state:
    st.session_state['items'] = []  # 'items' - name for what's in the FRIDGE (what you own)
    db_ingredients = get_ingredients()  # Getting from database - to have everything stored after reloading the page
    for ing in db_ingredients:
        st.session_state['items'].append({
            'id': ing[0],
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
            'id': groc[0],
            'name': groc[1]
        })

if "reset_fields" in st.session_state and st.session_state.reset_fields:
    st.session_state["input_name"] = ""
    st.session_state["input_amount"] = ""
    st.session_state["input_expiry"] = date.today()
    st.session_state["input_unit"] = 'litres'
    st.session_state["input_name_cart"] = ""
    st.session_state["reset_fields"] = False  # Reset the flag

with left_col: 
    ingred_tab, cart_tab, create_tab, cookbook_tab = st.tabs(["Ingredients", "Shopping Cart", "Create Recipe", "Cookbook"])  # 4 separate tabs
    with ingred_tab:
        ingred_tab.subheader("Ingredients You Have")

        # Input field for the ingridient + Add button
        product_name = st.text_input("Add the product:", placeholder = 'Milk', key = "input_name").capitalize()
        am_col, unit_col, expiry_col = st.columns([1, 1, 1])
        with am_col:
            product_amount = st.text_input("Amount", placeholder = '2', key = "input_amount")
        with unit_col:
            product_unit = st.selectbox("Unit", ['litres', 'kilograms', 'grams', 'units'], key = "input_unit")
        with expiry_col:
            expiry_date = st.date_input("Expiry date", key = "input_expiry")

        add_col, show_exp_col = st.columns([3.5, 1.27])
        with add_col:
            if st.button("Add", key = "add_ingredient"):  # Adding the item with all the entered parameters
                if product_name:
                    new_id_ing = insert_ingredient(product_name, product_amount, product_unit, expiry_date)
                    st.session_state['items'].append({
                        'id': new_id_ing,
                        'name': product_name, 
                        'amount': product_amount,
                        'unit': product_unit,
                        'expiry': expiry_date,
                        'checked': False
                    })
                    st.session_state["reset_fields"] = True
                    st.rerun()
                else:
                    st.warning("Please add a product name.")  # Must enter a product name
        with show_exp_col:
            if st.button("Show/Hide Expired", key = "show_expired"):
                expired_state = st.session_state.get('expired_list', False)
                button_label = "Hide Expired" if expired_state else "Show Expired"
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
                            f"<span style='color: #e95952; position: relative; top: 7px;'>{item['expiry']}</span>",
                            unsafe_allow_html=True
                        )
                    with remove_col:
                        if st.button("Remove", key=f"remove_ingredient{idx}"):
                            curr_state = st.session_state.get(f"confirm_delete_exp{idx}", False)
                            st.session_state[f"confirm_delete_exp{idx}"] = not curr_state
                    
                    if st.session_state.get(f"confirm_delete_exp{idx}", False):
                        st.warning(f"Are you sure you want to delete this expired ingredient?")
                        confirm_col, cancel_col = st.columns([1, 1])
                        with confirm_col:
                            if st.button("Yes, delete", key=f"confirm_{idx}"):
                                target_id = item['id']
                                remove_ingredient_from_db(target_id)
                                st.session_state.pop(f"confirm_delete_exp{idx}", None)
                                st.session_state['items'] = [
                                    item for item in st.session_state['items']
                                    if item['id'] != target_id
                                ]
                                st.rerun()
                        with cancel_col:
                            if st.button("Cancel", key=f"cancel_{idx}"):
                                del st.session_state[f"confirm_delete_exp{idx}"]
                                st.rerun()
            else:
                st.write("##### Expired products:")
                st.write("You don't have any expired groceries!")
        else:
            # Displaying the list of products in the fridge
            st.write("##### Products:")
            for i, item in enumerate(st.session_state['items']):
                check_name_col, details_col, remove_col = st.columns([2, 3, 1])  # All in line
                with check_name_col:
                    st.checkbox(f"{item['name']}", value = item['checked'], key = f'item{i}')
                with details_col:
                    if 0 < (datetime.strptime(str(item['expiry']), "%Y-%m-%d") - curr_date).days <= 3:
                        st.markdown(
                            f"<span style='color: grey; position: relative; top: 7px;'>{item['amount']} {item['unit']}, </span>"
                            f"<span style='color: #dea452; position: relative; top: 7px;'>{item['expiry']}</span>",
                            unsafe_allow_html=True
                        )
                    elif (datetime.strptime(str(item['expiry']), "%Y-%m-%d") - curr_date).days <= 0:
                        st.markdown(
                            f"<span style='color: grey; position: relative; top: 7px;'>{item['amount']} {item['unit']}, </span>"
                            f"<span style='color: #e95952; position: relative; top: 7px;'>{item['expiry']}</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown('<p style="padding-top: 7px; color: grey;">' + f"{item['amount']} {item['unit']}, {item['expiry']}" + '</p>', unsafe_allow_html=True)
                with remove_col:
                    if st.button("Remove", key=f"remove_ingredient{i}"):
                        curr_state = st.session_state.get(f"confirm_delete_ing{i}", False)
                        st.session_state[f"confirm_delete_ing{i}"] = not curr_state
                
                if st.session_state.get(f"confirm_delete_ing{i}", False):
                    st.warning(f"Are you sure you want to delete this ingredient?")
                    confirm_col, cancel_col = st.columns([1, 1])
                    with confirm_col:
                        if st.button("Yes, delete", key=f"confirm_{i}"):
                            target_id = item['id']
                            remove_ingredient_from_db(target_id)
                            st.session_state.pop(f"confirm_delete_ing{i}", None)
                            st.session_state['items'] = [
                                item for item in st.session_state['items']
                                if item['id'] != target_id
                            ]
                            st.rerun()  # Instantly updating the list without having to refresh the page
                    with cancel_col:
                        if st.button("Cancel", key=f"cancel_{i}"):
                            del st.session_state[f"confirm_delete_ing{i}"]
                            st.rerun()


    with cart_tab:
        cart_tab.subheader("Your Shopping Cart")
        product_name_buy = st.text_input("Add the product you plan to buy:", placeholder = 'Carrots', key = "input_name_cart")

        if st.button("Add", key = "add_grocery"):
            if product_name_buy:
                new_id = insert_grocery_item(product_name_buy)
                st.session_state['groceries'].append({  # Adding to the list in the UI
                    'id': new_id,
                    'name': product_name_buy
                })
                # insert_grocery_item(product_name_buy)  # Adding to the groceries database
                st.session_state["reset_fields"] = True
                st.rerun()
            else:
                st.warning("Please add a product name.")

        st.write("##### Shopping List:")
        for i, item in enumerate(st.session_state['groceries']):
            name_col_shop, add_to_fridge_col, remove_col_shop = st.columns([4, 2, 1.5])
            with name_col_shop:
                st.markdown(f"<div style='padding-top: 6px;'>{item['name']}</div>", unsafe_allow_html=True)
            with add_to_fridge_col:
                if st.button("Add to Ingredients", key=f"prepare_grocery{i}"):  # Button to enter details of the product you bought
                    # Tracking the current state of the button so that we can toggle it on and off
                    current_state = st.session_state.get(f'show_inputs_{i}', False)
                    st.session_state[f'show_inputs_{i}'] = not current_state  # Toggling
            with remove_col_shop:
                if st.button("Remove", key=f"remove_grocery{i}"):  # In case you decided not to buy the item - remove from shopping list
                    curr_state = st.session_state.get(f"confirm_delete_groc{i}", False)
                    st.session_state[f"confirm_delete_groc{i}"] = not curr_state
                
            if st.session_state.get(f"confirm_delete_groc{i}", False):
                st.warning(f"Are you sure you want to delete this ingredient?")
                confirm_col, cancel_col = st.columns([1, 1])
                with confirm_col:
                    if st.button("Yes, delete", key=f"confirm_{i}"):
                        target_id_shop = item['id']
                        remove_grocery_from_db(target_id_shop)
                        st.session_state.pop(f"confirm_delete_groc{i}", None)
                        fresh = get_grocery_list()
                        st.session_state['groceries'] = [
                            {'id': groc[0], 'name': groc[1]}
                            for groc in fresh
                        ]
                        st.rerun()
                with cancel_col:
                    if st.button("Cancel", key=f"cancel_{i}"):
                        del st.session_state[f"confirm_delete_groc{i}"]
                        st.rerun()

            if st.session_state.get(f'show_inputs_{i}', False):  # Showing the details drop-down if "Prepare" button was clicked
                amount_shop, unit_col, expiry_shop = st.columns([1, 1, 1])
                with amount_shop:
                    amount = st.text_input(f"Amount", key=f"amount_{i}", placeholder = "1")
                with unit_col:
                    unit = st.selectbox(f"Unit", ['litres', 'kilograms', 'grams', 'units'], key=f"unit_{i}")
                with expiry_shop:
                    expiry = st.date_input(f"Expiry date", key=f"expiry_{i}")
                if st.button("Confirm", key=f"confirm_grocery{i}"):  # Adding from list to the fridge
                    if amount:
                        insert_ingredient(item['name'], amount, unit, expiry)  # Adding item to FRIDGE database
                        # Updating the fridge list so that we don't have to reaload the table to see it 
                        db_ingredients = get_ingredients()
                        st.session_state['items'] = []  # Clearing the prev list firstly to avoiding doubling the items
                        for ing in db_ingredients:
                            st.session_state['items'].append({
                                'id': len(st.session_state['items']),
                                'name': ing[1],
                                'amount': str(ing[2]),
                                'unit': ing[3],
                                'expiry': ing[4],
                                'checked': False
                            })
                        remove_grocery_from_db(item['id'])  # Removing item fromshopping list DATABASE
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
            num_recipes = st.text_input("Number of recipes to create:", placeholder = "3")  # Passed to the prompt
        with type_col:
            meal_type = st.selectbox("Meal type:", ["Any", "Breakfast", "Lunch", "Dinner", "Dessert"])  # Passed to the prompt
        personal_preferences = st.text_input("Specify any preferences (e.g. allergies, preferred preparation methods, temperature):")  # Passed to the prompt

        response = ''
        if st.button("Create the recipe", key = "create"):  # Receiving the answer from AI
            if not num_recipes.strip().isdigit():
                st.warning("Please enter a whole number for the number of recipes.")
            elif 2 < int(num_recipes) < 11 and len(checked_items) != 0:
                st.session_state["select_recipe_index"] = None
                response = generate_meal_plan(st.session_state['items'], st.session_state['groceries'], meal_type, num_recipes, checked_items, personal_preferences)
                st.session_state['response'] = response
            elif (num_recipes != None or 2 > int(num_recipes) < 11) and len(checked_items) != 0:
                st.warning("Please choose a number of recipes between 3 and 10.")
            elif len(checked_items) == 0:
                st.warning("Please select at least 1 ingredient.")

    with cookbook_tab:
        st.write("#### Your Saved Recipies")
        all_recipes = get_recipes_from_db()
        all_recipes = sorted(all_recipes, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse = True)

        st.write("##### Search through your cookbook")
        key_words = st.text_input("Key words or name of the recipe:", placeholder = "Chicken Salad")
        search_type_col, empty = st.columns([2, 5])
        with search_type_col:
            search_type = st.selectbox("Meal type:", ["Any", "Breakfast", "Lunch", "Dinner", "Dessert"], key = "search_recipe_type")

        search_btn_col, showall_btn_col = st.columns([3, 1])
        with search_btn_col:
            if st.button("Search", key = "search_recipes_inputted"):
                st.session_state["show_search_recipes"] = True
                st.session_state["show_all_recipes"] = False
                st.session_state["active_recipe_list"] = "search"
        with showall_btn_col:
            if st.button("Show All Recipes", key = "show_all_recipes_res"):
                st.session_state["show_search_recipes"] = False
                st.session_state["show_all_recipes"] = True
                st.session_state["active_recipe_list"] = "all"
        st.divider()
        st.write("#### Recipes")

        if st.session_state.get("show_all_recipes", False):
            if all_recipes:
                countRecipes = 0
                st.session_state["displayed_recipes"] = all_recipes
                for i in all_recipes:
                    name_col, show_col = st.columns([3, 1.27])
                    current_selected_show_recipe = st.session_state.get("selected_recipe_index", None)  # For showing recipes button
                    with name_col:
                        st.write(f"##### {i[1]}")
                    with show_col:
                        if st.button("Show/Hide Recipe", key = f"show_{countRecipes}"):
                            if current_selected_show_recipe == countRecipes:
                                st.session_state["selected_recipe_index"] = None
                            else:
                                st.session_state["selected_recipe_index"] = countRecipes
                                st.session_state.pop("response", None)

                    type_col, date_col, remove_col = st.columns([1.5, 6, 2.75])
                    with type_col:
                        st.caption(i[0].capitalize())
                    with date_col:
                        st.caption(i[4])
                    with remove_col:
                        if st.button("Remove Recipe", key = f"remove_rec_{countRecipes}"):
                            curr_state = st.session_state.get(f"confirm_delete_recipe{countRecipes}", False)
                            st.session_state[f"confirm_delete_recipe{countRecipes}"] = not curr_state
                    
                    if st.session_state.get(f"confirm_delete_recipe{countRecipes}", False):
                        st.warning(f"Are you sure you want to delete this recipe from your cookbook?")
                        confirm_col, cancel_col = st.columns([1, 1])
                        with confirm_col:
                            if st.button("Yes, delete", key=f"confirm_{countRecipes}"):
                                remove_recipe_from_db(i["id"])
                                del st.session_state[f"confirm_delete_recipe{countRecipes}"]
                                st.rerun()
                        with cancel_col:
                            if st.button("Cancel", key=f"cancel_{countRecipes}"):
                                del st.session_state[f"confirm_delete_recipe{countRecipes}"]
                                st.rerun()

                    split_ingredients = re.findall(r'.+?\([^)]*\)(?: \(using soonest\))?', i[2])
                    formatted = "<br>".join(split_ingredients)
                    st.markdown(formatted, unsafe_allow_html=True)
                    st.divider()
                    countRecipes += 1
            else:
                st.write("No recipes in your cookbook yet.")
        elif st.session_state.get("show_search_recipes", False):
            list_of_found = []
            if search_type == "Any":
                for i in all_recipes:
                        if key_words.lower() in i[1].lower() or key_words.lower() in i[2].lower():
                            list_of_found.append(i)
            else:
                list_of_type = []
                for i in all_recipes:
                    if search_type.lower() == i[0] and (key_words.lower() in i[1].lower() or key_words.lower() in i[2].lower()):
                            list_of_found.append(i)
            if list_of_found:
                st.session_state["displayed_recipes"] = list_of_found
                countRecipes = 0
                for i in list_of_found:
                    name_col, show_col = st.columns([3, 1])
                    current_selected_show_recipe = st.session_state.get("selected_recipe_index", None)  # For showing recipes button
                    with name_col:
                        st.write(f"##### {i[1]}")
                    with show_col:
                        if st.button("Show/Hide Recipe", key = f"show_{countRecipes}"):
                            if current_selected_show_recipe == countRecipes:
                                # If already selected, unselect (toggle off)
                                st.session_state["selected_recipe_index"] = None
                            else:
                                # Select a different one (toggle on)
                                st.session_state["selected_recipe_index"] = countRecipes

                    type_col, date_col, remove_col = st.columns([1, 6, 2])
                    with type_col:
                        st.caption(i[0].capitalize())
                    with date_col:
                        st.caption(i[4])
                    with remove_col:
                        if st.button("Remove Recipe", key = f"remove_rec_{countRecipes}"):
                            curr_state = st.session_state.get(f"confirm_delete_recipe{countRecipes}", False)
                            st.session_state[f"confirm_delete_recipe{countRecipes}"] = not curr_state
                    
                    if st.session_state.get(f"confirm_delete_recipe{countRecipes}", False):
                        st.warning(f"Are you sure you want to delete this recipe from your cookbook?")
                        confirm_col, cancel_col = st.columns([1, 1])
                        with confirm_col:
                            if st.button("Yes, delete", key=f"confirm_{countRecipes}"):
                                remove_recipe_from_db(i["id"])
                                del st.session_state[f"confirm_delete_recipe{countRecipes}"]
                                st.rerun()
                        with cancel_col:
                            if st.button("Cancel", key=f"cancel_{countRecipes}"):
                                del st.session_state[f"confirm_delete_recipe{countRecipes}"]
                                st.rerun()

                    split_ingredients = re.findall(r'.+?\([^)]*\)(?: \(using soonest\))?', i[2])
                    formatted = "<br>".join(split_ingredients)
                    st.markdown(formatted, unsafe_allow_html=True)
                    st.divider()
                    countRecipes += 1
            else:
                st.write("Looks like there are no recipes with such parameters...")
        else:
            st.write('Click "Show All Recipes" or enter your search parameters to display your cookbook.')

with right_col: 
    st.subheader("Recipes Output")

    # selected_index = st.session_state.get("selected_recipe_index")
    selected_index = st.session_state.get("selected_recipe_index")  
    displayed_recipes = st.session_state.get("displayed_recipes", [])

    if 'response' in st.session_state and st.session_state['response'] != "":
        cleaned = st.session_state['response'].strip()
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned)
        cleaned = cleaned.replace("END", "").strip()

        m = re.search(r"(\[.*\])", cleaned, flags=re.DOTALL)
        if not m:
            st.error("⚠️ Couldn't find a JSON array in the AI output:")
            st.code(st.session_state['response'])
        else:
            payload = m.group(1)
            try:
                recipes = json.loads(payload)
            except json.JSONDecodeError:
                st.error("⚠️ AI returned invalid JSON; here’s the raw output:")
                st.code(st.session_state['response'])
            else:
                counter = -1
                for r in recipes:
                    counter += 1
                    name = r["name"]
                    query = urllib.parse.quote(name)
                    search_url = f"https://www.google.com/search?q={query}+recipe"
                    st.markdown(
                        f'''
                        <h1 style="font-weight:bold;">
                        <a href="{search_url}" target="_blank"
                            style="color: inherit;">{name}</a>
                        </h1>
                        ''',
                        unsafe_allow_html=True
                    )
                    st.caption(f"*{r['type'].capitalize()}*")
                    st.subheader("Ingredients")
                    for ing in r["ingredients"]:
                        st.write(f"- {ing}")
                    st.subheader("Instructions")
                    for i, step in enumerate(r["instructions"], 1):
                        st.write(f"{i}. {step}")
                    if st.button("Add the recipe", key = f"add_recipy_{counter}"):
                        save_recipes_to_db(json.dumps(r))
                        st.success(f"✅ \"{r['name']}\" added to database!")
    elif selected_index is not None and 0 <= selected_index < len(displayed_recipes):
        st.session_state["response"] = ""
        # if list_of_found:
        #     selected = list_of_found[selected_index]
        # else:
        selected = displayed_recipes[selected_index]
        st.subheader(f"{selected[1]}")
        st.caption(f"*{selected[0].capitalize()}*")

        st.markdown("**Ingredients**")
        split_ingredients = re.findall(r'.+?\([^)]*\)(?: \(using soonest\))?', selected[2])
        formatted = "<br>".join(split_ingredients)
        st.markdown(formatted, unsafe_allow_html=True)

        st.markdown("**Instructions**")
        st.markdown(selected[3])
    else:
        st.write("Click “Create the recipe” to see your meal plan or show any recipe from your cookbook.")

        