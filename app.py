import streamlit as st
from google import genai
from PIL import Image

# --- Web App UI Setup ---
st.set_page_config(page_title="Nano Banana Studio", page_icon="🍌", layout="wide")
st.title("🍌 Nano Banana Studio: Prompt Engineer")
st.markdown("**Created by Sajjad SABOUR**")
st.write("Upload a base image, define your style, dial in your pro camera settings, and get the ultimate prompt.")

st.divider()

# --- Setup the API Client ---
try:
    api_key = st.secrets["API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("API Key not found! Please add it to your Streamlit Settings > Secrets.")
    st.stop()

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
        "3. Atmosphere & Material Style:",
        [
            "Workspace & PC Setups (Wood grains, matte plastics, glowing screens)",
            "Generic Scene / Character",
            "Cosmetics / Beauty (Soft lighting, caustics, subsurface scattering)",
            "Hard Surface Industrial (Brushed metals, hard reflections)",
            "Architecture / Interior (Global illumination, realistic fabrics)"
        ]
    )
    
    target_style = st.selectbox("4. Target Style:", ["Ultra Realistic Render", "Octane Render / Cinema 4D", "Anime / Cel Shaded", "Cinematic Photography", "Cyberpunk / Neon"])
    
    background_details = st.text_input("5. Change Background (Optional):", placeholder="e.g., A neon-lit gaming room, a modern home office...")
    
    extra_details = st.text_input("6. Extra Details (Optional):", placeholder="e.g., Make the desk walnut wood...")
    
    # NEW: Negative Prompt Field
    negative_prompt = st.text_input("7. Negative Prompt (What to AVOID):", placeholder="e.g., messy cables, people, plants, text, watermarks...")

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
                
                neg_instruction = f" --no {negative_prompt}" if negative_prompt else ""

                # Fixed Category Logic: Force it to apply to MATERIALS only, not objects.
                category_instruction = ""
                if "Workspace" in product_category:
                    category_instruction = (
                        f" Apply a high-end commercial workspace aesthetic to the existing objects. Focus ONLY on upgrading the materials (rich wood grains, premium fabrics, matte plastics, glowing screens). DO NOT add new physical objects to the scene."
                    )
                elif "Generic" not in product_category:
                    category_instruction = (
                        f" Apply a {product_category.split('(')[0].strip()} aesthetic to the existing objects. Focus ONLY on upgrading the physical materials and lighting appropriate for this style. DO NOT add new physical objects to the scene."
                    )

                if "3D Render" in input_type:
                    instruction = (
                        f"Act as an expert AI prompt engineer for Nano Banana. Look at the attached simple 3D render. "
                        f"CRITICAL RULE: Identify ONLY the exact physical objects present in this image. You MUST command the image AI to keep this exact 3D geometry. Do not add, hallucinate, or suggest any new structural elements, furniture, or props that are not in the reference image. "
                        f"{category_instruction} "
                        f"{('Additional details from user: ' + extra_details) if extra_details else ''}. "
                        f"{bg_instruction} "
                        f"Upgrade the scene to a {target_style} masterpiece with these photographic settings:\n"
                        f"- Lens: {selected_lens}\n"
                        f"- Depth of Field: {selected_dof}\n"
                        f"- Lighting: {selected_lighting}\n"
                        f"Write a highly detailed, comma-separated prompt. DO NOT output conversational text, just the raw prompt."
                    )
                else:
                    instruction = (
                        f"Act as an expert AI prompt engineer for Nano Banana. Look at the attached sketch. "
                        f"Use the sketch as a compositional guide. {category_instruction} "
                        f"{('Additional details from user: ' + extra_details) if extra_details else ''}. "
                        f"{bg_instruction} "
                        f"Creatively turn this into a {target_style} masterpiece with these photographic settings:\n"
                        f"- Lens: {selected_lens}\n"
                        f"- Depth of Field: {selected_dof}\n"
                        f"- Lighting: {selected_lighting}\n"
                        f"Write a highly detailed, comma-separated prompt. DO NOT output conversational text, just the raw prompt."
                    )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[instruction, img]
                )
                
                final_prompt = f"{response.text.strip()} {final_ar_tag}{neg_instruction}"
                
                st.success("Prompt successfully generated! Hover over the top right corner of the box below to copy it.")
                st.code(final_prompt, language="text")
                
            except Exception as e:
                st.error(f"Error generating prompt: {e}")
