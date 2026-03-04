import streamlit as st
import google.generativeai as genai

# --- Web App UI Setup ---
st.set_page_config(page_title="AI Prompt Generator", page_icon="🎨", layout="wide")
st.title("🎨 AI Image Prompt Engineer")
st.markdown("**Created by Sajjad SABOUR**")
st.write("Generate highly detailed, professional prompts for Midjourney, Stable Diffusion, and other AI image generators.")

st.divider()

# --- Organize into 3 Tabs ---
tab1, tab2, tab3 = st.tabs(["🖌️ Sketch/3D to High-End", "📐 Change Angle", "🎛️ Advanced Studio Builder"])

# Helper function to generate and display the prompt
def generate_and_display(system_instruction):
    try:
        # This securely uses YOUR Gemini API key from the Streamlit Secrets vault
        api_key = st.secrets["API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        with st.spinner("Engineering the perfect prompt..."):
            response = model.generate_content(system_instruction)
            
        st.success("Prompt Generated! Hover over the top right of the box below to copy it.")
        st.code(response.text.strip(), language="text")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- TAB 1: Sketch / Basic 3D to High-End Render ---
with tab1:
    st.subheader("Convert a Sketch or Basic 3D to a Realistic Render")
    st.write("Use the generated prompt alongside an Image-to-Image (Img2Img) or ControlNet workflow.")
    
    base_subject = st.text_input("What is the sketch/3D model of?", placeholder="e.g., A futuristic motorcycle, a modern gaming room...")
    target_finish = st.selectbox("Desired Finish:", ["Photorealistic / Cinematic", "Octane Render / 3D Stylized", "Anime / Cel Shaded", "Matte Painting / Concept Art"])
    
    if st.button("Generate Prompt", key="btn_tab1", type="primary"):
        if not base_subject:
            st.warning("Please describe the subject.")
        else:
            instruction = f"Act as an expert AI image prompt engineer. I am using an image-to-image AI. I have a basic sketch/3D model of '{base_subject}'. Write a highly detailed, comma-separated prompt to turn it into a {target_finish} masterpiece. Include lighting, texture, and quality keywords (e.g., 8k, highly detailed, global illumination). Only output the prompt itself, nothing else."
            generate_and_display(instruction)

# --- TAB 2: Change Camera Angle ---
with tab2:
    st.subheader("Change the Angle or Perspective")
    st.write("Keep the same subject but force the AI to render it from a specific camera angle.")
    
    angle_subject = st.text_input("Describe the current subject/image:", placeholder="e.g., A cyberpunk character standing in an alleyway")
    new_angle = st.selectbox("New Camera Angle:", [
        "Bird's-eye view (Top down)", 
        "Low angle (Looking up, heroic)", 
        "Isometric (3D strategy game view)", 
        "Extreme Close-up (Macro)", 
        "Over-the-shoulder shot", 
        "Dutch angle (Tilted camera)"
    ])
    
    if st.button("Generate Prompt", key="btn_tab2", type="primary"):
        if not angle_subject:
            st.warning("Please describe the subject.")
        else:
            instruction = f"Act as an expert AI image prompt engineer. I want to render this subject: '{angle_subject}'. However, it MUST be shot from a {new_angle}. Write a highly detailed, comma-separated prompt emphasizing the camera angle, perspective, and depth of field. Only output the prompt itself, nothing else."
            generate_and_display(instruction)

# --- TAB 3: Advanced Studio Builder ---
with tab3:
    st.subheader("Advanced Prompt Builder from Scratch")
    
    col1, col2 = st.columns(2)
    with col1:
        adv_subject = st.text_area("Subject & Action:", placeholder="e.g., A glowing neon jellyfish floating through a ruined library")
        adv_lens = st.selectbox("Camera Lens:", ["35mm (Standard Cinematic)", "14mm (Ultra Wide/Distorted)", "85mm (Portrait/Shallow Depth of Field)", "200mm (Telephoto/Compressed background)", "Macro Lens (Extreme detail)"])
    
    with col2:
        adv_lighting = st.selectbox("Lighting Setup:", ["Cinematic Studio Lighting", "Golden Hour (Sunlight)", "Cyberpunk / Neon Rim Lights", "Volumetric Fog / God Rays", "Harsh Flash / Polaroid"])
        adv_ar = st.selectbox("Aspect Ratio:", ["16:9 (Landscape/Video)", "9:16 (Vertical/Social)", "1:1 (Square)", "21:9 (Ultrawide Cinema)"])
        
    if st.button("Generate Prompt", key="btn_tab3", type="primary"):
        if not adv_subject:
            st.warning("Please describe the subject.")
        else:
            instruction = f"Act as an expert AI image prompt engineer. Write a highly detailed, comma-separated prompt for this subject: '{adv_subject}'. Apply these specific parameters: Lens: {adv_lens}, Lighting: {adv_lighting}, Aspect Ratio: {adv_ar}. Include technical photography terms and high-quality keywords. At the very end of the prompt, add the aspect ratio parameter as '--ar {adv_ar.split(' ')[0]}'. Only output the prompt itself, nothing else."
            generate_and_display(instruction)
