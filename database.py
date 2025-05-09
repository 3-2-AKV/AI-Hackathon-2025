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
    meal_name TEXT NOT NULL,
    meal_ingredients TEXT NOT NULL,
    meal_instructions TEXT NOT NULL
)''')

    c.execute('''CREATE TABLE IF NOT EXISTS shopping_list (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL)''')

    conn.commit()
    conn.close()

# Insert a new ingredient into the database
def insert_ingredient(name, amount, unit, expiration_date):  # Needed ONLY FOR INGREDIENTS.PY, we do NOT use it anywhere else
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''INSERT INTO ingredients (name, amount, unit, expiration_date)
                 VALUES (?, ?, ?, ?)''',
              (name, amount, unit, expiration_date))
    conn.commit()
    conn.close()

def insert_grocery_item(name):
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''INSERT INTO shopping_list (name)
                VALUES (?)''',
                (name,))
    conn.commit()
    conn.close()

def get_grocery_list():
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM shopping_list''')
    groceries = c.fetchall()
    conn.close()
    return groceries

# Retrieve all ingredients from the database
def get_ingredients():  # Needed ONLY FOR MAIN PY when getting the STORED items into the items LIST in main.py
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM ingredients''')
    ingredients = c.fetchall()
    conn.close()
    return ingredients

# Save a generated meal plan to the database
def insert_meal_plan(meal_type, meal_name, meal_ingredients, meal_instructions):  # WILL be needed for the MAIN PY after we make a REQUEST and get and answer from AI
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('''INSERT INTO meal_plans (meal_type, meal_ingredients, meal_name, meal_instructions)
                 VALUES (?, ?, ?, ?)''',
              (meal_type, ', '.join(meal_ingredients), meal_name, meal_instructions))
    conn.commit()
    conn.close()

def remove_ingredient_from_db(name):
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('DELETE FROM ingredients WHERE name = ?', (name,))
    conn.commit()
    conn.close()

def get_meal_plans():
    """
    Fetch all saved meal plans, most-recent first.
    Returns a list of tuples:
      (id, meal_type, meal_name, meal_ingredients, meal_instructions)
    """
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute("""
        SELECT id,
               meal_type,
               meal_name,
               meal_ingredients,
               meal_instructions
        FROM meal_plans
        ORDER BY id DESC
    """)  # <-- triple-quotes open and close correctly
    plans = c.fetchall()
    conn.close()
    return plans

