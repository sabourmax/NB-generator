import streamlit as st
from google import genai
from PIL import Image
import io

# --- Web App UI Setup ---
st.set_page_config(page_title="Nano Banana Studio", page_icon="🍌", layout="wide")
st.title("🍌 Nano Banana Studio")
st.markdown("**Created by Sajjad SABOUR**")
st.write("Step 1: Upload a base image and dial in your pro camera settings. Step 2: Generate the final render.")

st.divider()

# --- Initialize Session State ---
if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = ""
if "final_aspect_ratio" not in st.session_state:
    st.session_state.final_aspect_ratio = "1:1"

# --- Setup the API Client ---
try:
    api_key = st.secrets["API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("API Key not found! Please add it to your Streamlit Settings > Secrets.")
    st.stop()

# Helper function to match image dimensions to supported API ratios
def get_closest_aspect_ratio(width, height):
    ratio = width / height
    if ratio >= 1.5: return "16:9"
    elif ratio >= 1.1: return "4:3"
    elif ratio <= 0.6: return "9:16"
    elif ratio <= 0.9: return "3:4"
    else: return "1:1"

# ==========================================
# STEP 1: PRO CONTROLS & PROMPT GENERATION
# ==========================================
st.header("1️⃣ Analyze Image & Write Prompt")

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

if st.button("Analyze Image & Generate Prompt", type="primary"):
    if not uploaded_file:
        st.warning("Please upload an image first!")
    else:
        with st.spinner("Gemini is analyzing the layout and applying camera settings..."):
            try:
                img = Image.open(uploaded_file)
                
                # Logic to handle aspect ratio matching
                if selected_ar == "Match Uploaded Image":
                    calc_ar = get_closest_aspect_ratio(img.width, img.height)
                    st.session_state.final_aspect_ratio = calc_ar
                    st.info(f"Detected image proportions. Locked aspect ratio to **{calc_ar}**.")
                else:
                    st.session_state.final_aspect_ratio = selected_ar

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
                    f"Write a highly detailed, comma-separated prompt to recreate this exact layout as a {target_style} masterpiece. Include high-quality rendering textures. Only output the raw prompt text."
                )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[instruction, img]
                )
                
                st.session_state.generated_prompt = response.text.strip()
                st.success("Pro Prompt successfully generated!")
            except Exception as e:
                st.error(f"Error generating prompt: {e}")

st.divider()

# ==========================================
# STEP 2: EDIT PROMPT & GENERATE IMAGE
# ==========================================
st.header("2️⃣ Edit Prompt & Generate Image")

edited_prompt = st.text_area("Review and Edit Your Prompt:", value=st.session_state.generated_prompt, height=150)

if edited_prompt != st.session_state.generated_prompt:
    st.session_state.generated_prompt = edited_prompt

if st.button("Generate Image 🍌", type="primary"):
    if not st.session_state.generated_prompt.strip():
        st.warning("Please generate or write a prompt first!")
    else:
        with st.spinner(f"Nano Banana is rendering your image in {st.session_state.final_aspect_ratio}..."):
            try:
                # Fixed to the correct supported model version
                result = client.models.generate_images(
                    model='imagen-3.0-generate-001',
                    prompt=st.session_state.generated_prompt,
                    config=dict(
                        number_of_images=1,
                        aspect_ratio=st.session_state.final_aspect_ratio
                    )
                )
                
                final_image = result.generated_images[0].image
                
                st.image(final_image, caption=f"Generated by Nano Banana Studio | AR: {st.session_state.final_aspect_ratio}", use_container_width=True)
                
                buf = io.BytesIO()
                final_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="Download Full Resolution Image 📥",
                    data=byte_im,
                    file_name="nano_banana_pro_render.png",
                    mime="image/png",
                    type="primary"
                )
                
            except Exception as e:
                st.error(f"Image generation failed. Error: {e}")
