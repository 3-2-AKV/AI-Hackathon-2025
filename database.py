import sqlite3
import json
from datetime import datetime
from datetime import date

# Taking the current date - for the recipe
today_str = str(date.today())

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
                    ingredients TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    date TEXT NOT NULL)''')

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
def remove_ingredient_from_db(id):
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('DELETE FROM ingredients WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def get_recipes_from_db():
    conn = sqlite3.connect('meal_planner.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM meal_plans')
    recipes = c.fetchall()
    conn.close()
    return recipes

def save_recipes_to_db(response):
    # Parse the JSON response
    try:
        recipe = json.loads(response)
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return

    # Check that we got a dict, not a list
    if not isinstance(recipe, dict):
        print("Expected a single recipe as a JSON object.")
        return

    # Connect to SQLite database
    conn = sqlite3.connect("meal_planner.db")
    c = conn.cursor()

    # Loop through each recipe and insert into DB
    name = recipe.get("name", "Unnamed Recipe")
    meal_type = recipe.get("type", "unspecified")
    ingredients = '\n'.join(recipe.get("ingredients", []))  # Join list to string
    instructions = '\n'.join(recipe.get("instructions", []))  # Join list to string
    date = today_str

    c.execute('''
        INSERT INTO meal_plans (meal_type, meal_name, ingredients, instructions, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (meal_type, name, ingredients, instructions, date))

    conn.commit()
    conn.close()

def remove_recipe_from_db(name):
    conn = sqlite3.connect('meal_planner.db')
    c = conn.cursor()
    c.execute('DELETE FROM meal_plans WHERE meal_name = ?', (name,))
    conn.commit()
    conn.close()