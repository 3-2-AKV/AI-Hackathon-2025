import sqlite3

# Create the database and tables if they don't exist
def create_db():
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()

    # Create ingredients table
    c.execute('''CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    expiration_date TEXT NOT NULL)''')

    # Create meal plans table (this can store generated meal plans)
    c.execute('''CREATE TABLE IF NOT EXISTS meal_plans (
                    id INTEGER PRIMARY KEY,
                    meal_type TEXT NOT NULL,
                    days INTEGER NOT NULL,
                    ingredients TEXT NOT NULL,
                    meal_plan TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS shopping_list (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL)''')

    conn.commit()
    conn.close()

# Insert a new ingredient into the database
def insert_ingredient(name, amount, unit, expiration_date):
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''INSERT INTO ingredients (name, amount, unit, expiration_date)
                 VALUES (?, ?, ?, ?)''',
              (name, amount, unit, expiration_date))
    conn.commit()
    conn.close()

# Insert an item to the shopping list database
def insert_grocery_item(name):
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''INSERT INTO shopping_list (name)
                VALUES (?)''',
                (name,))
    conn.commit()
    conn.close()

# Get all the items from the shopping list database
def get_grocery_list():
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM shopping_list''')
    groceries = c.fetchall()
    conn.close()
    return groceries

# Remove an item from shopping list database
def remove_grocery_from_db(name):
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('DELETE FROM shopping_list WHERE name = ?', (name,))
    conn.commit()
    conn.close()

# Get all ingredients from the fridge database
def get_ingredients():
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM ingredients''')
    ingredients = c.fetchall()
    conn.close()
    return ingredients

# Remove an item from fridge database
def remove_ingredient_from_db(name):
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('DELETE FROM ingredients WHERE name = ?', (name,))
    conn.commit()
    conn.close()

# Save a generated meal plan to the database
def insert_meal_plan(meal_plan, ingredients_list, meal_type, days):  # WILL be needed for the MAIN PY after we make a REQUEST and get and answer from AI
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''INSERT INTO meal_plans (meal_type, days, ingredients, meal_plan)
                 VALUES (?, ?, ?, ?)''',
              (meal_type, days, ', '.join(ingredients_list), meal_plan))
    conn.commit()
    conn.close()