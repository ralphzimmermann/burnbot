# **AI Event Recommendation Engine - Project Plan**

## **Project Overview**
Build a minimal viable AI recommendation system for Burning Man events using FAISS for vector similarity search, GPT-5 for embeddings, Python/FastAPI backend, and React/Tailwind frontend.

**YAGNI Constraints:**
- No user accounts/authentication
- No event favoriting/bookmarking  
- No admin interface
- No analytics/tracking
- No caching beyond basic in-memory
- No database - JSON file only
- No advanced filtering UI

---

## **Phase 1: Backend Foundation**

### **Task 1.1: Project Structure & Dependencies**
**Acceptance Criteria:**
- [x] Create `website/backend/` directory structure
- [x] Set up virtual environment with requirements.txt
- [x] Install core dependencies: FastAPI, FAISS, OpenAI, numpy, uvicorn
- [x] Create basic FastAPI app that returns "Hello World" on GET /health

**Technical Details:**
```
website/backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   └── api/                 # API routes
├── data/
│   ├── events.json          # Symlink to ../../data/events.json
│   └── embeddings.npy       # Generated embeddings
├── requirements.txt
└── .env.example
```

**Dependencies (requirements.txt):**
```
fastapi==0.104.1
uvicorn==0.24.0
faiss-cpu==1.7.4
openai==1.3.5
numpy==1.24.3
pydantic==2.5.0
python-dotenv==1.0.0
```

### **Task 1.2: Data Models**
**Acceptance Criteria:**
- [x] Create Pydantic models for Event, RecommendationRequest, RecommendationResponse
- [x] Models validate against existing events.json structure
- [x] All fields properly typed with validation

**Technical Details:**
```python
# app/models/event.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import time, date

class EventTime(BaseModel):
    date: str           # MM/DD/YYYY format
    start_time: str     # HH:MM format  
    end_time: str       # HH:MM format

class Event(BaseModel):
    id: str
    times: List[EventTime]
    type: str
    camp: str
    campurl: Optional[str] = ""
    location: str
    description: str

class RecommendationRequest(BaseModel):
    query: str
    max_results: int = 30

class RecommendationResponse(BaseModel):
    events: List[Event]
    query: str
    processing_time_ms: float
```

---

## **Phase 2: Embedding Pipeline**

### **Task 2.1: Embedding Generation Service**
**Acceptance Criteria:**
- [x] Script generates embeddings for all events using GPT-5
- [x] Saves embeddings as numpy array to `data/embeddings.npy`
- [x] Handles API rate limits and errors gracefully
- [ ] Completes processing of 4K events in <10 minutes

**Technical Details:**
```python
# app/services/embedding_service.py
class EmbeddingService:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
    
    async def generate_event_embedding(self, event: Event) -> List[float]:
        # Combine type, camp, and description for embedding
        text = f"Type: {event.type}. Camp: {event.camp}. {event.description}"
        response = await self.client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding
    
    async def generate_all_embeddings(self, events: List[Event]) -> np.ndarray:
        # Batch process with rate limiting
        pass
```

### **Task 2.2: One-time Embedding Generation Script**
**Acceptance Criteria:**
- [x] Standalone script reads events.json, generates embeddings
- [x] Saves results to `data/embeddings.npy` 
- [x] Script is idempotent (can be re-run safely)
- [x] Logs progress and completion status

---

## **Phase 3: Recommendation Engine**

### **Task 3.1: FAISS Vector Search Service**
**Acceptance Criteria:**
- [x] Loads events.json and embeddings.npy on startup
- [x] Creates FAISS index with cosine similarity
- [ ] `find_similar_events()` returns top-k similar events in <10ms
- [ ] Memory usage stays under 200MB

**Technical Details:**
```python
# app/services/recommendation_service.py
class RecommendationService:
    def __init__(self):
        self.events: List[Event] = []
        self.index: faiss.Index = None
        self._load_data()
    
    def _load_data(self):
        # Load events and embeddings, create FAISS index
        pass
    
    async def get_recommendations(self, query: str, max_results: int = 30) -> List[Event]:
        # 1. Get query embedding from GPT-5
        # 2. Search FAISS index
        # 3. Return top events
        pass
    
    def find_similar_events(self, query_embedding: np.ndarray, k: int = 20) -> List[Event]:
        # Pure vector similarity search
        pass
```

### **Task 3.2: Query Processing**
**Acceptance Criteria:**
- [ ] Generates embedding for user query using GPT-5
- [ ] Returns results in <2 seconds for any query
- [ ] Handles empty queries gracefully
- [ ] Deduplicates results by event ID
- [ ] (Optional) Reranks top-N candidates with ChatGPT when enabled via env

---

## **Phase 4: API Layer**

### **Task 4.1: REST API Endpoints**
**Acceptance Criteria:**
- [ ] `GET /health` - returns service status
- [ ] `POST /recommend` - accepts query, returns recommendations
- [ ] `GET /events/{event_id}` - returns single event details
- [ ] All endpoints return proper HTTP status codes
- [ ] CORS enabled for frontend domain

**Technical Details:**
```python
# app/api/recommendations.py
@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    start_time = time.time()
    
    events = await recommendation_service.get_recommendations(
        request.query, 
        request.max_results
    )
    
    processing_time = (time.time() - start_time) * 1000
    
    return RecommendationResponse(
        events=events,
        query=request.query,
        processing_time_ms=processing_time
    )
```

### **Task 4.2: Error Handling & Validation**
**Acceptance Criteria:**
- [ ] Invalid requests return 400 with clear error message
- [ ] OpenAI API failures return 503 with retry message
- [ ] Empty query returns helpful error message
- [ ] All exceptions logged properly

---

## **Phase 5: Frontend Foundation**

### **Task 5.1: React Project Setup**
**Acceptance Criteria:**
- [ ] Create React app in `website/frontend/`
- [ ] Install and configure Tailwind CSS
- [ ] Set up basic routing with React Router
- [ ] Remove all default React boilerplate

**Technical Details:**
```
website/frontend/
├── src/
│   ├── components/
│   │   ├── SearchForm.jsx
│   │   ├── EventCard.jsx
│   │   └── LoadingSpinner.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   └── Results.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.jsx
│   └── index.js
├── public/
├── package.json
└── tailwind.config.js
```

**Dependencies:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0", 
    "react-router-dom": "^6.8.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.0"
  }
}
```

### **Task 5.2: API Service Layer**
**Acceptance Criteria:**
- [ ] `api.js` handles all backend communication
- [ ] Proper error handling for network failures
- [ ] Loading states managed consistently
- [ ] API base URL configurable via environment

---

## **Phase 6: User Interface**

### **Task 6.1: Search Interface**
**Acceptance Criteria:**
- [ ] Multi-line textarea for query input (min 3 rows)
- [ ] Submit button triggers search
- [ ] 3-5 example queries displayed below input
- [ ] Responsive design works on mobile
- [ ] Loading spinner during search

**Technical Details:**
```jsx
// Example queries to display:
const EXAMPLE_QUERIES = [
  "I love electronic music and want to dance all night",
  "Looking for creative workshops where I can make something",
  "Want to try unique food experiences and meet people", 
  "Interested in spiritual or wellness activities",
  "Comedy shows or entertaining performances"
];
```

### **Task 6.2: Results Display**
**Acceptance Criteria:**
- [ ] Event cards show: title, type, camp, times, description
- [ ] Clean, readable layout with proper spacing
- [ ] Links to camp URLs open in new tab
- [ ] "No results" state with helpful message
- [ ] Results load in <3 seconds

**Technical Details:**
```jsx
// EventCard component must include:
- Event type badge (colored by category)
- Camp name with clickable URL
- All event times displayed clearly  
- Full description text
- Clean typography with proper contrast
```

---

## **Phase 7: Integration & Polish**

### **Task 7.1: Frontend-Backend Integration**
**Acceptance Criteria:**
- [ ] Search form calls `/recommend` endpoint
- [ ] Results page displays API response data
- [ ] Error states handled gracefully
- [ ] Loading states provide feedback
- [ ] URL updates reflect search state

### **Task 7.2: Error Handling & UX**
**Acceptance Criteria:**
- [ ] Network errors show user-friendly message
- [ ] API errors display helpful guidance
- [ ] Empty query prevented with validation
- [ ] Form resets after successful search

---

## **Phase 8: Deployment Preparation**

### **Task 8.1: Production Configuration**
**Acceptance Criteria:**
- [ ] Environment variables for OpenAI API key
- [ ] Production-ready CORS settings
- [ ] Logging configuration
- [ ] Health check endpoint functional
- [ ] Static file serving configured

### **Task 8.2: Documentation**
**Acceptance Criteria:**
- [ ] README with setup instructions
- [ ] API documentation
- [ ] Environment variable documentation
- [ ] Deployment guide for common platforms

---

## **Acceptance Criteria Summary**

**Backend Success Metrics:**
- API responds in <2 seconds
- Memory usage <200MB  
- Handles 100 concurrent requests
- 99.9% uptime during testing

**Frontend Success Metrics:**
- Mobile responsive design
- Accessible (basic WCAG compliance)
- Fast loading (<3 seconds initial)
- Works in Chrome, Firefox, Safari

**Integration Success Metrics:**
- End-to-end search flow works
- Error handling covers edge cases
- No console errors in browser
- Semantic search returns relevant results

## **Technical Architecture**

### **Data Flow**
```
User Query → Frontend → Backend API → GPT-5 Embedding → FAISS Search → Results → Frontend
```

### **Technology Stack**
- **Backend**: Python 3.10+, FastAPI, FAISS, OpenAI SDK
- **Frontend**: React 18, Tailwind CSS, Axios
- **Data**: JSON file storage, NumPy arrays for embeddings
- **Deployment**: Standard web hosting (backend + static frontend)

### **Performance Targets**
- **Search Response Time**: <2 seconds end-to-end
- **Memory Usage**: <200MB backend, <50MB frontend
- **Concurrent Users**: 100+ simultaneous searches
- **Data Size**: 5K events max, ~30MB total memory footprint

This plan strictly follows YAGNI principles by building only the essential functionality: search input → AI recommendations → results display. No additional features beyond this core workflow are included.
