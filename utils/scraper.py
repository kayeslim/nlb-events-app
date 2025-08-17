import json
import streamlit as st
from pathlib import Path
from utils.rag_database import EventsRAGDatabase

class NLBEventsScraper:
    def __init__(self):
        self.data_file = Path("data/nlb_events.jsonl")
        
    def scrape_events(self, max_events=50):
        """Load events from JSONL file (all events, no date filtering)"""
        
        # Validate max_events parameter
        if max_events < 5:
            st.error(f"❌ Invalid max_events: {max_events}. Minimum required is 5.")
            return []
        
        if max_events > 100:
            st.error(f"❌ Invalid max_events: {max_events}. Maximum allowed is 100.")
            return []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Check if JSONL file exists
        status_text.text("🔍 Loading events from data file...")
        progress_bar.progress(0.2)
        
        if not self.data_file.exists():
            st.warning("📁 JSONL data file not found. Please place 'nlb_events.jsonl' in the data/ folder.")
            status_text.text("📋 Using sample events for demonstration...")
            return self._get_sample_events()[:max_events]
        
        # Step 2: Load events from JSONL
        try:
            events = self._load_events_from_jsonl()
            progress_bar.progress(0.5)
            status_text.text(f"📊 Loaded {len(events)} events from file...")
            
        except Exception as e:
            st.error(f"❌ Error loading JSONL file: {str(e)}")
            status_text.text("📋 Using sample events as fallback...")
            return self._get_sample_events()[:max_events]
        
        # Step 3: Use all events (no date filtering)
        progress_bar.progress(0.7)
        status_text.text("📊 Processing all events...")
        
        all_events = events
        
        # Step 4: Limit to requested number
        if len(all_events) > max_events:
            all_events = all_events[:max_events]
        
        # Add sample events if we need more data (but respect the max_events limit)
        if len(all_events) < max_events:
            sample_events = self._get_sample_events()
            needed_events = max_events - len(all_events)
            all_events.extend(sample_events[:needed_events])
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Ready! Selected {len(all_events)} events for processing")
        
        return all_events
    
    def _load_events_from_jsonl(self):
        """Load events from JSONL file with duplicate checking"""
        events = []
        skipped_duplicates = 0
        
        # Initialize RAG database to check for existing events
        try:
            rag_db = EventsRAGDatabase()
        except Exception as e:
            st.warning(f"⚠️ Could not initialize database for duplicate checking: {e}")
            rag_db = None
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    line = line.strip()
                    if line:  # Skip empty lines
                        event_data = json.loads(line)
                        
                        # Normalize the event data format
                        normalized_event = self._normalize_event_format(event_data)
                        if normalized_event:
                            # Check for duplicates if database is available
                            if rag_db and rag_db.check_event_exists(normalized_event['event_id']):
                                skipped_duplicates += 1
                                st.info(f"⏭️ Skipping duplicate event: {normalized_event['title'][:50]}... (ID: {normalized_event['event_id']})")
                                continue
                            
                            events.append(normalized_event)
                            
                except json.JSONDecodeError as e:
                    st.warning(f"⚠️ Skipping malformed JSON on line {line_num}: {str(e)}")
                    continue
                except Exception as e:
                    st.warning(f"⚠️ Error processing line {line_num}: {str(e)}")
                    continue
        
        if skipped_duplicates > 0:
            st.info(f"📊 Loaded {len(events)} unique events, skipped {skipped_duplicates} duplicates from JSONL")
        
        return events
    
    def _normalize_event_format(self, event_data):
        """Normalize event data to consistent format"""
        try:
            # Handle different possible field names in your JSONL
            title = (event_data.get('title') or 
                    event_data.get('name') or 
                    event_data.get('event_title') or 
                    'Untitled Event')
            
            description = (event_data.get('description') or 
                          event_data.get('summary') or 
                          event_data.get('details') or 
                          'No description available')
            
            # Fix: Use date_text and time_text from NLB JSONL format
            date = (event_data.get('date_text') or 
                   event_data.get('date') or 
                   event_data.get('start_date') or 
                   event_data.get('event_date') or 
                   'Date TBA')
            
            time = (event_data.get('time_text') or 
                   event_data.get('time') or 
                   event_data.get('start_time') or 
                   event_data.get('event_time') or 
                   '')
            
            location = (event_data.get('venue') or 
                       event_data.get('location') or 
                       event_data.get('library') or 
                       'NLB Library')
            
            url = (event_data.get('source_url') or 
                  event_data.get('url') or 
                  event_data.get('link') or 
                  'https://www.nlb.gov.sg/main/whats-on/events')
            
            category = (event_data.get('type') or 
                       event_data.get('category') or 
                       event_data.get('event_type') or 
                       'library_event')
             
            # Extract event_id from the data
            event_id = (event_data.get('event_id') or 
                       event_data.get('id') or 
                       'unknown')
             
            return {
                'title': str(title)[:200],  # Limit title length
                'description': str(description)[:1000],  # Limit description length
                'date': str(date),
                'time': str(time),
                'location': str(location),
                'url': str(url),
                'source': 'nlb_jsonl_data',
                'category': str(category).lower(),
                'event_id': str(event_id)
            }
            
        except Exception as e:
            st.warning(f"⚠️ Error normalizing event: {str(e)}")
            return None
    

    
    def _get_sample_events(self):
        """High-quality sample events as backup"""
        return [
            {
                'title': 'Storytime for 4-6 years old @ Tampines Regional Library | Early READ',
                'description': 'About the Programme: Join us for a session of storytelling where we share some interesting and fun tales with children aged 4-6 years old! This programme is intended for children 4-6 years old. Please note the following: •Parents are encouraged to accompany their child during Storytime for 4-6 years old. •NLB reserves the right to deny entry to participants who do not abide by the ground rules.',
                'date': 'Tue, 26 Aug',
                'time': '04:00 PM - 04:30 PM',
                'location': 'Tampines Regional Library - BooksForBabies, Public Space (Level 3)',
                'url': 'https://www.nlb.gov.sg/main/whats-on/event-detail?event-id=1114235912609',
                'source': 'nlb_sample',
                'category': 'storytelling',
                'event_id': '1114235912609'
            },
            {
                'title': 'Create Content that Connects and Converts',
                'description': 'In today\'s digital age, content isn\'t just king — it\'s the voice of your brand. Create Content that Connects and Converts is designed to help aspiring entrepreneurs, marketers, and business owners unlock the power of compelling content. Through this engaging and practical course, you\'ll learn what content really is, why it matters, and how to craft stories that speak directly to your audience.',
                'date': 'Sun, 24 Aug',
                'time': '01:00 PM - 07:00 PM',
                'location': 'Tampines Regional Library - Programme Zone (Level 6)',
                'url': 'https://www.nlb.gov.sg/main/whats-on/event-detail?event-id=175003824241',
                'source': 'nlb_sample',
                'category': 'workshop',
                'event_id': '175003824241'
            },
            {
                'title': 'Think Smart: Enhancing Critical Thinking in the Workplace',
                'description': 'In today\'s fast-paced and ever-changing work environment, the ability to think critically is more important than ever. This webinar will explore the essential skills and strategies needed to enhance critical thinking, and offer practical techniques to improve decision-making and problem-solving skills to increase effectiveness in the workplace.',
                'date': 'Tue, 19 Aug',
                'time': '07:00 PM - 08:30 PM',
                'location': 'Online',
                'url': 'https://www.nlb.gov.sg/main/whats-on/event-detail?event-id=175003850853',
                'source': 'nlb_sample',
                'category': 'talk',
                'event_id': '175003850853'
            },
            {
                'title': 'Leading the Machine: How to Think With AI, Not Like It',
                'description': 'As AI tools like ChatGPT and Gemini become part of daily life, a new challenge emerges —how do we think with it? This talk confronts the hidden cost of over-reliance: becoming a cognitive sloth. While AI accelerates outputs, it can dull our judgment, creativity, and sense-making skills.',
                'date': 'Tue, 09 Sep',
                'time': '07:00 PM - 08:30 PM',
                'location': 'Central Public Library – Programme Room 1',
                'url': 'https://www.nlb.gov.sg/main/whats-on/event-detail?event-id=175099303380',
                'source': 'nlb_sample',
                'category': 'talk',
                'event_id': '175099303380'
            },
            {
                'title': 'Dungeons & Dragons w/The Legitimate Business | Choa Chu Kang Public Library',
                'description': 'Heard of the world of Dungeons & Dragons (D&D)? Come by Choa Chu Kang Public Library for a taste of this legendary fantasy role-playing game and find out why millions of players worldwide have stepped into the boots of mighty heroes (and sneaky antiheroes) to create their own stories.',
                'date': 'Sat, 23 Aug',
                'time': '01:00 PM - 05:00 PM',
                'location': 'Choa Chu Kang Public Library – Programme Room 1 (Level 4)',
                'url': 'https://www.nlb.gov.sg/main/whats-on/event-detail?event-id=175266149742',
                'source': 'nlb_sample',
                'category': 'learnx',
                'event_id': '175266149742'
            },
            {
                'title': 'Artivation x NAFA: Introduction to Watercolour Painting',
                'description': 'Discover the joy of watercolour painting in this hands-on workshop! Perfect for absolute beginners, this session covers essential techniques like colour mixing, brush control, and layering. You\'ll create a simple landscape or floral piece while learning how to embrace the fluid, unpredictable nature of watercolours.',
                'date': 'Tue, 26 Aug',
                'time': '06:30 PM - 08:30 PM',
                'location': 'Yishun Public Library - Programme Zone',
                'url': 'https://www.nlb.gov.sg/main/whats-on/event-detail?event-id=175144541956',
                'source': 'nlb_sample',
                'category': 'workshop',
                'event_id': '175144541956'
            },
            {
                'title': 'Turn Data into Stories: Visualise Info With Looker Studio| My Digital Life',
                'description': 'In today\'s information-heavy world, making sense of data can feel overwhelming — whether you\'re a student, researcher, hobbyist, or just curious. How do you organise, analyse, and present data in a way that\'s clear and compelling? Join us for an introductory webinar on Looker Studio, a free and user-friendly tool that helps you transform raw data into beautiful, easy-to-understand reports and dashboards.',
                'date': 'Thu, 21 Aug',
                'time': '07:00 PM - 08:30 PM',
                'location': 'Online',
                'url': 'https://www.nlb.gov.sg/main/whats-on/event-detail?event-id=175094642690',
                'source': 'nlb_sample',
                'category': 'talk',
                'event_id': '175094642690'
            },
            {
                'title': 'Nature Walk @ Sembawang Park Connector',
                'description': 'Join us for a refreshing morning walk along the scenic Sembawang Park Connector and discover the rich history of Sembawang and the transformation of Bukit Canberra. This nature walk is a chance to reconnect with the nature, learn about the neibourhood history and bond with fellow participants through shared experience.',
                'date': 'Sat, 30 Aug',
                'time': '08:30 AM - 12:00 PM',
                'location': 'Sembawang Public Library - Programme Zone',
                'url': 'https://www.nlb.gov.sg/main/whats-on/event-detail?event-id=175126810971',
                'source': 'nlb_sample',
                'category': 'learnx',
                'event_id': '175126810971'
            }
        ]
    
    def get_total_events_count(self):
        """Get total number of events in JSONL file"""
        if not self.data_file.exists():
            return 0
        
        try:
            count = 0
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        count += 1
            return count
        except Exception:
            return 0
    
    def get_jsonl_statistics(self):
        """Get detailed statistics about the JSONL file including duplicates"""
        if not self.data_file.exists():
            return {
                "total_lines": 0,
                "unique_events": 0,
                "duplicate_events": 0,
                "malformed_lines": 0
            }
        
        try:
            total_lines = 0
            event_ids = []
            malformed_lines = 0
            
            # Initialize RAG database to check for existing events
            try:
                rag_db = EventsRAGDatabase()
            except Exception:
                rag_db = None
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        total_lines += 1
                        try:
                            event_data = json.loads(line)
                            event_id = event_data.get('event_id', event_data.get('id', 'unknown'))
                            event_ids.append(event_id)
                        except json.JSONDecodeError:
                            malformed_lines += 1
                        except Exception:
                            malformed_lines += 1
            
            # Count unique events
            unique_event_ids = set(event_ids)
            duplicate_count = len(event_ids) - len(unique_event_ids)
            
            # Count events that would be skipped due to existing in database
            existing_duplicates = 0
            if rag_db:
                for event_id in unique_event_ids:
                    if rag_db.check_event_exists(event_id):
                        existing_duplicates += 1
            
            return {
                "total_lines": total_lines,
                "unique_events": len(unique_event_ids),
                "duplicate_events": duplicate_count,
                "malformed_lines": malformed_lines,
                "existing_in_database": existing_duplicates,
                "new_events_available": len(unique_event_ids) - existing_duplicates
            }
            
        except Exception as e:
            st.warning(f"⚠️ Error analyzing JSONL file: {e}")
            return {
                "total_lines": 0,
                "unique_events": 0,
                "duplicate_events": 0,
                "malformed_lines": 0,
                "existing_in_database": 0,
                "new_events_available": 0
            }
