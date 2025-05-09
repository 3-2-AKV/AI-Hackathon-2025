from database import insert_ingredient

# Function to add an ingredient to the database
def add_ingredient_to_db(name, amount, unit, expiration_date):
    insert_ingredient(name, amount, unit, expiration_date)