import streamlit as st
from utils.security import check_password
from streamlit_mermaid import st_mermaid

def main():
    if not check_password():
        return
    
    st.title("🔬 Methodology")
    
    st.markdown("""
    ## Technical Implementation & Data Flow
    
    This page explains the technical architecture, data processing workflows, and implementation 
    details of the NLB Events Assistant system.
    
    ### System Architecture
    
    #### Core Components
    1. **Data Loader Module** (`utils/scraper.py`)
    2. **LLM Enhancement Engine** (`utils/llm_enhancer.py`) 
    3. **RAG Database** (`utils/rag_database.py`)
    4. **Security Layer** (`utils/security.py`)
    5. **User Interface** (Streamlit pages)
    
    #### Technology Stack
    - **Framework**: Streamlit for rapid web app development
    - **LLM Integration**: OpenAI GPT models (gpt-3.5-turbo, gpt-5)
    - **Search Engine**: Text-based semantic matching with metadata filtering
    - **Data Processing**: Pandas for tabular operations
    - **Security**: Input validation and prompt injection prevention
    
    ### Data Flow Architecture
    
    ```
    JSONL File → Data Loader → Filtered Events → LLM Enhancement → Search DB → User Interface
         ↓            ↓            ↓               ↓              ↓           ↓
    Raw Events → Parsing → Normalized JSON → Enhanced JSON → Text Index → Search Results
    ```
    """)
    
    with st.expander("## Use Case 1 Flowchart: Event Data Processing", expanded=True):
        use_case_1_mermaid = '''
        flowchart TD
            A[User Input: Number of Events] --> B[Check JSONL Data File]
            B --> C{JSONL File Exists?}
            C -->|Yes| D[Load Events from JSONL]
            C -->|No| E[Use Sample Events]
            D --> F[Normalize Event Format]
            E --> F
            F --> G[Filter Aug/Sep Events]
            G --> H[Initialize LLM Enhancer]
            H --> I[For Each Event]
            I --> J[Generate Enhanced Content]
            J --> K[Create Summaries & Q&A]
            K --> L[Categorize Event]
            L --> M{More Events?}
            M -->|Yes| I
            M -->|No| N[Initialize Search Database]
            N --> O[Process Event Metadata]
            O --> P[Create Text Search Index]
            P --> Q[Store Database to Disk]
            Q --> R[Display Results to User]
        '''
        
        st_mermaid(use_case_1_mermaid)
    
    with st.expander("## Use Case 2 Flowchart: Eventie Conversational AI Workflow", expanded=True):
        eventie_mermaid = '''
        flowchart TD
            A[User Input] --> B[Input Validation]
            B --> C{Valid Input?}
            C -->|No| D[Show Error Message]
            C -->|Yes| E[LLM Input Parsing]
            E --> F[Extract 5 Parameters:<br/>Context, Date, Time, Location, Audience]
            F --> G{Sufficient Context?<br/>3 out of 5 parameters?}
            G -->|No| H[Prompt for More Context]
            H --> I[Show Parameter Progress]
            I --> J[User Provides More Info]
            J --> E
            G -->|Yes| K[Search RAG Database]
            K --> L[Multiple Search Strategies]
            L --> M[Rank by Similarity Score]
            M --> N[Generate Enhanced Response]
            N --> O[Display Recommendations]
            O --> P[Show Detailed Event Info]
            P --> Q[Calendar Download Options]
            Q --> R[Start New Conversation]
            R --> A
            
            style A fill:#e1f5fe
            style E fill:#f3e5f5
            style G fill:#fff3e0
            style K fill:#e8f5e8
            style N fill:#fce4ec
            style O fill:#e0f2f1
            style Q fill:#f1f8e9
        '''
        
        st_mermaid(eventie_mermaid)
    
    with st.expander("## Data Collection Flowchart: Custom Data Collection Process", expanded=True):
        scraping_mermaid = '''
        flowchart TD
            A[Manual URL Discovery] --> B[Compile Master URL List]
            B --> C[426 NLB Event URLs]
            C --> D[Data Collection System]
            D --> E[Extract Individual Events]
            E --> F[Structured Data Extraction]
            F --> G[Event Metadata + Descriptions]
            G --> H[Structured Event Data]
            H --> I[Quality Validation]
            I --> J[426 Events in JSONL Format]
            J --> K[Integration with Main App]
            K --> L[Enhanced by LLM Processing]
            L --> M[Search Database Creation]
            
            style A fill:#fff2cc
            style D fill:#d5e8d4
            style F fill:#dae8fc
            style H fill:#e1d5e7
            style J fill:#f8cecc
            style L fill:#ffe6cc
        '''
        
        st_mermaid(scraping_mermaid)
    
    with st.expander("### Data Collection Methodology", expanded=False):
        st.markdown("""
        **Two-Stage Data Collection Process:**
        
        **Stage 1: URL Collection**
        - Manual discovery of NLB event detail page patterns
        - Systematic extraction of 426 individual event URLs
        - Compilation into master URL list for batch processing
        
        **Stage 2: Event Data Extraction**
        - Custom Python data collection system
        - Structured data extraction with metadata parsing
        - Robust error handling with validation mechanisms
        - Structured output in JSONL format for streaming processing
        
        **Key Features:**
        - **Scalable Architecture**: Efficient data processing pipeline
        - **Quality Assurance**: Comprehensive data validation and error logging
        - **Rich Metadata**: Venue, timing, descriptions, tags, and location data
        - **Production Ready**: Suitable for enterprise-level government data processing
        """)
    
    with st.expander("### Eventie Algorithm Details", expanded=False):
        st.markdown("""
        **Parameter Extraction System**:
        - **LLM-Powered Parsing**: Uses GPT-3.5-turbo for intelligent input understanding
        - **5 Key Parameters**: Context, Date, Time, Location, Audience
        - **Confidence Scoring**: 0-5 scale based on clarity of user preferences
        - **Fallback Mechanism**: Keyword matching if LLM fails
        
        **Context Sufficiency Logic**:
        - Requires minimum 3 out of 5 parameters
        - OR confidence score ≥ 3
        - Progressive parameter collection with visual feedback
        
        **Multi-Strategy Search**:
        1. Full context query (all parameters)
        2. Context + Location + Audience (priority combination)
        3. Context + Location (fallback)
        4. Context + Audience (fallback)
        5. Context only (minimal)
        6. Location only (if no context)
        
        **Enhanced Response Generation**:
        - Personalized recommendations with parameter acknowledgment
        - Context-aware event matching
        - Conversational tone with enthusiasm
        - Calendar integration for seamless event management
        """)
    
    with st.expander("### Implementation Details", expanded=False):
        st.markdown("""
        #### 1. Data Loading Strategy
        
        **JSONL File Processing**:
        - Flexible field mapping handles different data formats
        - Line-by-line processing prevents memory issues
        - Graceful error handling for malformed JSON
        - Automatic normalization to consistent schema
        
        **Data Schema**:
        ```python
        Event Schema:
        {
            "title": str,
            "description": str, 
            "date": str,
            "time": str,
            "location": str,
            "url": str,
            "source": str,
            "category": str
        }
        ```
        
        #### 2. LLM Enhancement Process
        
        **Purpose**: Enrich scraped data with structured, searchable content
        
        **Enhancement Pipeline**:
        1. **Concise Summary**: 1-2 sentences for dense retrieval
        2. **Long Summary**: 120-200 words for comprehensive understanding
        3. **Q&A Pairs**: 3+ question-answer pairs to reduce hallucination
        4. **Categorization**: Automatic event type and audience classification
        
        **Prompt Engineering**:
        ```python
        Template Structure:
        - Input: Raw event data (title, description, date, location)
        - Output: JSON with enhanced fields
        - Instructions: Factual, library-focused, helpful tone
        - Validation: JSON parsing with fallback handling
        ```
        
        #### 3. RAG Database Implementation
        
        **Search Engine**: Text-based matching with word overlap scoring
        
        **Document Structure**:
        - **Text**: Searchable content combining all event fields
        - **Metadata**: Structured data for filtering
        - **Search Index**: Text-based search with metadata filtering
        
        **Search Strategy**:
        - Text similarity matching using word overlap scoring
        - Metadata filtering for audience/category
        - Top-K retrieval (default: 5 results)
        
        #### 4. Security Measures
        
        **Input Validation**:
        - Prompt injection detection
        - Length limitations (max 1000 chars)
        - Pattern-based filtering
        
        **Application Security**:
        - Password-protected access
        - Session state management
        - Error handling without exposing internals
        
        **Data Privacy**:
        - No personal data collection
        - Temporary session storage only
        - Public data sources only
        """)
    
    with st.expander("### Performance Considerations", expanded=False):
        st.markdown("""
        #### Optimization Strategies
        1. **Persistent Storage**: Search metadata saved to disk
        2. **Batch Processing**: Multiple events processed together
        3. **Progressive Loading**: Real-time progress indicators
        4. **Error Recovery**: Graceful fallbacks at each stage
        
        #### Scalability Factors
        - **Database Size**: Optimized for 50-500 events
        - **Response Time**: ~2-3 seconds for search queries
        - **Memory Usage**: Efficient text storage with metadata indexing
        - **API Limits**: Rate limiting for LLM calls
        """)
    
    with st.expander("### Quality Assurance", expanded=False):
        st.markdown("""
        #### Data Quality
        - **Validation**: Schema checking for all extracted data
        - **Completeness**: Fallback content for missing fields
        - **Accuracy**: Source attribution and disclaimer requirements
        
        #### User Experience
        - **Responsive Design**: Works on mobile and desktop
        - **Clear Feedback**: Progress indicators and status messages
        - **Error Handling**: User-friendly error messages
        - **Accessibility**: Proper contrast and semantic markup
        """)
    
    with st.expander("### Deployment Architecture", expanded=False):
        st.markdown("""
        #### Streamlit Community Cloud Setup
        ```
        Repository Structure:
        ├── requirements.txt (Dependencies)
        ├── nlb_app.py (Entry point)
        ├── pages/ (Multi-page structure)
        ├── utils/ (Core logic modules)
        └── data/ (JSONL data and generated indexes)
        ```
        
        #### Environment Configuration
        - **Secrets Management**: Streamlit secrets for API keys
        - **Password Protection**: Environment variable configuration
        - **Persistent Storage**: Pickle metadata files
        """)
    
    with st.expander("### Data Quality Metrics", expanded=False):
        st.markdown("""
        #### Processing Statistics
        - **Load Success Rate**: JSONL parsing accuracy
        - **Enhancement Quality**: LLM enhancement completion
        - **Search Relevance**: User satisfaction indicators
        - **Response Time**: Query processing speed
        """)
    
    with st.expander("### Future Enhancements", expanded=False):
        st.markdown("""
        #### Technical Improvements
        1. **Real-time Updates**: Scheduled data refresh
        2. **Advanced NLP**: Better event categorization
        3. **Multi-language Support**: Chinese/Malay translations
        4. **Mobile App**: Native mobile interface
        
        #### Feature Additions
        1. **User Preferences**: Personalized recommendation learning
        2. **Social Features**: Event sharing and reviews
        3. **Notifications**: Event reminders and updates
        4. **Integration**: External calendar synchronization
        
        ---
        
        *This methodology demonstrates a comprehensive approach to building AI-powered government service interfaces with focus on reliability, security, and user experience.*
        """)

if __name__ == "__main__":
    main()
