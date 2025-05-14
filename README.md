# Chefmate: Intelligent Recipe Planner

**Chefmate** is a great AI helper when you need to manage your kitchen ingredients, plan shoppnig trips and generate personalized recipes based on the products you choose. It's built using Streamlit, allowing you to reduce food waste and enhance your culinary experiences.

---

## Key Features

* **Ingredients Tab:** This tab represents all your ingredients you currently have in your fridge. You can specify the quantity, units and the expiry date. Track items that are already expired or that are about to by checking the appropriate list (Show/Hide Expired). Items that have less than 4 days until being expired will have an orange colored expiry date. Expired ones are showed in red.
* **Shopping Cart Tab:** Organize and plan grocery shopping. Adding the products you're planning to buy allows you to click the "Prepare" button and add this item to your fridge.
* **AI Recipe Generator Tab:** Automatically generate recipes based on available ingredients, those you have in your shopping cart (plan to buy) and personal preferences. Choose the number of recipes you want to get and their type. Press the "Save The Recipe" button after the recipe you want to save to your cookbook.
* **Personal Cookbook Tab:** Save and manage your favorite recipes, searchable by keywords or meal types. All recipes are sorted from the newest to the oldest depending on when you add them to the cookbook.

---

## Technologies Used

* **Streamlit:** Interactive user interface
* **Python:** Backend logic
* **SQLite:** Database management
* **Google Gemini API:** AI-driven recipe generation

---

## Prerequisites

* Python 3.7 or later
* SQLite3
* Gemini API Key (from Google Generative AI)

---

## Installation Guide

### Step-by-Step Installation

1. **Clone the Repository:**

```bash
git clone https://github.com/3-2-AKV/Chefmate-for-AI-Hackathon-2025
cd chefmate
```

2. **Set Up a Virtual Environment (Optional but Recommended):**

```bash
python -m venv env
source env/bin/activate # on Windows: .\env\Scripts\activate
```

3. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables:**

Create a `.env` file in the root directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

---

## Usage Examples

### Running the Application

```bash
streamlit run main.py
```

### Adding Ingredients

* Navigate to **Ingredients** tab.
* Enter product details and click **Add**.

### Creating a Recipe

* Select ingredients you wish to use.
* Go to **Create Recipe** tab.
* Specify number of recipes, meal type, and preferences, then click **Create Recipe**.

---

## Configuration

* **Gemini API Key:** Required for recipe generation. Set via `.env` file.
* **Databases:** SQLite databases (`meal_planner.db`, `recipes.db`) store ingredients, shopping lists, and recipes.

---

## Project Structure

```
chefmate/
├── database.py              # Database interactions
├── existing_recipies.py     # Recipe retrieval from existing database
├── main.py                  # Main Streamlit application
├── recipe_gen.py            # Recipe generation via Gemini API
├── requirements.txt         # Project dependencies
├── meal_planner.db          # Ingredient, meal plan, and shopping list database
├── recipes.db               # Existing recipe database
└── README.md                # Project documentation
```

---

## Contributing Guidelines

Currently, no specific contributing guidelines provided. General recommendations:

* Fork and create a feature branch.
* Ensure clear commit messages.
* Test your changes locally before submitting a pull request.

---

## License

No explicit license information found. Please contact the repository owner for usage permissions or licensing details.

---

Enjoy exploring culinary creativity with Chefmate!
