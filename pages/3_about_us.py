import streamlit as st
from utils.security import check_password

def main():
    if not check_password():
        return
    
    st.title("ℹ️ About Us")
    
    st.markdown("""
    ## Project Overview
    
    The **NLB Library Events Assistant** is an educational prototype that demonstrates AI-powered 
    government service discovery for Singapore's National Library Board events.
    """)
    
    with st.expander("🎯 Project Scope & Objectives", expanded=False):
        st.markdown("""
        **Scope:**
        - **Domain**: Singapore National Library Board (NLB) Events
        - **Data**: 426+ real NLB events from official website
        - **Purpose**: Educational AI capstone project
        
        **Objectives:**
        - Consolidate NLB event information in one platform
        - Provide personalized event recommendations via AI
        - Demonstrate LLM integration for government services
        - Showcase RAG (Retrieval Augmented Generation) technology
        """)
    
    with st.expander("📊 Data Sources & Collection", expanded=False):
        st.markdown("""
        **Primary Data Source:**
        - NLB Official Website (nlb.gov.sg/main/whats-on/events)
        - 426+ individual event detail pages
        
        **Collection Method:**
        - Two-stage custom data collection process
        - Manual URL discovery + automated event extraction
        - Structured output in JSONL format
        
        **Data Enhancement:**
        - LLM-generated summaries and Q&A pairs
        - Event categorization and audience targeting
        - Semantic search indexing
        """)
    
    with st.expander("🚀 Key Features", expanded=False):
        st.markdown("""
        **Use Case 1: Event Data Processing**
        - Load and validate NLB event data
        - LLM enhancement of event descriptions
        - RAG database creation for semantic search
        
        **Use Case 2: Personalized Recommendations**
        - Interactive chat interface (Eventie)
        - Intelligent parameter extraction (context, date, time, location, audience)
        - Multi-strategy semantic search
        - Calendar export (.ics) functionality
        
        **Database Browser**
        - Explore all processed events
        - Search and filter capabilities
        - Detailed event information display
        """)
    
    with st.expander("👥 Target Audience", expanded=False):
        st.markdown("""
        **Primary Users:**
        - Singapore residents seeking library events
        - Families looking for educational activities
        - Students and professionals pursuing learning
        - Seniors interested in community programs
        
        **Use Cases:**
        - Event discovery and planning
        - Personalized recommendations
        - Calendar integration
        - Educational content exploration
        """)
    
    with st.expander("🛠️ Technology Stack", expanded=False):
        st.markdown("""
        **Frontend:** Streamlit web application
        **AI/ML:** OpenAI GPT-3.5-turbo for LLM processing
        **Search:** Semantic text matching with metadata filtering
        **Data:** JSONL format for efficient streaming
        **Security:** Input validation and prompt injection prevention
        **Deployment:** Streamlit Community Cloud
        """)
    
    with st.expander("📚 Educational Context", expanded=False):
        st.markdown("""
        **AI Champions Bootcamp Capstone Project**
        
        **Demonstrates:**
        - Web scraping and data collection techniques
        - Large Language Model integration
        - Retrieval-Augmented Generation (RAG)
        - Government service digitization
        - User experience design principles
        
        **Learning Outcomes:**
        - End-to-end AI application development
        - Real-world data processing challenges
        - Ethical AI implementation
        - User-centered design
        """)
    
    with st.expander("⚠️ Limitations & Disclaimers", expanded=False):
        st.markdown("""
        **Educational Purpose Only:**
        - Prototype for learning and demonstration
        - Not intended for production use
        - May contain inaccuracies or outdated information
        
        **Data Limitations:**
        - Scraped data may not be real-time
        - LLM-generated content may contain errors
        - Sample data used when real data unavailable
        
        **Technical Constraints:**
        - Requires OpenAI API key for full functionality
        - Limited to NLB events only
        - No real-time data synchronization
        """)
    
    with st.expander("💡 Value Proposition", expanded=False):
        st.markdown("""
        **For Users:**
        - Centralized NLB event discovery
        - Personalized recommendations
        - Simplified access to library services
        - Calendar integration for planning
        
        **For Government:**
        - Demonstrates AI-enhanced citizen services
        - Shows potential for service digitization
        - Provides insights into user preferences
        - Educational case study for AI implementation
        
        **For Developers:**
        - Complete AI application example
        - RAG implementation reference
        - Government service integration patterns
        - Ethical AI development practices
        """)
    
    st.markdown("---")
    st.markdown("*This project showcases how AI can enhance citizen engagement with government services while maintaining educational and ethical standards.*")

if __name__ == "__main__":
    main()
