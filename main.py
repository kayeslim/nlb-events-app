import streamlit as st
from utils.security import check_password, setup_openai_key

def main():
    st.set_page_config(
        page_title="NLB Events Assistant",
        page_icon="📚",
        layout="wide"
    )
    
    if not check_password():
        return
    
    # Setup OpenAI API key
    api_key = setup_openai_key()
    if not api_key:
        st.stop()  # Stop execution if no API key is provided
    
    st.title("📚 NLB Library Events Assistant")
    
    # Mandatory disclaimer in expander
    with st.expander("⚠️ IMPORTANT NOTICE", expanded=True):
        st.warning("""
        IMPORTANT NOTICE: This web application is a prototype developed for educational purposes
        only. The information provided here is NOT intended for real-world usage and should not be relied
        upon for making any decisions, especially those related to financial, legal, or healthcare matters.

        Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You
        assume full responsibility for how you use any generated output.

        Always consult with qualified professionals for accurate and personalized advice.
        """)
    
    st.markdown("""
    ## Welcome to the NLB Events Discovery System
    
    This application helps you discover and get personalized recommendations for 
    National Library Board events and programs across Singapore.
    
    ### Features:
    - 📊 **Use Case 1**: Build comprehensive events database from NLB website
    - 💬 **Use Case 2**: Get personalized event recommendations via chat
    - 🔍 **Database Browser**: Explore and search through all processed events
    - 📚 **Documentation**: Learn about methodology and implementation
    
    Navigate using the sidebar to explore different features.
    """)
    
    # Show API key status
    with st.sidebar:
        st.success("🔑 OpenAI API Key: Configured")

if __name__ == "__main__":
    main()
