import streamlit as st
from google import genai
from PIL import Image

# --- Web App UI Setup ---
st.set_page_config(page_title="Nano Banana Studio", page_icon="🍌", layout="wide")
st.title("🍌 Nano Banana Studio: Prompt Engineer")
st.markdown("**Created by Sajjad SABOUR**")
st.write("Upload a base image, define your product category, dial in your pro camera settings, and get the ultimate prompt.")

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
    st.markdown("### 📝 Core Settings")
    
    input_type = st.radio(
        "1. What are you uploading?", 
        ["🧊 Simple 3D Render / Blockout (Strict Geometry)", "🖌️ Hand-Drawn Sketch (Creative Interpretation)"]
    )
    
    uploaded_file = st.file_uploader("2. Upload your Image:", type=["jpg", "jpeg", "png"])
    
    product_category = st.selectbox(
        "3. Product / Subject Category:",
        [
            "Workspace & PC Setups (Desks, Chairs, Tech)",
            "Generic Scene / Character",
            "Cosmetics / Beauty Products",
            "Hard Surface Industrial / Automotive",
            "Architecture / Interior Design"
        ]
    )
    
    target_style = st.selectbox("4. Target Style:", ["Ultra Realistic Render", "Octane Render / Cinema 4D", "Anime / Cel Shaded", "Cinematic Photography", "Cyberpunk / Neon"])
    
    background_details = st.text_input("5. Change Background (Optional):", placeholder="e.g., A neon-lit gaming room, a modern home office...")
    
    extra_details = st.text_input("6. Extra Details (Optional):", placeholder="e.g., Make the desk walnut wood, add RGB lighting behind the monitors...")

with col2:
    st.markdown("### ⚙️ Pro Camera Controls")
    
    selected_ar = st.selectbox(
        "Aspect Ratio:", 
        ["Match Uploaded Image", "16:9", "9:16", "4:3", "3:4", "1:1"]
    )
    
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
    
    selected_dof = st.selectbox(
        "Depth of Field (Bokeh):", 
        [
            "Let the AI decide",
            "Heavy Bokeh / Shallow DOF (Subject crisp, background very blurry)",
            "Subtle DOF (Slight background blur for professional cinematic look)",
            "Deep Focus / f/16 (Everything is perfectly in focus)"
        ]
    )
    
    selected_lighting = st.selectbox(
        "Lighting Setup:",
        [
            "Let the AI decide",
            "Commercial Product Studio Lighting",
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
                
                if selected_ar == "Match Uploaded Image":
                    final_ar_tag = get_closest_aspect_ratio_tag(img.width, img.height)
                    st.info(f"Detected image proportions. Appending aspect ratio: **{final_ar_tag}**.")
                else:
                    final_ar_tag = f"--ar {selected_ar}"

                bg_instruction = f" Replace the current background/environment with this completely new background: '{background_details}'." if background_details else " Keep the background/environment consistent with the original image."

                category_instruction = ""
                if product_category == "Workspace & PC Setups (Desks, Chairs, Tech)":
                    category_instruction = (
                        f" This image features a professional workspace or gaming setup. Optimize the prompt specifically for high-end commercial visualization of desks, ergonomic chairs, and PC hardware. "
                        f"Explicitly mention high-quality physical materials like rich wood grains, premium fabrics, matte plastics, and glowing monitor screens. "
                        f"Ensure the staging looks like a top-tier lifestyle product shot with excellent cable management and atmospheric lighting. "
                    )
                elif product_category != "Generic Scene / Character":
                    category_instruction = (
                        f" This image features a '{product_category}'. Optimize the prompt specifically for high-end commercial visualization of this category. "
                        f"Explicitly mention appropriate physical materials and lighting that flatter this specific type of product. "
                    )

                if "3D Render" in input_type:
                    instruction = (
                        f"Act as an expert AI prompt engineer for Nano Banana. Look at the attached simple 3D render. "
                        f"{category_instruction}"
                        f"{('Additional details from user: ' + extra_details) if extra_details else ''}. "
                        f"CRITICAL INSTRUCTION: The generated prompt MUST explicitly command the image AI to keep the EXACT same foreground 3D structure, geometry, shapes, and details as the reference image. Do not add or remove structural elements from the main subject. "
                        f"{bg_instruction} "
                        f"The prompt should focus on upgrading the scene to a {target_style} masterpiece by applying ultra-realistic materials, high-end texturing, and these photographic settings:\n"
                        f"- Lens: {selected_lens}\n"
                        f"- Depth of Field: {selected_dof}\n"
                        f"- Lighting: {selected_lighting}\n"
                        f"Write a highly detailed, comma-separated prompt. DO NOT include the aspect ratio in your text output. Only output the raw prompt text."
                    )
                else:
                    instruction = (
                        f"Act as an expert AI prompt engineer for Nano Banana. Look at the attached sketch. "
                        f"{category_instruction}"
                        f"{('Additional details from user: ' + extra_details) if extra_details else ''}. "
                        f"{bg_instruction} "
                        f"Use the sketch as a compositional guide, but creatively flesh out the details to turn it into a {target_style} masterpiece. "
                        f"Apply these photographic settings:\n"
                        f"- Lens: {selected_lens}\n"
                        f"- Depth of Field: {selected_dof}\n"
                        f"- Lighting: {selected_lighting}\n"
                        f"Write a highly detailed, comma-separated prompt describing the scene, textures, and lighting. DO NOT include the aspect ratio in your text output. Only output the raw prompt text."
                    )
                
                # Locked safely to the fast model to avoid quota crashes
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[instruction, img]
                )
                
                final_prompt = f"{response.text.strip()} {final_ar_tag}"
                
                st.success("Prompt successfully generated! Hover over the top right corner of the box below to copy it.")
                st.code(final_prompt, language="text")
                
            except Exception as e:
                st.error(f"Error generating prompt: {e}")
