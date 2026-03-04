import streamlit as st
from google import genai
from PIL import Image

# --- Web App UI Setup ---
st.set_page_config(page_title="Nano Banana Studio", page_icon="🍌", layout="wide")
st.title("🍌 Nano Banana Studio: Prompt Engineer")
st.markdown("**Created by Sajjad SABOUR**")
st.write("Upload a base image, dial in your pro camera settings, and get an editable master prompt.")

st.divider()

# --- Initialize Session State for Editable Prompt ---
if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = ""

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
    
    target_style = st.selectbox("3. Target Style:", ["Ultra Realistic Render", "Octane Render / Cinema 4D", "Anime / Cel Shaded", "Cinematic Photography", "Cyberpunk / Neon"])
    
    background_details = st.text_input("4. Change Background (Optional):", placeholder="e.g., A neon-lit gaming room, a modern home office...")
    
    extra_details = st.text_input("5. Extra Details (Optional):", placeholder="e.g., Make the desk walnut wood...")

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

                bg_instruction = f" Replace the background/environment with: '{background_details}'." if background_details else " Keep the background exact."

                # --- HYPER-STRICT 3D RENDER INSTRUCTIONS ---
                if "3D Render" in input_type:
                    instruction = (
                        f"Act as a strict structural analyzer and lighting engine for Nano Banana. Look at the attached 3D blockout. "
                        f"CRITICAL RULE: Describe ONLY the literal geometric shapes and surfaces you see. If a surface is empty, state that it is empty. "
                        f"ABSOLUTELY DO NOT name, suggest, or add props, clutter, computers, plants, or characters unless they are explicitly modeled in the reference image. "
                        f"Your job is to assign high-end materials and lighting to the EXACT geometry shown. "
                        f"{('User overrides: ' + extra_details) if extra_details else ''}. {bg_instruction} "
                        f"Target style: {target_style}. Camera Lens: {selected_lens}. Depth of Field: {selected_dof}. Lighting: {selected_lighting}. "
                        f"Write a sparse, comma-separated prompt focused entirely on materials, lighting, textures, and the existing blank geometry. DO NOT write full sentences."
                    )
                else:
                    instruction = (
                        f"Act as an expert AI prompt engineer for Nano Banana. Look at the attached sketch. "
                        f"Use the sketch as a compositional guide. "
                        f"{('Additional details from user: ' + extra_details) if extra_details else ''}. {bg_instruction} "
                        f"Creatively turn this into a {target_style} masterpiece with these photographic settings:\n"
                        f"- Lens: {selected_lens}\n"
                        f"- Depth of Field: {selected_dof}\n"
                        f"- Lighting: {selected_lighting}\n"
                        f"Write a highly detailed, comma-separated prompt describing the scene, textures, and lighting. DO NOT output conversational text, just the raw prompt."
                    )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[instruction, img]
                )
                
                # Save the generated prompt to session state so it can be edited
                st.session_state.generated_prompt = f"{response.text.strip()} {final_ar_tag}"
                
            except Exception as e:
                st.error(f"Error generating prompt: {e}")

# --- EDITABLE PROMPT SECTION ---
# This section only appears if a prompt has been generated
if st.session_state.generated_prompt:
    st.divider()
    st.subheader("✏️ Review and Edit")
    
    # The text area allows the user to manually edit the prompt
    edited_prompt = st.text_area("Tweak your prompt here:", value=st.session_state.generated_prompt, height=150)
    
    st.success("Ready! Click the copy icon in the top right corner of the box below:")
    # The code box dynamically updates to show whatever the user typed in the text area above
    st.code(edited_prompt, language="text")
