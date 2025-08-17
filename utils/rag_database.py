import streamlit as st
import json
import pickle
import os
from pathlib import Path
import re

class EventsRAGDatabase:
    def __init__(self):
        self.data_dir = Path("./data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.data_dir / "metadata.pkl"
        
        # Load existing data if available
        self.events_metadata = []
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing metadata"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'rb') as f:
                    self.events_metadata = pickle.load(f)
        except Exception as e:
            st.warning(f"Could not load existing data: {e}")
            self.events_metadata = []
    
    def add_events_to_database(self, enhanced_events):
        """Add enhanced events to database using simple text matching with duplicate prevention"""
        
        if not enhanced_events:
            st.warning("No events to add to database")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Get existing event IDs to check for duplicates
        existing_event_ids = set()
        if self.events_metadata:
            existing_event_ids = {metadata.get('event_id', 'unknown') for metadata in self.events_metadata}
        
        # Prepare metadata with duplicate checking
        new_metadata = []
        skipped_duplicates = 0
        
        for i, event in enumerate(enhanced_events):
            event_id = event.get('event_id', 'unknown')
            
            # Check for duplicate event_id
            if event_id in existing_event_ids:
                skipped_duplicates += 1
                status_text.text(f"⏭️ Skipping duplicate: {event['title'][:50]}... (ID: {event_id})")
                continue
            
            # Create searchable document text
            doc_text = f"""
            {event['title']}
            {event.get('concise_summary', '')}
            {event.get('long_summary', '')}
            Category: {event.get('event_category', 'event')}
            Audience: {event.get('target_audience', 'general')}
            Location: {event['location']}
            Date: {event['date']}
            """
            
            new_metadata.append({
                "title": event['title'],
                "date": event['date'],
                "location": event['location'],
                "category": event.get('event_category', 'event'),
                "audience": event.get('target_audience', 'general'),
                "url": event.get('url', ''),
                "event_id": event_id,
                "full_data": event,
                "search_text": doc_text.lower()  # Store lowercase for matching
            })
            
            # Add to existing IDs set to prevent duplicates within the same batch
            existing_event_ids.add(event_id)
            
            status_text.text(f"📝 Processing: {event['title'][:50]}...")
            progress_bar.progress((i + 1) / len(enhanced_events) * 0.7)
        
        # Update metadata
        if not self.events_metadata:
            self.events_metadata = new_metadata
        else:
            self.events_metadata.extend(new_metadata)
        
        progress_bar.progress(0.9)
        status_text.text("💾 Saving database...")
        
        # Save to disk
        try:
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.events_metadata, f)
        except Exception as e:
            st.error(f"Failed to save database: {e}")
        
        progress_bar.progress(1.0)
        
        # Show results with duplicate information
        if skipped_duplicates > 0:
            status_text.text(f"✅ Added {len(new_metadata)} events, skipped {skipped_duplicates} duplicates")
            st.success(f"🎉 Database now contains {len(self.events_metadata)} events")
            st.info(f"📊 Processing Summary: {len(new_metadata)} new events added, {skipped_duplicates} duplicates skipped")
        else:
            status_text.text(f"✅ Added {len(new_metadata)} events to database")
            st.success(f"🎉 Database now contains {len(self.events_metadata)} events")
    
    def search_events(self, query, n_results=5, audience_filter=None, category_filter=None):
        """Search for relevant events using enhanced text matching with preference scoring"""
        
        if not self.events_metadata:
            return []
        
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        # Enhanced scoring system
        scored_events = []
        for metadata in self.events_metadata:
            # Apply filters first
            if audience_filter and audience_filter != "Any":
                if metadata.get("audience") != audience_filter:
                    continue
            
            if category_filter and category_filter != "Any":
                if metadata.get("category") != category_filter:
                    continue
            
            # Get event data
            event_data = metadata["full_data"]
            search_text = metadata.get("search_text", "")
            search_words = set(re.findall(r'\w+', search_text))
            
            # Calculate enhanced similarity score
            similarity_score = self._calculate_enhanced_score(
                query_lower, query_words, search_text, search_words, event_data
            )
            
            if similarity_score > 0:
                event_data_copy = event_data.copy()
                event_data_copy["similarity_score"] = similarity_score
                scored_events.append(event_data_copy)
        
        # Sort by similarity score and return top results
        scored_events.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        return scored_events[:n_results]
    
    def _calculate_enhanced_score(self, query_lower, query_words, search_text, search_words, event_data):
        """Calculate enhanced similarity score with preference weighting"""
        
        base_score = 0.0
        
        # 1. Word overlap score (30% weight)
        matches = len(query_words.intersection(search_words))
        total_query_words = len(query_words)
        if total_query_words > 0:
            word_overlap_score = matches / total_query_words
            base_score += word_overlap_score * 0.3
        
        # 2. Exact phrase matches (25% weight)
        if query_lower in search_text:
            base_score += 0.25
        
        # 3. Title relevance (20% weight)
        title_lower = event_data.get('title', '').lower()
        title_words = set(re.findall(r'\w+', title_lower))
        title_matches = len(query_words.intersection(title_words))
        if total_query_words > 0:
            title_score = title_matches / total_query_words
            base_score += title_score * 0.2
        
        # 4. Category/Audience matching (15% weight)
        category = event_data.get('event_category', '').lower()
        audience = event_data.get('target_audience', '').lower()
        
        category_matches = sum(1 for word in query_words if word in category)
        audience_matches = sum(1 for word in query_words if word in audience)
        
        if total_query_words > 0:
            category_audience_score = (category_matches + audience_matches) / total_query_words
            base_score += category_audience_score * 0.15
        
        # 5. Location matching (10% weight)
        location = event_data.get('location', '').lower()
        location_matches = sum(1 for word in query_words if word in location)
        if total_query_words > 0:
            location_score = location_matches / total_query_words
            base_score += location_score * 0.1
        
        # 6. Boost for specific preference matches
        boost_score = 0.0
        
        # Topic/interest matching
        topic_keywords = ['technology', 'tech', 'digital', 'computer', 'coding', 'programming',
                         'arts', 'art', 'craft', 'creative', 'painting', 'drawing',
                         'family', 'children', 'kids', 'parenting',
                         'workshop', 'class', 'learning', 'education', 'skill',
                         'book', 'reading', 'literature', 'storytelling',
                         'music', 'dance', 'performance', 'theatre',
                         'science', 'nature', 'environment', 'sustainability',
                         'business', 'entrepreneurship', 'career', 'professional',
                         'health', 'wellness', 'fitness', 'yoga', 'meditation']
        
        for keyword in topic_keywords:
            if keyword in query_lower and keyword in search_text:
                boost_score += 0.1
                break
        
        # Time matching
        time_keywords = ['morning', 'afternoon', 'evening', 'night', 'am', 'pm']
        for keyword in time_keywords:
            if keyword in query_lower and keyword in search_text:
                boost_score += 0.05
                break
        
        # Date matching
        date_keywords = ['weekend', 'week', 'today', 'tomorrow', 'month']
        for keyword in date_keywords:
            if keyword in query_lower and keyword in search_text:
                boost_score += 0.05
                break
        
        # Location matching
        location_keywords = ['central', 'east', 'west', 'north', 'south', 'orchard', 'bugis', 
                           'jurong', 'woodlands', 'sengkang', 'punggol', 'tampines']
        for keyword in location_keywords:
            if keyword in query_lower and keyword in search_text:
                boost_score += 0.05
                break
        
        # Apply boost (capped at 0.3 to avoid over-scoring)
        boost_score = min(boost_score, 0.3)
        base_score += boost_score
        
        # Normalize score to 0-1 range
        final_score = min(base_score, 1.0)
        
        return final_score
    
    def get_database_stats(self):
        """Get database statistics"""
        # Count unique event IDs
        event_ids = [metadata.get('event_id', 'unknown') for metadata in self.events_metadata]
        unique_event_ids = set(event_ids)
        
        return {
            "total_events": len(self.events_metadata),
            "unique_events": len(unique_event_ids),
            "duplicate_events": len(event_ids) - len(unique_event_ids),
            "collection_name": "simple_text_nlb_events"
        }
    
    def check_event_exists(self, event_id):
        """Check if an event with the given ID already exists in the database"""
        if not self.events_metadata:
            return False
        
        return any(metadata.get('event_id') == event_id for metadata in self.events_metadata)
    
    def get_duplicate_event_ids(self):
        """Get list of event IDs that appear multiple times in the database"""
        if not self.events_metadata:
            return []
        
        event_ids = [metadata.get('event_id', 'unknown') for metadata in self.events_metadata]
        from collections import Counter
        counter = Counter(event_ids)
        return [event_id for event_id, count in counter.items() if count > 1]
    
    def get_all_events(self):
        """Get all events from the database with full details"""
        if not self.events_metadata:
            return []
        
        # Return full event data for all events
        return [metadata["full_data"] for metadata in self.events_metadata]
