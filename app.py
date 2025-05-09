import re
import subprocess
import streamlit as st

# Configure Streamlit app
st.set_page_config(page_title="AI Recipe Recommender")
st.title("🍳 AI Recipe Recommender")

# Ingredient input
ingredients_input = st.text_input(
    "Enter your ingredients (comma-separated)",
    placeholder="e.g., chicken, rice, bell pepper"
)

if st.button("Get Recipe"):
    if not ingredients_input:
        st.error("Please enter at least one ingredient.")
    else:
        ingredients = [i.strip() for i in ingredients_input.split(",") if i.strip()]
        # Instruct model to format as Markdown list and omit internal tags
        prompt = (
            f"Suggest a cooking recipe using the following ingredients: {', '.join(ingredients)}. "
            "Respond only in Markdown format with: 1) a level-2 heading for the recipe name, "
            "2) ingredients as bullet points under an 'Ingredients' subheading, and "
            """"3) numbered steps under an 'Instructions' subheading. "
            "Do not include any <think> tags or analysis."""
        )
        # Show spinner while generating
        with st.spinner("Generating recipe..."):
            try:
                # Launch Ollama process and send prompt via STDIN
                proc = subprocess.Popen(
                    ["ollama", "run", "deepseek-r1"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = proc.communicate(prompt, timeout=60)

                if proc.returncode != 0:
                    err = stderr.strip() or f"Exit code {proc.returncode}"
                    st.error(f"Error fetching recipe: {err}")
                else:
                    # Clean any stray tags
                    recipe_md = re.sub(r"<.*?>", "", stdout).strip()
                    if not recipe_md:
                        st.warning("No response from the model. Try again or check your Ollama setup.")
                    else:
                        st.subheader("Suggested Recipe")
                        st.markdown(recipe_md)

            except subprocess.TimeoutExpired:
                proc.kill()
                st.error("The model took too long to respond. Please try again.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")