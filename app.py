import streamlit as st
import openai

# OpenAI API Key (Make sure to replace it with your actual API key)
openai.api_key = "your-api-key-here"

def generate_recipe(ingredients):
    prompt = f"Generate a simple recipe using the following ingredients: {ingredients}. Provide step-by-step instructions."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful chef."},
                  {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

# Streamlit UI
st.title("Food Recipe Generator 🍽️")

ingredients = st.text_area("Enter ingredients (comma-separated):", "eggs, tomatoes, onions")

if st.button("Generate Recipe"):
    if ingredients:
        recipe = generate_recipe(ingredients)
        st.subheader("Generated Recipe:")
        st.write(recipe)
    else:
        st.warning("Please enter some ingredients!")
