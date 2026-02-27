import streamlit as st
import google.generativeai as genai

# --- Web App UI Setup ---
st.set_page_config(page_title="AE Expression Generator", page_icon="🎬")
st.title("🎬 After Effects Expression Generator")
st.markdown("**Created by Sajjad SABOUR**") # Don't forget your name!
st.write("Choose a preset or describe the animation you want, and the AI will write the JavaScript expression for you.")

st.divider()

# --- 10 Quick Presets ---
presets = [
    "Custom (Type your own below)",
    "Inertial Bounce (Realistic overshoot/bounce when keyframes stop)",
    "Continuous Wiggle (Random smooth movement on all axes)",
    "Seamless Loop (Cycle keyframes forever without stopping)",
    "Hovering / Floating Object (Smooth, slow up-and-down motion)",
    "Neon Light Flicker (Random, sharp jumps in opacity)",
    "Auto-Rotate (Constant spinning over time without keyframes)",
    "Squash and Stretch (Scale changes based on the layer's speed)",
    "Pendulum Swing (Smooth back-and-forth rotation from an anchor point)",
    "Layer Delay (Follow the movement of the layer above it with a slight time delay)",
    "Blinking Cursor (Turn opacity on and off every second like a computer prompt)"
]

selected_preset = st.selectbox("⚡ Quick Presets:", presets)

# --- User Input Logic ---
# If they choose Custom, show the text box. Otherwise, use the preset description.
if selected_preset == "Custom (Type your own below)":
    user_text = st.text_area("Describe the custom motion:", height=100)
else:
    user_text = selected_preset
    st.info(f"**Selected Preset:** {user_text}")

if st.button("Generate Expression", type="primary"):
    if not user_text:
        st.warning("Please type an animation description.")
    else:
        try:
            # Securely pull the API key
            api_key = st.secrets["API_KEY"]
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Generate the expression
            prompt = f"Write an Adobe After Effects expression for this animation: '{user_text}'. ONLY output the raw JavaScript code. Do not include markdown formatting like ```javascript. Do not explain the code."
            
            with st.spinner("Thinking and writing..."):
                response = model.generate_content(prompt)
                
            st.success("Expression Generated! Hover over the box below to copy it.")
            
            # Display result with an automatic copy button
            st.code(response.text.strip(), language="javascript")
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
