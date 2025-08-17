import streamlit as st
from utils.rag_database import EventsRAGDatabase
from utils.security import check_password, validate_user_input, get_openai_key
import pandas as pd
from icalendar import Calendar, Event
from datetime import datetime, date
import re
import openai
import json

def main():
    if not check_password():
        return
    
    # Check if OpenAI API key is available
    if not get_openai_key():
        st.error("❌ OpenAI API key not configured. Please go back to the main page and set up your API key.")
        return
    
    # Add custom CSS for better chat styling
    st.markdown("""
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #1f77b4;
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 0.1rem;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
        color: black;
        margin-right: 20%;
        border-bottom-left-radius: 0.1rem;
    }
    .chat-message .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .chat-message .message-content {
        line-height: 1.4;
    }
    .quick-action-btn {
        margin: 0.25rem 0;
    }
    .follow-up-btn {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        transition: all 0.2s;
    }
    .follow-up-btn:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("💬 Eventie - Your NLB Event Assistant")
    
    with st.expander("⚠️ IMPORTANT NOTICE", expanded=True):
        st.warning("""
        IMPORTANT NOTICE: This web application is a prototype developed for educational purposes
        only. The information provided here is NOT intended for real-world usage and should not be relied
        upon for making any decisions, especially those related to financial, legal, or healthcare matters.

        Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You
        assume full responsibility for how you use any generated output.

        Always consult with qualified professionals for accurate and personalized advice.
        """)
    
    # Initialize RAG database
    try:
        rag_db = EventsRAGDatabase()
        
        # Check if database has events
        stats = rag_db.get_database_stats()
        if stats["total_events"] == 0:
            st.warning("⚠️ No events found in database. Please run '1 use case 1' first to scrape and enhance events.")
            return
        else:
            st.info(f"📊 Database contains {stats['total_events']} events")
            
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        return
    
    # Initialize session state for conversation and user preferences
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = {
            "context": None,
            "date": None,
            "time": None,
            "location": None,
            "audience": None
        }
    
    if "current_recommendations" not in st.session_state:
        st.session_state.current_recommendations = []
    
    if "context_data" not in st.session_state:
        st.session_state.context_data = {}
    
    if "recommendations_for_download" not in st.session_state:
        st.session_state.recommendations_for_download = []
    
    # Debug mode toggle (optional - for development)
    with st.sidebar:
        debug_mode = st.checkbox("🔍 Debug Mode", value=False, help="Show context data and search queries")
        st.session_state.debug_mode = debug_mode
    
    # Chat interface container
    chat_container = st.container()
    
    with chat_container:
        # Step A → B: Display Welcome Message (ensure it's shown first)
        if not st.session_state.conversation_history:
            welcome_message = """
            **Hi there! I'm Eventie, your friendly NLB event assistant! 🎉**
            
            I'm here to help you discover amazing library events that match your interests perfectly!
            
            **🎯 To give you the best recommendations, I need to know about at least 3 out of 5 preferences:**
            
            **1. 📚 Context**: What kind of events interest you?
               • Technology & Digital (coding, AI, workshops)
               • Arts & Creative (painting, music, crafts)
               • Family Activities (storytelling, games)
               • Learning & Education (workshops, classes)
               • Health & Wellness (yoga, fitness)
               • Business & Career (networking, skills)
            
            **2. 📅 Date**: When would you like to attend?
               • This weekend, next week, tomorrow
               • Specific dates (e.g., 15th December)
               • Flexible timing
            
            **3. ⏰ Time**: What time works best?
               • Morning (9 AM - 12 PM)
               • Afternoon (1 PM - 5 PM)
               • Evening (6 PM - 9 PM)
               • Specific times (e.g., 2 PM)
            
            **4. 📍 Location**: Which area of Singapore?
               • Central (Orchard, Bugis, Marina Bay)
               • East (Tampines, Bedok, Pasir Ris)
               • West (Jurong, Woodlands, Clementi)
               • North (Sengkang, Punggol, Yishun)
               • South (Sentosa, HarbourFront)
            
            **5. 👥 Audience**: Who is this for?
               • Adults (18+)
               • Children (kids, young ones)
               • Families (parents with children)
               • Seniors (elderly, mature adults)
               • Teens (teenagers, youth)
            
            **💡 You can tell me all at once like:**
            *"I'm looking for technology workshops this weekend in Central Singapore for adults"*
            
            **Or I'll guide you through each preference step by step! 😊**
            
            **What would you like to tell me about first?**
            """
            
            # Add welcome message to conversation history
            st.session_state.conversation_history.append(("assistant", welcome_message))
        
        # Display conversation history in a chat-like format
        if st.session_state.conversation_history:
            st.markdown("### 💬 Our Conversation")
            
            # Create a chat-like display using CSS classes
            for i, (role, message) in enumerate(st.session_state.conversation_history):
                if role == "user":
                    # User message
                    st.markdown(f"""
                    <div class="chat-message user">
                        <div class="message-header">You</div>
                        <div class="message-content">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Assistant message
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div class="message-header">Eventie</div>
                        <div class="message-content">{message}</div>
                    </div>
                                         """, unsafe_allow_html=True)
         
         # New message input area (for ongoing conversation)
        st.markdown("---")
        st.markdown("### 💭 Send a message")
        
        # Use form for better input handling
        with st.form("chat_form", clear_on_submit=True):
            # Step B → C: User Input
            user_input = st.text_input(
                "Type your message here...",
                placeholder="e.g., I'm interested in technology workshops this weekend in Central Singapore",
                label_visibility="collapsed"
            )
            
            send_button = st.form_submit_button("💬 Send", type="primary", use_container_width=True)
        
        # Handle form submission
        if send_button and user_input:
            with st.spinner("🤖 Eventie is thinking..."):
                # Step C → D: Parse Input for Context
                if st.session_state.debug_mode:
                    st.info("🔄 Step C → D: Parsing input for context...")
                context_data = parse_input_for_context(user_input)
                
                # Step D → E: Check if Sufficient Context
                if st.session_state.debug_mode:
                    st.info("🔄 Step D → E: Checking if context is sufficient...")
                is_sufficient = check_sufficient_context(context_data)
                
                if is_sufficient:
                    # Step E → G: Search RAG DB with context data
                    if st.session_state.debug_mode:
                        st.info("🔄 Step E → G: Searching RAG database...")
                    recommendations = search_rag_database(context_data, rag_db)
                    
                    # Step G → I: Display Recommendation (with enhanced LLM response)
                    if st.session_state.debug_mode:
                        st.info("🔄 Step G → I: Displaying recommendations...")
                    if recommendations:
                        enhanced_response, enhanced_events = generate_enhanced_recommendations(context_data, rag_db)
                        st.session_state.conversation_history.append(("assistant", enhanced_response))
                        st.session_state.current_recommendations = enhanced_events[:3]
                    else:
                        display_recommendation(recommendations, rag_db)
                else:
                    # Step E → F: Prompt for more context
                    if st.session_state.debug_mode:
                        st.info("🔄 Step E → F: Prompting for more context...")
                    prompt_for_more_context(context_data)
            
            # Use form_submit_button approach to clear input
            st.rerun()
        
        # Reset conversation button (smaller, secondary option)
        if st.session_state.conversation_history:
            if st.button("🔄 Start New Conversation", type="secondary"):
                # Clear only chat history and LLM-related data
                st.session_state.conversation_history = []
                st.session_state.context_data = {}
                st.session_state.current_recommendations = []
                st.session_state.recommendations_for_download = []
                st.rerun()
    
    # Display current recommendations if we have any (in chat format)
    if st.session_state.current_recommendations:
        # Add recommendations to conversation history as assistant message
        recommendations_message = format_recommendations_for_chat(st.session_state.current_recommendations)
        st.session_state.conversation_history.append(("assistant", recommendations_message))
        
        # Store events for calendar download
        st.session_state.recommendations_for_download = st.session_state.current_recommendations.copy()
        
        # Clear current recommendations to avoid duplication
        st.session_state.current_recommendations = []
    
    # Display detailed event information as separate chat messages
    if hasattr(st.session_state, 'recommendations_for_download') and st.session_state.recommendations_for_download:
        st.markdown("---")
        st.markdown("### 📖 Detailed Event Information")
        
        # Create a separate chat-like display for detailed information
        for i, event in enumerate(st.session_state.recommendations_for_download, 1):
            details_message = format_event_details_for_chat(event, i)
            
            # Display as Eventie message in chat format
            st.markdown(f"""
            <div class="chat-message assistant">
                <div class="message-header">Eventie</div>
                <div class="message-content">{details_message}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Calendar download section (appears after chat conversation)
    if hasattr(st.session_state, 'recommendations_for_download') and st.session_state.recommendations_for_download:
        st.markdown("---")
        st.markdown("### 📅 Add to Your Calendar")
        st.markdown("Ready to add these events to your calendar? Download the calendar file below:")
        
        col1, col2 = st.columns(2)
        with col1:
            ics_content = generate_ics_file(st.session_state.recommendations_for_download)
            st.download_button(
                label="📥 Download Calendar (.ics)",
                data=ics_content,
                file_name="nlb_personalized_events.ics",
                mime="text/calendar",
                use_container_width=True
            )
        
        with col2:
            # Create summary table for download
            event_data = []
            for event in st.session_state.recommendations_for_download:
                event_data.append({
                    "Title": event['title'],
                    "Date": event.get('date', 'Not specified'),
                    "Time": event.get('time', 'Not specified'),
                    "Location": event.get('location', 'Not specified'),
                    "Category": event.get('event_category', 'N/A'),
                    "Match Score": f"{event.get('similarity_score', 0):.2f}"
                })
            
            df = pd.DataFrame(event_data)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📊 Download Summary (CSV)",
                data=csv_data,
                file_name="nlb_personalized_events.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("💡 **Tip:** Import the .ics file into your calendar app (Google Calendar, Outlook, Apple Calendar, etc.) to automatically add all events!")
    
    # Start New Conversation button (only appears after recommendations are provided)
    if hasattr(st.session_state, 'recommendations_for_download') and st.session_state.recommendations_for_download:
        st.markdown("---")
        st.markdown("### 🔄 Ready for a Fresh Start?")
        st.markdown("Want to discover different events or try new preferences? Start a new conversation!")
        
        if st.button("🔄 Start New Conversation", type="primary", use_container_width=True):
            # Clear only chat history and LLM-related data
            st.session_state.conversation_history = []
            st.session_state.context_data = {}
            st.session_state.current_recommendations = []
            st.session_state.recommendations_for_download = []
            st.rerun()

def parse_event_date(date_string):
    """Attempt to parse event date string into a date object"""
    if not date_string or date_string == "Not available":
        return date.today()
    
    # Try to extract date patterns (flexible implementation)
    date_patterns = [
        r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
        r'(\d{1,2})-(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_string, re.IGNORECASE)
        if match:
            try:
                if pattern == date_patterns[0] or pattern == date_patterns[2]:
                    day = int(match.group(1) if pattern == date_patterns[0] else match.group(2))
                    month_name = match.group(2) if pattern == date_patterns[0] else match.group(1)
                    year = int(match.group(3))
                    
                    # Convert month name to number
                    month_map = {
                        'january': 1, 'february': 2, 'march': 3, 'april': 4,
                        'may': 5, 'june': 6, 'july': 7, 'august': 8,
                        'september': 9, 'october': 10, 'november': 11, 'december': 12
                    }
                    month = month_map.get(month_name.lower(), 1)
                    
                    return date(year, month, day)
            except (ValueError, IndexError):
                continue
    
    # Fallback to current date
    return date.today()

def generate_ics_file(events):
    """Generate ICS calendar file from events"""
    cal = Calendar()
    cal.add('prodid', '-//NLB Events//mxm.dk//')
    cal.add('version', '2.0')
    
    for event_data in events:
        event = Event()
        event.add('summary', event_data['title'])
        event.add('description', event_data.get('long_summary', event_data['description']))
        event.add('location', event_data['location'])
        
        # Parse event date or use fallback
        event_date = parse_event_date(event_data.get('date', ''))
        event.add('dtstart', event_date)
        event.add('dtend', event_date)
        
        cal.add_component(event)
    
    return cal.to_ical()

def parse_input_for_context(user_input):
    """Step D: Parse Input for Context using LLM for intelligent understanding"""
    
    # Validate input
    is_valid, validation_msg = validate_user_input(user_input)
    if not is_valid:
        st.error(f"❌ Input validation failed: {validation_msg}")
        return {}
    
    # Add user input to conversation history
    st.session_state.conversation_history.append(("user", user_input))
    
    # Initialize context data
    context_data = {
        "topic": None,
        "date": None,
        "time": None,
        "location": None,
        "raw_input": user_input,
        "confidence_score": 0
    }
    
    # Use LLM to intelligently parse user input
    try:
        context_data = parse_input_with_llm(user_input)
        context_data["raw_input"] = user_input  # Preserve original input
        
    except Exception as e:
        # Fallback to simple keyword matching if LLM fails
        if st.session_state.get("debug_mode", False):
            st.warning(f"⚠️ LLM parsing failed, using fallback: {str(e)}")
        context_data = parse_input_fallback(user_input)
    
    # Store context data in session state (Step D → H: Context Data)
    st.session_state.context_data = context_data
    
    # Log context data for debugging (optional)
    if st.session_state.get("debug_mode", False):
        st.info(f"🔍 Context Data: {context_data}")
    
    return context_data

def parse_input_with_llm(user_input):
    """Use LLM to intelligently understand user input"""
    
    # Set up OpenAI
    openai.api_key = get_openai_key()
    
    # Create conversation context for better understanding
    conversation_context = ""
    if st.session_state.conversation_history:
        # Include last few messages for context
        recent_messages = st.session_state.conversation_history[-4:]  # Last 4 messages
        for role, message in recent_messages:
            conversation_context += f"{role}: {message}\n"
    
    prompt = f"""
You are Eventie, an intelligent NLB event assistant. Extract user preferences from their input.

Conversation context:
{conversation_context}

User input: "{user_input}"

Extract the following preferences and return ONLY a valid JSON object:

{{
    "context": "extracted topic/interest or null",
    "date": "extracted date preference or null", 
    "time": "extracted time preference or null",
    "location": "extracted location preference or null",
    "audience": "extracted audience preference or null",
    "confidence_score": number_between_0_and_5
}}

Guidelines:
- Context: Look for interests like technology, arts, family activities, workshops, reading, music, science, business, health, etc.
- Date: Extract date preferences like "this weekend", "next week", "tomorrow", specific dates
- Time: Extract time preferences like "morning", "afternoon", "evening", specific times
- Location: Extract Singapore locations like "Central", "East", "West", "North", "South", or specific areas/regions
- Audience: Extract audience preferences like "adult", "children", "family", "senior", "teen", "kids", "parent", etc.
- Confidence: Score 0-5 based on how clearly preferences are expressed
- Be flexible with synonyms and natural language
- If unsure, return null for that field
- Return ONLY the JSON object, no other text
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1  # Low temperature for consistent parsing
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Clean the response to extract JSON
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON response
        parsed_data = json.loads(response_text)
        
        # Validate and normalize the parsed data
        context_data = {
            "context": parsed_data.get("context"),
            "date": parsed_data.get("date"),
            "time": parsed_data.get("time"),
            "location": parsed_data.get("location"),
            "audience": parsed_data.get("audience"),
            "raw_input": user_input,
            "confidence_score": min(5, max(0, parsed_data.get("confidence_score", 0)))
        }
        
        return context_data
        
    except Exception as e:
        if st.session_state.get("debug_mode", False):
            st.error(f"❌ LLM parsing error: {str(e)}")
        raise e

def parse_input_fallback(user_input):
    """Fallback to simple keyword matching if LLM fails"""
    
    context_data = {
        "context": None,
        "date": None,
        "time": None,
        "location": None,
        "audience": None,
        "raw_input": user_input,
        "confidence_score": 0
    }
    
    user_input_lower = user_input.lower()
    
    # Extract context (same as original topic)
    context_keywords = [
        "technology", "tech", "digital", "computer", "coding", "programming",
        "arts", "art", "craft", "creative", "painting", "drawing",
        "family", "children", "kids", "parenting",
        "workshop", "class", "learning", "education", "skill",
        "book", "reading", "literature", "storytelling",
        "music", "dance", "performance", "theatre",
        "science", "nature", "environment", "sustainability",
        "business", "entrepreneurship", "career", "professional",
        "health", "wellness", "fitness", "yoga", "meditation"
    ]
    
    for keyword in context_keywords:
        if keyword in user_input_lower:
            context_data["context"] = keyword
            context_data["confidence_score"] += 1
            break
    
    # Extract date (same as original)
    date_patterns = [
        r"this weekend", r"next weekend", r"weekend",
        r"this week", r"next week", r"week",
        r"today", r"tomorrow", r"next month",
        r"(\d{1,2})[/-](\d{1,2})",  # DD/MM or DD-MM
        r"(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)",
        r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            context_data["date"] = match.group(0)
            context_data["confidence_score"] += 1
            break
    
    # Extract time (same as original)
    time_keywords = [
        "morning", "afternoon", "evening", "night",
        "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm"
    ]
    
    for keyword in time_keywords:
        if keyword in user_input_lower:
            context_data["time"] = keyword
            context_data["confidence_score"] += 1
            break
    
    # Extract location (same as original)
    location_keywords = [
        "central", "east", "west", "north", "south",
        "orchard", "bugis", "marina bay", "chinatown", "little india",
        "jurong", "woodlands", "sengkang", "punggol", "tampines",
        "bedok", "pasir ris", "changi", "ang mo kio", "bishan",
        "toa payoh", "serangoon", "hougang", "yishun", "sembawang"
    ]
    
    for keyword in location_keywords:
        if keyword in user_input_lower:
            context_data["location"] = keyword
            context_data["confidence_score"] += 1
            break
    
    # Extract audience
    audience_keywords = [
        "adult", "adults", "grown-up", "grownup",
        "children", "child", "kids", "kid", "young",
        "family", "families", "parent", "parents",
        "senior", "seniors", "elderly", "old",
        "teen", "teens", "teenager", "teenagers",
        "student", "students", "youth", "young adult"
    ]
    
    for keyword in audience_keywords:
        if keyword in user_input_lower:
            context_data["audience"] = keyword
            context_data["confidence_score"] += 1
            break
    
    return context_data

def check_sufficient_context(context_data):
    """Step E: Check if Sufficient Context - Now requires 3 out of 5 parameters"""
    # Consider context sufficient if we have at least 3 out of 5 key preferences
    # or if confidence score is 3 or higher
    filled_preferences = sum(1 for key in ["context", "date", "time", "location", "audience"] 
                           if context_data.get(key))
    
    return filled_preferences >= 3 or context_data.get("confidence_score", 0) >= 3

def search_rag_database(context_data, rag_db):
    """Step G: Search RAG DB with context data (H → G: Context Data flows to search)"""
    
    # Set up OpenAI
    openai.api_key = get_openai_key()
    
    # Build enhanced search query from context data
    search_terms = []
    
    # Prioritize context and location for better matching
    if context_data.get("context"):
        search_terms.append(context_data["context"])
    if context_data.get("location"):
        search_terms.append(context_data["location"])
    if context_data.get("audience"):
        search_terms.append(context_data["audience"])
    if context_data.get("date"):
        search_terms.append(context_data["date"])
    if context_data.get("time"):
        search_terms.append(context_data["time"])
    
    # Create search query
    search_query = " ".join(search_terms) if search_terms else context_data.get("raw_input", "")
    
    # Log the search query for debugging (optional)
    if st.session_state.get("debug_mode", False):
        st.info(f"🔍 Search Query: {search_query}")
    
    # Search the RAG database
    try:
        results = rag_db.search_events(search_query, n_results=5)
        return results
    except Exception as e:
        st.error(f"❌ Search failed: {str(e)}")
        return []

def display_recommendation(recommendations, rag_db):
    """Step I: Display Recommendation"""
    
    if not recommendations:
        response = "I couldn't find any events matching your preferences. Could you try being more specific about what you're looking for?"
        st.session_state.conversation_history.append(("assistant", response))
        return
    
    # Generate personalized response
    response = f"Great! I found {len(recommendations)} events that match your interests:\n\n"
    
    for i, event in enumerate(recommendations[:3], 1):
        response += f"**{i}. {event.get('title', 'Untitled Event')}**\n"
        response += f"📅 {event.get('date', 'Date TBD')}\n"
        response += f"📍 {event.get('location', 'Location TBD')}\n"
        response += f"📝 {event.get('description', 'No description available')[:100]}...\n\n"
    
    response += "Would you like me to show you more details about any of these events?"
    
    st.session_state.conversation_history.append(("assistant", response))
    st.session_state.current_recommendations = recommendations[:3]

def prompt_for_more_context(context_data):
    """Step F: Prompt for more context - Now asks for 3 out of 5 parameters"""
    
    # Calculate how many more we need
    current_count = sum(1 for key in ["context", "date", "time", "location", "audience"] 
                       if context_data.get(key))
    needed_count = 3 - current_count
    
    # Start with what I have collected
    response = "**📋 Here's what I understand so far:**\n\n"
    
    # List what we have
    collected_info = []
    if context_data.get("context"):
        collected_info.append(f"✅ **📚 Context**: {context_data['context']}")
    else:
        collected_info.append("❌ **📚 Context**: Not specified")
    
    if context_data.get("date"):
        collected_info.append(f"✅ **📅 Date**: {context_data['date']}")
    else:
        collected_info.append("❌ **📅 Date**: Not specified")
    
    if context_data.get("time"):
        collected_info.append(f"✅ **⏰ Time**: {context_data['time']}")
    else:
        collected_info.append("❌ **⏰ Time**: Not specified")
    
    if context_data.get("location"):
        collected_info.append(f"✅ **📍 Location**: {context_data['location']}")
    else:
        collected_info.append("❌ **📍 Location**: Not specified")
    
    if context_data.get("audience"):
        collected_info.append(f"✅ **👥 Audience**: {context_data['audience']}")
    else:
        collected_info.append("❌ **👥 Audience**: Not specified")
    
    response += "\n".join(collected_info)
    response += f"\n\n**📊 Progress**: {current_count}/5 parameters collected"
    
    if needed_count <= 0:
        response += "\n\n🎉 **Perfect! I have enough information to find great events for you!**"
    else:
        # Build a helpful response based on what's missing
        missing_info = []
        
        if not context_data.get("context"):
            missing_info.append("**📚 what kind of events interest you** (technology, arts, family activities, etc.)")
        if not context_data.get("date"):
            missing_info.append("**📅 when you'd like to attend** (this weekend, next week, specific date)")
        if not context_data.get("time"):
            missing_info.append("**⏰ what time works best** (morning, afternoon, evening)")
        if not context_data.get("location"):
            missing_info.append("**📍 which area of Singapore** (Central, East, West, North, South)")
        if not context_data.get("audience"):
            missing_info.append("**👥 who this is for** (adults, children, families, seniors)")
        
        # Show only the number of missing preferences we need
        priority_missing = missing_info[:needed_count]
        
        response += f"\n\n**🎯 I need {needed_count} more parameter(s) to give you the best recommendations!**"
        
        if needed_count == 1:
            response += f"\n\n**What I still need:** {priority_missing[0]}"
        elif needed_count == 2:
            response += f"\n\n**What I still need:** {priority_missing[0]} and {priority_missing[1]}"
        else:
            response += f"\n\n**What I still need:** {', '.join(priority_missing[:-1])} and {priority_missing[-1]}"
        
        # Add helpful examples
        response += "\n\n**💡 Examples:**"
        if not context_data.get("context"):
            response += "\n• \"I'm interested in technology workshops\""
            response += "\n• \"Looking for arts and crafts activities\""
            response += "\n• \"Family-friendly events please\""
        if not context_data.get("date"):
            response += "\n• \"This weekend would be great\""
            response += "\n• \"Next week works for me\""
            response += "\n• \"Any time in December\""
        if not context_data.get("time"):
            response += "\n• \"Morning sessions preferred\""
            response += "\n• \"Afternoon or evening works\""
            response += "\n• \"Around 2 PM would be perfect\""
        if not context_data.get("location"):
            response += "\n• \"Something in Central Singapore\""
            response += "\n• \"East area would be convenient\""
            response += "\n• \"Near Orchard or Bugis\""
        if not context_data.get("audience"):
            response += "\n• \"For adults please\""
            response += "\n• \"Something for children\""
            response += "\n• \"Family activities\""
        
        response += f"\n\n**🎯 I need at least 3 out of 5 preferences to give you the best recommendations! 😊**"
    
    st.session_state.conversation_history.append(("assistant", response))

def generate_enhanced_recommendations(context_data, rag_db):
    """Generate enhanced recommendations using LLM with context data"""
    
    # Set up OpenAI
    openai.api_key = get_openai_key()
    
    # Build enhanced search query from context data
    search_terms = []
    
    # Prioritize context and location for better matching
    if context_data.get("context"):
        search_terms.append(context_data["context"])
    if context_data.get("location"):
        search_terms.append(context_data["location"])
    if context_data.get("audience"):
        search_terms.append(context_data["audience"])
    if context_data.get("date"):
        search_terms.append(context_data["date"])
    if context_data.get("time"):
        search_terms.append(context_data["time"])
    
    # Create multiple search strategies for better results
    search_strategies = []
    
    # Strategy 1: Full query with all context
    if search_terms:
        search_strategies.append(" ".join(search_terms))
    
    # Strategy 2: Context + Location + Audience (most important)
    if context_data.get("context") and context_data.get("location") and context_data.get("audience"):
        search_strategies.append(f"{context_data['context']} {context_data['location']} {context_data['audience']}")
    
    # Strategy 3: Context + Location (fallback)
    elif context_data.get("context") and context_data.get("location"):
        search_strategies.append(f"{context_data['context']} {context_data['location']}")
    
    # Strategy 4: Context + Audience (fallback)
    elif context_data.get("context") and context_data.get("audience"):
        search_strategies.append(f"{context_data['context']} {context_data['audience']}")
    
    # Strategy 5: Context only (fallback)
    elif context_data.get("context"):
        search_strategies.append(context_data["context"])
    
    # Strategy 6: Location only (if no context)
    elif context_data.get("location"):
        search_strategies.append(context_data["location"])
    
    # Try each search strategy and combine results
    all_events = []
    seen_event_ids = set()
    
    for strategy in search_strategies:
        events = rag_db.search_events(strategy, n_results=15)
        for event in events:
            event_id = event.get('event_id', event.get('title', ''))
            if event_id not in seen_event_ids:
                all_events.append(event)
                seen_event_ids.add(event_id)
    
    # Sort by similarity score and take top results
    all_events.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
    events = all_events[:10]
    
    if not events:
        return "I'm sorry, I couldn't find any events matching your preferences. Could you try being more specific or tell me about different interests?", []
    
    # Create context for LLM
    events_context = ""
    for i, event in enumerate(events[:3]):
        events_context += f"""
Event {i+1}: {event['title']}
Date: {event.get('date', 'Not specified')}
Time: {event.get('time', 'Not specified')}
Location: {event.get('location', 'Not specified')}
Category: {event.get('event_category', 'Not specified')}
Target Audience: {event.get('target_audience', 'Not specified')}
Summary: {event.get('concise_summary', event.get('description', 'Not available'))}
"""
    
    # Generate personalized response
    prompt = f"""
You are Eventie, a warm and enthusiastic NLB event assistant. The user has provided their context and you need to give them personalized recommendations.

User Context:
- Context: {context_data.get('context') or 'Not specified'}
- Date: {context_data.get('date') or 'Not specified'}
- Time: {context_data.get('time') or 'Not specified'}
- Location: {context_data.get('location') or 'Not specified'}
- Audience: {context_data.get('audience') or 'Not specified'}
- Raw Input: {context_data.get('raw_input', 'Not specified')}
- Confidence Score: {context_data.get('confidence_score', 0)}

Available events:
{events_context}

Provide a friendly, conversational response that:
1. First, acknowledge their context warmly and show what you understood
2. List the parameters you collected (use ✅ for collected, ❌ for missing)
3. Recommends exactly 3 events with specific reasons why each is perfect for them
4. Be enthusiastic and personal about each recommendation
5. End with an invitation to download their calendar

Start your response with a summary of what you understood, then provide recommendations.
Format your response as a warm conversation, not a list. Make it personal and engaging.
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.9
        )
        
        response_text = response.choices[0].message.content.strip()
        return response_text, events
        
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        # Fallback response with parameter summary
        fallback_response = f"Perfect! Based on your preferences, I found {len(events)} wonderful events for you!\n\n"
        
        # Add parameter summary
        fallback_response += "**📋 Here's what I understood:**\n\n"
        
        if context_data.get("context"):
            fallback_response += f"✅ **📚 Context**: {context_data['context']}\n"
        else:
            fallback_response += "❌ **📚 Context**: Not specified\n"
        
        if context_data.get("date"):
            fallback_response += f"✅ **📅 Date**: {context_data['date']}\n"
        else:
            fallback_response += "❌ **📅 Date**: Not specified\n"
        
        if context_data.get("time"):
            fallback_response += f"✅ **⏰ Time**: {context_data['time']}\n"
        else:
            fallback_response += "❌ **⏰ Time**: Not specified\n"
        
        if context_data.get("location"):
            fallback_response += f"✅ **📍 Location**: {context_data['location']}\n"
        else:
            fallback_response += "❌ **📍 Location**: Not specified\n"
        
        if context_data.get("audience"):
            fallback_response += f"✅ **👥 Audience**: {context_data['audience']}\n"
        else:
            fallback_response += "❌ **👥 Audience**: Not specified\n"
        
        fallback_response += f"\nLet me share the top 3 events that I think you'll love!"
        
        return fallback_response, events



def format_recommendations_for_chat(events):
    """Format recommendations as a chat message with calendar download options"""
    
    message = "**🎯 Here are your personalized recommendations:**\n\n"
    
    # Display events in a conversational format
    for i, event in enumerate(events):
        message += f"**{i+1}. 🎪 {event['title']}**\n"
        message += f"📅 **When:** {event.get('date', 'Not specified')} at {event.get('time', 'Not specified')}\n"
        message += f"📍 **Where:** {event.get('location', 'Not specified')}\n"
        message += f"📝 **Why you'll love it:** {event.get('concise_summary', event.get('description', 'Not available'))}\n\n"
    
    # Add calendar download invitation
    message += "**📅 Want to add these to your calendar?** You can download the calendar file below!\n\n"
    message += "💡 **Tip:** Import the .ics file into your calendar app (Google Calendar, Outlook, Apple Calendar, etc.) to automatically add all events!"
    
    return message

def format_event_details_for_chat(event, event_number):
    """Format detailed event information as a chat message"""
    
    message = f"**📖 Detailed Information - Event {event_number}**\n\n"
    message += f"**🎪 {event['title']}**\n\n"
    
    # Basic details
    message += f"📅 **Date & Time:** {event.get('date', 'Not specified')} at {event.get('time', 'Not specified')}\n"
    message += f"📍 **Location:** {event.get('location', 'Not specified')}\n"
    message += f"📂 **Category:** {event.get('event_category', 'N/A')}\n"
    message += f"👥 **Perfect for:** {event.get('target_audience', 'N/A')}\n"
    message += f"🎯 **Match Score:** {event.get('similarity_score', 0):.2f}\n\n"
    
    # Full description
    if event.get('long_summary'):
        message += "**📝 Full Description:**\n"
        message += f"{event['long_summary']}\n\n"
    elif event.get('description'):
        message += "**📝 Description:**\n"
        message += f"{event['description']}\n\n"
    
    # FAQ section
    if event.get('qna_pairs'):
        message += "**❓ Frequently Asked Questions:**\n"
        for i, qa in enumerate(event['qna_pairs'], 1):
            message += f"{i}. **Q:** {qa.get('question', 'N/A')}\n"
            message += f"   **A:** {qa.get('answer', 'N/A')}\n\n"
    
    # Original link
    if event.get('url', '').startswith('http'):
        message += f"🌐 **Original Event Page:** {event['url']}\n\n"
    
    message += "---"
    
    return message

def display_recommendations(events, rag_db):
    """Display recommendations with calendar download (for standalone display)"""
    
    st.markdown("### 🎯 Your Personalized Recommendations")
    st.markdown("Based on your preferences, here are the 3 events I think you'll love:")
    
    # Display events in a conversational format
    for i, event in enumerate(events):
        st.markdown(f"""
        **{i+1}. 🎪 {event['title']}**
        
        📅 **When:** {event.get('date', 'Not specified')} at {event.get('time', 'Not specified')}
        📍 **Where:** {event.get('location', 'Not specified')}
        📝 **Why you'll love it:** {event.get('concise_summary', event.get('description', 'Not available'))}
        """)
        
        # Show more details in expander
        with st.expander(f"📖 More details about {event['title']}"):
            if event.get('long_summary'):
                st.write("**Full Description:**")
                st.write(event['long_summary'])
            
            if event.get('qna_pairs'):
                st.write("**❓ Frequently Asked Questions:**")
                for qa in event['qna_pairs'][:3]:
                    st.write(f"**Q:** {qa.get('question', 'N/A')}")
                    st.write(f"**A:** {qa.get('answer', 'N/A')}")
                    st.write("")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**📂 Category:** {event.get('event_category', 'N/A')}")
                st.write(f"**👥 Perfect for:** {event.get('target_audience', 'N/A')}")
            with col2:
                st.metric("🎯 Match Score", f"{event.get('similarity_score', 0):.2f}")
                if event.get('url', '').startswith('http'):
                    st.link_button("🌐 View Original", event['url'])
        
        st.markdown("---")
    
    # Calendar download section
    st.markdown("### 📅 Add to Your Calendar")
    st.markdown("Ready to add these events to your calendar? Download the calendar file below:")
    
    col1, col2 = st.columns(2)
    with col1:
        ics_content = generate_ics_file(events)
        st.download_button(
            label="📥 Download Calendar (.ics)",
            data=ics_content,
            file_name="nlb_personalized_events.ics",
            mime="text/calendar",
            use_container_width=True
        )
    
    with col2:
        # Create summary table for download
        event_data = []
        for event in events:
            event_data.append({
                "Title": event['title'],
                "Date": event.get('date', 'Not specified'),
                "Time": event.get('time', 'Not specified'),
                "Location": event.get('location', 'Not specified'),
                "Category": event.get('event_category', 'N/A'),
                "Match Score": f"{event.get('similarity_score', 0):.2f}"
            })
        
        df = pd.DataFrame(event_data)
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📊 Download Summary (CSV)",
            data=csv_data,
            file_name="nlb_personalized_events.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    st.markdown("💡 **Tip:** Import the .ics file into your calendar app (Google Calendar, Outlook, Apple Calendar, etc.) to automatically add all events!")



if __name__ == "__main__":
    main()
