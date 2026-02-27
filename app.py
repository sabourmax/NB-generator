import streamlit as st
import google.generativeai as genai

# --- Web App UI Setup ---
st.set_page_config(page_title="AE Expression Generator", page_icon="🎬")
st.title("🎬 After Effects Expression Generator")
st.write("Describe the motion or animation you want, and the AI will write the JavaScript expression for you.")

# --- API Key Input (Secure for web) ---
api_key = st.text_input("Enter your Google Gemini API Key:", type="password")
st.markdown("*Get a free API key from [Google AI Studio](https://aistudio.google.com/)*")

st.divider()

# --- User Input ---
user_text = st.text_area("Describe the motion (e.g., 'Wiggle on the Y axis every 2 seconds'):", height=100)

if st.button("Generate Expression", type="primary"):
    if not api_key:
        st.error("Please enter your API key first!")
    elif not user_text:
        st.warning("Please type an animation description.")
    else:
        try:
            # Configure AI
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate the expression
            prompt = f"Write an Adobe After Effects expression for this animation: '{user_text}'. ONLY output the raw JavaScript code. Do not include markdown formatting like ```javascript. Do not explain the code."
            
            with st.spinner("Thinking and writing..."):
                response = model.generate_content(prompt)
                
            st.success("Expression Generated! Hover over the box below to copy it.")
            
            # Display result with an automatic copy button
            st.code(response.text.strip(), language="javascript")
            
        except Exception as e:
            st.error(f"An error occurred: {e}")