"""
LLM Event Enhancement Module
============================

This module enhances library event data using OpenAI's language models.
Configuration is loaded from environment variables (.env file).

Environment Variables Required:
- LLM_MODEL: OpenAI model to use (default: gpt-3.5-turbo)

Hardcoded Parameters:
- Temperature: 0.7 (balanced consistency and creativity)
- Max Tokens: 1000 (standard length responses)

Advisory Notes:
- Temperature 0.7: Balanced consistency and creativity (optimized for event enhancement)
- Max Tokens 1000: Standard length responses suitable for JSON output

Model Options:
- gpt-3.5-turbo: Fast, cost-effective, good for most use cases
"""

import openai
import json
import streamlit as st
import os
from utils.security import get_openai_key

class EventEnhancer:
    def __init__(self):
        # Get API key from session or environment
        api_key = get_openai_key()
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set it up first.")
        
        # Set up OpenAI client
        openai.api_key = api_key
        self.client = openai
        
        # Load LLM configuration from environment variables with fallbacks
        # Advisory: These settings can be customized in your .env file
        self.model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        
        # Validate model selection
        supported_models = ['gpt-3.5-turbo']
        if self.model not in supported_models:
            st.warning(f"⚠️ Unsupported model '{self.model}'. Using gpt-3.5-turbo")
            self.model = 'gpt-3.5-turbo'
        
        # Log configuration for debugging
        st.info(f"🤖 LLM Configuration: Model={self.model}")
    
    def enhance_event_data(self, events):
        """Enhance scraped events with LLM-generated content"""
        
        enhanced_events = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, event in enumerate(events):
            status_text.text(f"🤖 Enhancing event {i+1}/{len(events)}: {event['title'][:50]}...")
            
            try:
                enhanced_event = self._enhance_single_event(event)
                enhanced_events.append(enhanced_event)
            except Exception as e:
                st.warning(f"⚠️ Failed to enhance event: {event['title']}")
                st.error(f"Error details: {str(e)}")
                # Add original event without enhancement
                event.update({
                    "concise_summary": f"{event['title']} at {event['location']}",
                    "long_summary": event['description'],
                    "qna_pairs": [],
                    "target_audience": "general",
                    "event_category": "library_event"
                })
                enhanced_events.append(event)
            
            progress_bar.progress((i + 1) / len(events))
        
        status_text.text("✅ Enhancement complete!")
        return enhanced_events
    
    def _clean_json_response(self, response_text):
        """Clean JSON response to handle common formatting issues"""
        import re
        
        # Remove trailing commas before closing brackets/braces
        cleaned = re.sub(r',(\s*[}\]])', r'\1', response_text)
        
        # Remove any leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # If the response doesn't start with {, try to find JSON object
        if not cleaned.startswith('{'):
            # Look for JSON object in the response
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                cleaned = match.group(0)
        
        return cleaned
    
    def _enhance_single_event(self, event):
        """Enhance a single event with LLM"""
        
        prompt = f"""
        Based on this library event information:
        Title: {event['title']}
        Description: {event['description']}
        Date: {event['date']}
        Time: {event.get('time', 'Not specified')}
        Location: {event['location']}
        
        Generate a JSON response with the following structure:
        {{
            "concise_summary": "1-2 sentence summary for search, min 20 words, in positive perspective",
            "long_summary": "120-200 word detailed summary, in promotional tone",
            "qna_pairs": [
                {{"question": "Who is this event for?", "answer": "..."}},
                {{"question": "What will I learn?", "answer": "..."}},
                {{"question": "Why I should attend this event?", "answer": "..."}},
                {{"question": "What are the key highlights?", "answer": "..."}},
                {{"question": "How long is the event?", "answer": "..."}},
                {{"question": "Do I need to register?", "answer": "..."}}
            ],
            "target_audience": "families/seniors/students/professionals/general",
            "event_category": "workshop/talk/exhibition/program/class/festival"
        }}
        
        Provide only the JSON object without any additional text or formatting.
        Keep responses factual and helpful for library event attendees.
        """
        
        try:
            # Use gpt-3.5-turbo for all requests
            response = self.client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Debug: Show what the LLM actually returned
            if not response_text:
                st.error(f"❌ LLM returned empty response for event: {event['title']}")
                raise ValueError("Empty response from LLM")
            
            st.info(f"🔍 LLM Response for '{event['title'][:30]}...': {response_text[:200]}...")
            
            try:
                # Clean the JSON response to handle common formatting issues
                cleaned_response = self._clean_json_response(response_text)
                enhanced_data = json.loads(cleaned_response)
                event.update(enhanced_data)
                return event
            except json.JSONDecodeError as e:
                st.warning(f"⚠️ JSON parsing failed for event: {event['title']}")
                st.error(f"JSON Error: {str(e)}")
                st.error(f"Raw response: {response_text}")
                st.error(f"Cleaned response: {cleaned_response}")
                raise
            # Fallback enhancement
            event.update({
                "concise_summary": f"{event['title']} at {event['location']}",
                "long_summary": event['description'],
                "qna_pairs": [
                    {"question": "Who is this event for?", "answer": "All library members and the public"},
                    {"question": "Do I need to register?", "answer": "Please check the NLB website for registration requirements"}
                ],
                "target_audience": "general",
                "event_category": "library_event"
            })
            return event
        except Exception as e:
            st.error(f"OpenAI API Error: {str(e)}")
            # Fallback enhancement
            event.update({
                "concise_summary": f"{event['title']} at {event['location']}",
                "long_summary": event['description'],
                "qna_pairs": [
                    {"question": "Who is this event for?", "answer": "All library members and the public"},
                    {"question": "Do I need to register?", "answer": "Please check the NLB website for registration requirements"}
                ],
                "target_audience": "general",
                "event_category": "library_event"
            })
            return event
