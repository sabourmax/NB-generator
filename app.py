import streamlit as st
from google import genai
from PIL import Image

# --- Web App UI Setup ---
st.set_page_config(page_title="Nano Banana Studio", page_icon="🍌", layout="wide")
st.title("🍌 Nano Banana Studio: Prompt Engineer")
st.markdown("**Created by Sajjad SABOUR**")
st.write("Upload a base image, dial in your pro camera settings, and get the ultimate prompt ready to copy and paste.")

st.divider()

# --- Setup the API Client ---
try:
    api_key = st.secrets["API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("API Key not found! Please add it to your Streamlit Settings > Secrets.")
    st.stop()

# Helper function to match image dimensions to standard aspect ratio tags
def get_closest_aspect_ratio_tag(width, height):
    ratio = width / height
    if ratio >= 1.5: return "--ar 16:9"
    elif ratio >= 1.1: return "--ar 4:3"
    elif ratio <= 0.6: return "--ar 9:16"
    elif ratio <= 0.9: return "--ar 3:4"
    else: return "--ar 1:1"

# ==========================================
# PRO CONTROLS & PROMPT GENERATION
# ==========================================
col1, col2 = st.columns([1, 1.2])

with col1:
    uploaded_file = st.file_uploader("Upload your Sketch or Base Image:", type=["jpg", "jpeg", "png"])
    target_style = st.selectbox("Target Style:", ["Ultra Realistic Render", "Octane Render / Cinema 4D", "Anime / Cel Shaded", "Cinematic Photography", "Cyberpunk / Neon"])
    extra_details = st.text_input("Extra Details (Optional):", placeholder="e.g., Add a dual-monitor PC setup, make the RGB lights blue...")

with col2:
    st.markdown("### ⚙️ Pro Camera Controls")
    
    # Aspect Ratio Selection
    selected_ar = st.selectbox(
        "Aspect Ratio:", 
        ["Match Uploaded Image", "16:9", "9:16", "4:3", "3:4", "1:1"]
    )
    
    # Camera Lenses
    selected_lens = st.selectbox(
        "Camera Lens:", 
        [
            "Let the AI decide",
            "14mm Ultra-Wide (Great for sweeping room interiors)",
            "35mm Standard Cinematic",
            "50mm Human Eye Perspective",
            "85mm Telephoto (Perfect for character focal points)",
            "Macro Lens (Extreme close-up detail)"
        ]
    )
    
    # Depth of Field (DOF)
    selected_dof = st.selectbox(
        "Depth of Field (Bokeh):", 
        [
            "Let the AI decide",
            "Heavy Bokeh / Shallow DOF (Subject crisp, background very blurry)",
            "Subtle DOF (Slight background blur for professional cinematic look)",
            "Deep Focus / f/16 (Everything is perfectly in focus)"
        ]
    )
    
    # Lighting 
    selected_lighting = st.selectbox(
        "Lighting Setup:",
        [
            "Let the AI decide",
            "Cinematic Studio Lighting",
            "Volumetric Fog / God Rays",
            "Moody / Low Key Lighting",
            "Bright Natural Sunlight"
        ]
    )

if st.button("Generate Master Prompt ✨", type="primary"):
    if not uploaded_file:
        st.warning("Please upload an image first!")
    else:
        with st.spinner("Analyzing layout and engineering the prompt..."):
            try:
                img = Image.open(uploaded_file)
                
                # Logic to handle aspect ratio matching and formatting the tag
                if selected_ar == "Match Uploaded Image":
                    final_ar_tag = get_closest_aspect_ratio_tag(img.width, img.height)
                    st.info(f"Detected image proportions. Appending aspect ratio: **{final_ar_tag}**.")
                else:
                    final_ar_tag = f"--ar {selected_ar}"

                # Building the highly strict instruction prompt
                instruction = (
                    f"Act as an expert AI prompt engineer for Nano Banana. Look at the exact structure, composition, and layout of the attached image. "
                    f"{('Additional details: ' + extra_details) if extra_details else ''}. "
                    f"IMPORTANT: You MUST strictly enforce keeping the exact same structure, composition, and camera angle as the uploaded image. Do not change the perspective. "
                    f"Apply these specific photographic settings to your prompt keywords:\n"
                    f"- Target Style: {target_style}\n"
                    f"- Lens/Focal Length: {selected_lens}\n"
                    f"- Depth of Field: {selected_dof}\n"
                    f"- Lighting: {selected_lighting}\n"
                    f"Write a highly detailed, comma-separated prompt to recreate this exact layout as a {target_style} masterpiece. Include high-quality rendering textures. "
                    f"DO NOT include the aspect ratio in your text output. Only output the raw prompt text."
                )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[instruction, img]
                )
                
                # Combine the AI's prompt with the aspect ratio tag at the very end
                final_prompt = f"{response.text.strip()} {final_ar_tag}"
                
                st.success("Prompt successfully generated! Hover over the top right corner of the box below to copy it.")
                
                # st.code automatically provides a nice formatted box with a copy button
                st.code(final_prompt, language="text")
                
            except Exception as e:
                st.error(f"Error generating prompt: {e}")
