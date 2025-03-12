import os
import streamlit as st
import pandas as pd
import pyttsx3
from gtts import gTTS

# Install dependencies (if needed)
os.system("pip install -r Requirements.txt")
os.system("pip install gtts pyttsx3")

# Page configuration
st.set_page_config(page_title="🍛 Indian Food Recipes Bot", layout="wide")

# Load dataset
@st.cache_data
def load_dataset(file_path):
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format.")
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None

# Load dataset
dataset_file = "IndianFoodDatasetXLS.xlsx"
recipes_df = load_dataset(dataset_file)

# Initialize session state
if "feedback" not in st.session_state:
    st.session_state["feedback"] = {}
if "images" not in st.session_state:
    st.session_state["images"] = {}

# Function to convert text to speech (with fallback to pyttsx3)
def text_to_speech(text, lang='en'):
    audio_file = "recipe.mp3"
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(audio_file)
    except Exception:
        engine = pyttsx3.init()
        engine.save_to_file(text, audio_file)
        engine.runAndWait()
    return audio_file

if recipes_df is None:
    st.error("Failed to load dataset.")
else:
    st.markdown("<h1 style='text-align: center; color: #ff6347;'>🍛 Indian Food Recipes Bot</h1>", unsafe_allow_html=True)

    # Sidebar search & filters
    st.sidebar.header("🔍 Search & Filter")
    search_query = st.sidebar.text_input("Search by Name or Ingredient")
    
    cuisine_list = ["All"] + sorted(recipes_df['Cuisine'].dropna().unique().tolist())
    course_list = ["All"] + sorted(recipes_df['Course'].dropna().unique().tolist())
    diet_list = ["All"] + sorted(recipes_df['Diet'].dropna().unique().tolist())

    cuisine = st.sidebar.selectbox("Filter by Cuisine", cuisine_list)
    course = st.sidebar.selectbox("Filter by Course", course_list)
    diet = st.sidebar.selectbox("Filter by Diet", diet_list)

    # Apply Filters
    filtered_recipes = recipes_df.copy()
    if search_query:
        filtered_recipes = filtered_recipes[
            filtered_recipes['RecipeName'].str.contains(search_query, case=False, na=False) |
            filtered_recipes['TranslatedIngredients'].str.contains(search_query, case=False, na=False)
        ]
    if cuisine != "All":
        filtered_recipes = filtered_recipes[filtered_recipes['Cuisine'] == cuisine]
    if course != "All":
        filtered_recipes = filtered_recipes[filtered_recipes['Course'] == course]
    if diet != "All":
        filtered_recipes = filtered_recipes[filtered_recipes['Diet'] == diet]

    recipe_names = filtered_recipes['RecipeName'].tolist()
    recipe_name = st.sidebar.selectbox("Choose a recipe", recipe_names)

    if recipe_name:
        recipe = filtered_recipes[filtered_recipes['RecipeName'] == recipe_name].iloc[0]

        col1, col2 = st.columns([1, 2])

        with col1:
            if recipe_name in st.session_state["images"]:
                st.image(st.session_state["images"][recipe_name], use_column_width=True)
            else:
                st.image("default_recipe.jpg", use_column_width=True)

            uploaded_file = st.file_uploader("Upload your recipe image", type=["jpg", "png"])
            if uploaded_file is not None:
                st.session_state["images"][recipe_name] = uploaded_file
                st.success("Image uploaded successfully!")

        with col2:
            st.markdown(f"<h2>{recipe['RecipeName']}</h2>", unsafe_allow_html=True)
            
            # Ingredients
            st.markdown("**🥕 Ingredients:**")
            ingredients_text = "\n".join([f"- {ingredient.strip()}" for ingredient in recipe['TranslatedIngredients'].split(',') if ingredient.strip()])
            st.write(ingredients_text)
            
            # Instructions
            st.markdown("**📜 Instructions:**")
            instructions_text = "\n".join([f"- {step.strip()}" for step in recipe['TranslatedInstructions'].split('.') if step.strip()])
            st.write(instructions_text)
            
            # Text-to-Speech Button
            if st.button("🔊 Play Recipe Instructions"):
                combined_text = f"Ingredients:\n{ingredients_text}\n\nInstructions:\n{instructions_text}"
                audio_file = text_to_speech(combined_text)
                audio_bytes = open(audio_file, "rb").read()
                st.audio(audio_bytes, format="audio/mp3")

        # User Feedback Section
        st.markdown("### 💬 User Feedback")

        if recipe_name not in st.session_state["feedback"]:
            st.session_state["feedback"][recipe_name] = []

        for feedback in st.session_state["feedback"][recipe_name]:
            st.markdown(f"⭐ {feedback['rating']}/5 — {feedback['comment']}")

        rating = st.slider("Rate this recipe:", 1, 5, 3)
        comment = st.text_area("Leave a comment:")

        if st.button("Submit Feedback"):
            if comment.strip():
                st.session_state["feedback"][recipe_name].append({"rating": rating, "comment": comment})
                st.success("Feedback submitted successfully!")
            else:
                st.warning("Please enter a comment before submitting.")

    st.markdown("<hr><p style='text-align: center;'>👩‍🍳 Created with ❤️ using Streamlit</p>", unsafe_allow_html=True)
