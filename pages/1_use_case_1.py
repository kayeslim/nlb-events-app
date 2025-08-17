import streamlit as st
from utils.scraper import NLBEventsScraper
from utils.llm_enhancer import EventEnhancer
from utils.rag_database import EventsRAGDatabase
from utils.security import check_password, get_openai_key
from pathlib import Path

def main():
    if not check_password():
        return
    
    # Check if OpenAI API key is available
    if not get_openai_key():
        st.error("❌ OpenAI API key not configured. Please go back to the main page and set up your API key.")
        return
    
    st.title("📊 Use Case 1: Event Data Processing & RAG DB Builder")
    
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
    This tool processes your scraped NLB event data (JSONL format), enhances it with LLM-generated content, 
    and builds a RAG database for Use Case 2.
    """)
    
    # Initialize scraper to check data availability
    scraper = NLBEventsScraper()
    total_events = scraper.get_total_events_count()
    jsonl_stats = scraper.get_jsonl_statistics()
    
    # Data source information
    st.subheader("📂 Data Source Status")
    
    if total_events > 0:
        st.success(f"✅ Found {total_events} events in JSONL data file")
        
        # Show detailed JSONL statistics
        with st.expander("📊 JSONL File Analysis"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Lines", jsonl_stats["total_lines"])
                st.metric("Unique Events", jsonl_stats["unique_events"])
            
            with col2:
                st.metric("Duplicates in File", jsonl_stats["duplicate_events"])
                st.metric("Malformed Lines", jsonl_stats["malformed_lines"])
            
            with col3:
                st.metric("Already in DB", jsonl_stats["existing_in_database"])
                st.metric("New Events Available", jsonl_stats["new_events_available"])
            
            # Show warnings if there are issues
            if jsonl_stats["duplicate_events"] > 0:
                st.warning(f"⚠️ Found {jsonl_stats['duplicate_events']} duplicate events within the JSONL file")
            
            if jsonl_stats["malformed_lines"] > 0:
                st.warning(f"⚠️ Found {jsonl_stats['malformed_lines']} malformed JSON lines")
            
            if jsonl_stats["existing_in_database"] > 0:
                st.info(f"ℹ️ {jsonl_stats['existing_in_database']} events already exist in the database and will be skipped")
        
        st.info("Your scraped events will be processed and enhanced with LLM-generated summaries")
        data_source = "real_data"
    else:
        st.warning("⚠️ JSONL data file not found. Please place 'nlb_events.jsonl' in the data/ folder")
        st.info("Will use high-quality sample events for demonstration")
        data_source = "sample_data"
        
        # Show file placement instructions
        with st.expander("📋 How to add your JSONL data"):
            st.markdown("""
            **To use your scraped events:**
            1. Place your `nlb_events.jsonl` file in the `data/` folder
            2. Each line should contain a JSON object with event information
            3. Supported fields: title, description, date, time, location, url, category
            4. Refresh this page after adding the file
            
            **Example JSONL format:**
            ```json
            {"title": "Digital Workshop", "description": "Learn new skills", "date": "15 August 2025", "location": "Central Library"}
            {"title": "Book Discussion", "description": "Monthly book club", "date": "22 September 2025", "location": "Tampines Library"}
            ```
            """)
    
    # Input form
    with st.form("processing_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            num_events = st.number_input(
                "Number of events to process:", 
                min_value=5, 
                max_value=100, 
                value=20,
                help="Select how many events to enhance and add to the database"
            )
        
        with col2:
            if data_source == "real_data":
                st.metric("New Events Available", jsonl_stats["new_events_available"])
            else:
                st.metric("Sample Events", "8 high-quality events")
        
        submitted = st.form_submit_button("🚀 Start Processing & Enhancement")
    
    if submitted:
        # Validate the number of events
        if num_events < 5:
            st.error(f"❌ Invalid number of events: {num_events}. Minimum required is 5 events.")
            st.info("💡 Please select a number between 5 and 100.")
            return
        
        if num_events > 100:
            st.error(f"❌ Invalid number of events: {num_events}. Maximum allowed is 100 events.")
            st.info("💡 Please select a number between 5 and 100.")
            return
        
        with st.spinner("Processing events..."):
            try:
                # Step 1: Load and filter events
                st.subheader("Step 1: Loading Event Data")
                events = scraper.scrape_events(max_events=num_events)
                
                if not events:
                    st.error("❌ No events could be loaded. Please check your data file or use sample events.")
                    return
                
                st.success(f"✅ Loaded {len(events)} events for processing")
                
                # Show sample of loaded events
                with st.expander("👀 Preview of loaded events"):
                    for i, event in enumerate(events[:3]):
                        st.write(f"**{i+1}. {event['title']}**")
                        st.write(f"📅 Date: {event['date']} | 🕐 Time: {event.get('time', 'Not specified')} | 📍 Location: {event['location']}")
                        st.write(f"🔗 Source: {event['source']}")
                        st.write("---")
                
                # Step 2: Enhance with LLM
                st.subheader("Step 2: AI Enhancement Process")
                enhancer = EventEnhancer()
                enhanced_events = enhancer.enhance_event_data(events)
                
                if not enhanced_events:
                    st.error("❌ Event enhancement failed. Please check your OpenAI API key.")
                    return
                
                st.success(f"✅ Successfully enhanced {len(enhanced_events)} events")
                
                # Step 3: Build RAG database
                st.subheader("Step 3: Building Vector Database")
                rag_db = EventsRAGDatabase()
                rag_db.add_events_to_database(enhanced_events)
                
                # Step 4: Display results
                st.subheader("📊 Processing Results")
                
                # Database statistics
                stats = rag_db.get_database_stats()
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Events Processed", len(enhanced_events))
                with col2:
                    st.metric("Total in Database", stats["total_events"])
                with col3:
                    st.metric("Unique Events", stats["unique_events"])
                with col4:
                    enhancement_rate = len([e for e in enhanced_events if e.get('concise_summary')]) / len(enhanced_events) * 100
                    st.metric("Enhancement Rate", f"{enhancement_rate:.0f}%")
                
                # Show duplicate information if any
                if stats["duplicate_events"] > 0:
                    st.warning(f"⚠️ Found {stats['duplicate_events']} duplicate events in database")
                    
                    # Show duplicate event IDs
                    duplicate_ids = rag_db.get_duplicate_event_ids()
                    if duplicate_ids:
                        with st.expander("🔍 View Duplicate Event IDs"):
                            st.write("The following event IDs appear multiple times:")
                            for dup_id in duplicate_ids:
                                st.code(dup_id)
                
                # Show example of enhanced event
                st.subheader("🔍 Example Enhanced Event")
                if enhanced_events:
                    example_event = enhanced_events[0]
                    
                    with st.expander("View enhanced event details"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**📄 Original Data:**")
                            st.write(f"Title: {example_event['title']}")
                            st.write(f"Date: {example_event['date']}")
                            st.write(f"Time: {example_event.get('time', 'Not specified')}")
                            st.write(f"Location: {example_event['location']}")
                            st.write(f"Description: {example_event['description'][:100]}...")
                        
                        with col2:
                            st.write("**🤖 AI Enhancements:**")
                            st.write(f"**Concise Summary:** {example_event.get('concise_summary', 'Not generated')}")
                            st.write(f"**Target Audience:** {example_event.get('target_audience', 'Not classified')}")
                            st.write(f"**Category:** {example_event.get('event_category', 'Not classified')}")
                            
                            if example_event.get('qna_pairs'):
                                st.write("**Sample Q&A:**")
                                for qa in example_event['qna_pairs'][:2]:
                                    st.write(f"Q: {qa.get('question', 'N/A')}")
                                    st.write(f"A: {qa.get('answer', 'N/A')}")
                
                # Success message
                st.success("🎉 Database successfully built! You can now use Use Case 2 for event recommendations.")
                
                # Database Browser Link
                st.subheader("🔍 Explore Your Database")
                st.markdown("""
                Your events have been successfully processed and added to the database! 
                You can now explore and search through all your events using the dedicated Database Browser.
                """)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("📊 **Database Statistics:**")
                    st.write(f"• Total Events: {stats['total_events']}")
                    st.write(f"• Unique Events: {stats['unique_events']}")
                    st.write(f"• Duplicates: {stats['duplicate_events']}")
                
                with col2:
                    st.success("🎯 **Next Steps:**")
                    st.write("• Browse events in '6 Database Browser'")
                    st.write("• Test recommendations in '2 Use Case 2'")
                    st.write("• Export data for analysis")
                
                # Next steps
                st.info("➡️ **Next Steps:** Go to '2 Use Case 2' to test the event recommendation system, or visit '6 Database Browser' to explore your processed events.")
                
            except Exception as e:
                st.error(f"❌ An error occurred during processing: {str(e)}")
                st.info("💡 Please check your OpenAI API key and data file format.")
                
                # Debug information
                with st.expander("🐛 Debug Information"):
                    st.write("Error details:", str(e))
                    st.write("Make sure:")
                    st.write("- OpenAI API key is valid and has sufficient credits")
                    st.write("- JSONL file format is correct")
                    st.write("- Network connection is stable")

if __name__ == "__main__":
    main()
