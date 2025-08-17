import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def check_password():
    """Simple password gate for Streamlit app"""
    
    # Initialize session state
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    def password_entered():
        if st.session_state.get("password_input", "") == os.getenv("APP_PASSWORD", "nlbevents2024"):
            st.session_state.password_correct = True
            if "password_input" in st.session_state:
                del st.session_state["password_input"]
        else:
            st.session_state.password_correct = False

    if not st.session_state.password_correct:
        password_input = st.text_input(
            "🔐 Enter Password", 
            type="password", 
            on_change=password_entered, 
            key="password_input"
        )
        
        if not st.session_state.password_correct:
            if "password_input" in st.session_state and st.session_state.password_input:
                st.error("❌ Password incorrect. Please try again.")
            else:
                st.info("Please enter the application password to continue.")
            return False
        else:
            return True
    else:
        return True

def setup_openai_key():
    """Setup OpenAI API key with form input and .env backup"""
    
    # Check if API key is already set in session
    if "openai_api_key" in st.session_state and st.session_state.openai_api_key:
        return st.session_state.openai_api_key
    
    # Try to get from .env file as backup
    env_api_key = os.getenv("OPENAI_API_KEY", "")
    
    st.subheader("🔑 OpenAI API Key Setup")
    
    if env_api_key:
        st.info("✅ Backup API key found in environment variables")
        
        # Option to use env key or enter new one
        use_env_key = st.checkbox("Use environment API key", value=True)
        
        if use_env_key:
            st.session_state.openai_api_key = env_api_key
            st.success("Using environment API key")
            return env_api_key
    else:
        st.warning("⚠️ No backup API key found in environment variables")
    
    # Form for API key input
    with st.form("api_key_form"):
        st.markdown("**Enter your OpenAI API key:**")
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        submitted = st.form_submit_button("Set API Key")
        
        if submitted:
            if api_key_input and api_key_input.startswith("sk-"):
                st.session_state.openai_api_key = api_key_input
                st.success("✅ API key set successfully!")
                st.rerun()
            else:
                st.error("❌ Please enter a valid OpenAI API key (starts with 'sk-')")
                return None
    
    # If no key is set, show instructions
    if "openai_api_key" not in st.session_state:
        st.markdown("""
        ### How to get your OpenAI API Key:
        1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
        2. Sign in to your account
        3. Click "Create new secret key"
        4. Copy the key and paste it above
        
        **Note**: Your API key is only stored in your browser session and is not saved permanently.
        """)
        return None
    
    return st.session_state.openai_api_key

def get_openai_key():
    """Get the current OpenAI API key from session or env"""
    return st.session_state.get("openai_api_key") or os.getenv("OPENAI_API_KEY", "")

def validate_user_input(text):
    """Basic input validation and prompt injection prevention"""
    
    # Check for common prompt injection patterns
    injection_patterns = [
        "ignore previous instructions",
        "system:",
        "assistant:",
        "user:",
        "prompt:",
        "forget everything",
        "new instructions"
    ]
    
    text_lower = text.lower()
    for pattern in injection_patterns:
        if pattern in text_lower:
            return False, f"Invalid input detected: {pattern}"
    
    # Basic length validation
    if len(text) > 1000:
        return False, "Input too long (max 1000 characters)"
    
    return True, "Valid input"
