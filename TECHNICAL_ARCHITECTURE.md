# Technical Architecture & Implementation

## Overview: It's Not Just API Calls

While AcquiTalent AI uses API calls (Claude, scraping services), the **real sophistication** is in the **orchestration, data processing, and intelligent prompt engineering**. Here's what's actually happening under the hood:

---

## 🏗️ Architecture Layers

### 1. **Data Collection Layer** (Signal Fusion)

**Not just API calls** - Complex orchestration:

```python
# src/signal_fusion/engine.py
class SignalFusionEngine:
    def run_fusion(self, industry, role_level, min_score, limit):
        # 1. Multi-source signal collection
        raw_signals = self.collector.collect_all_signals(...)
        
        # 2. Intelligent deduplication & grouping
        candidates_with_signals = self._group_signals_by_candidate(raw_signals)
        
        # 3. Batch AI scoring with fallback logic
        scored_candidates = self.scorer.batch_score(candidates_with_signals)
        
        # 4. Filtering & database persistence
        high_score_candidates = [c for c in scored_candidates if score >= min_score]
        
        # 5. Transactional database operations
        for item in high_score_candidates:
            candidate = self._create_or_update_candidate(...)
            for signal in signals:
                self._create_signal(candidate.id, signal)
        
        return stored_candidates
```

**Key Technical Features:**
- **Deduplication Logic**: Groups signals by candidate (LinkedIn URL or email as key)
- **Data Normalization**: Handles inconsistent data formats from multiple sources
- **Transaction Management**: SQLAlchemy transactions ensure data consistency
- **Error Handling**: Fallback scoring if AI API fails

---

### 2. **AI Scoring Engine** (Prompt Engineering)

**Not just API calls** - Sophisticated prompt construction:

```python
# src/signal_fusion/scorer.py
def _build_scoring_prompt(self, candidate_data, signals):
    # Dynamic prompt construction based on:
    # - Candidate profile data
    # - Multiple signal sources
    # - Industry context
    # - Scoring guidelines
    
    prompt = f"""
    You are an expert executive recruiter analyzing passive interest signals...
    
    Scoring guidelines:
    - 0-30: Stable, no signals
    - 31-50: Some activity
    - 71-85: Strong signals, likely open
    - 86-100: Very strong signals
    
    Consider:
    1. Recency of signals
    2. Signal strength
    3. Signal diversity
    4. Industry context
    """
```

**Technical Sophistication:**
- **Context-Aware Prompting**: Builds prompts dynamically based on available data
- **JSON Parsing with Regex**: Extracts structured data from AI responses
- **Fallback Logic**: Heuristic scoring if AI fails (signal count * 15)
- **Confidence Scoring**: Returns both score and confidence level

**Response Parsing:**
```python
# Regex-based JSON extraction (handles AI formatting quirks)
json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
result = json.loads(json_match.group())
```

---

### 3. **Email Generation** (Advanced Prompt Engineering)

**Not just API calls** - Multi-context prompt building:

```python
# src/outreach/generator.py
def _build_email_prompt(self, candidate, job_opening, signals):
    # Combines:
    # - Candidate profile
    # - Job requirements
    # - Specific signals (top 3)
    # - Tone guidelines
    # - Format requirements
    
    prompt = f"""
    Write a personalized email that:
    1. References specific signals
    2. Mentions opportunity (if provided)
    3. Low-pressure ask
    4. Encourages reply
    
    Tone: Professional but warm
    Length: 4-6 sentences
    """
```

**Advanced Features:**
- **Signal Integration**: References specific signals in email
- **Multi-Format Parsing**: Handles different AI response formats
- **Markdown Cleaning**: Strips formatting for plain text emails
- **Fallback Templates**: Template-based emails if AI fails

---

### 4. **Database Architecture** (ORM + Relationships)

**Not just simple storage** - Complex relational model:

```python
# src/database/models.py
class Candidate(Base):
    # Primary entity
    id = Column(Integer, primary_key=True)
    openness_score = Column(Float)
    
    # Relationships (SQLAlchemy ORM)
    signals = relationship("Signal", back_populates="candidate", cascade="all, delete-orphan")
    outreach_campaigns = relationship("OutreachCampaign", back_populates="candidate")
    placements = relationship("Placement", back_populates="candidate")

class Signal(Base):
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    signal_data = Column(JSON)  # Flexible JSON storage for varied signal types
    
    candidate = relationship("Candidate", back_populates="signals")
```

**Technical Features:**
- **ORM (Object-Relational Mapping)**: SQLAlchemy for type-safe database access
- **Relationship Management**: Automatic foreign key handling
- **JSON Columns**: Flexible storage for varied signal data structures
- **Cascade Deletes**: Automatic cleanup of related records
- **Indexes**: Optimized queries on email, LinkedIn URL

**Query Patterns:**
```python
# Complex queries with filtering
candidates = db.query(Candidate).filter(
    Candidate.openness_score >= min_score,
    Candidate.status == "identified"
).order_by(Candidate.openness_score.desc()).limit(limit).all()
```

---

### 5. **API Layer** (RESTful + Dependency Injection)

**Not just endpoints** - Proper API design:

```python
# src/api/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

# Dependency injection for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/signal-fusion/run")
async def run_signal_fusion(
    request: SignalFusionRequest,
    db: Session = Depends(get_db)  # Injected dependency
):
    engine = SignalFusionEngine(db)
    candidates = engine.run_fusion(...)
    return {"candidates": candidates, "count": len(candidates)}
```

**Technical Features:**
- **Dependency Injection**: Clean separation of concerns
- **Pydantic Models**: Request/response validation
- **CORS Middleware**: Frontend integration
- **Error Handling**: HTTPException for proper status codes
- **Async Support**: FastAPI async/await for performance

---

### 6. **Frontend Architecture** (React + State Management)

**Not just UI** - Stateful React application:

```javascript
// frontend/src/App.jsx
function App() {
  // State management
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({ total: 0, avgScore: 0 })
  
  // Data fetching with error handling
  const loadCandidates = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/candidates?min_score=70`)
      setCandidates(response.data)
      calculateStats(response.data)
    } catch (error) {
      console.error('Error loading candidates:', error)
    } finally {
      setLoading(false)
    }
  }
  
  // Derived state calculation
  const calculateStats = (candidates) => {
    const total = candidates.length
    const avgScore = total > 0
      ? candidates.reduce((sum, c) => sum + c.openness_score, 0) / total
      : 0
    setStats({ total, avgScore: avgScore.toFixed(1) })
  }
}
```

**Technical Features:**
- **React Hooks**: useState, useEffect for state management
- **Axios**: HTTP client with interceptors
- **Derived State**: Calculated statistics from raw data
- **Error Handling**: Try/catch with user feedback
- **Loading States**: UX improvements during async operations
- **Tailwind CSS**: Utility-first styling

---

## 🔧 Core Technical Patterns

### 1. **Pipeline Architecture**

```
Raw Signals → Grouping → AI Scoring → Filtering → Database → API → Frontend
```

Each stage has:
- Error handling
- Fallback logic
- Data validation
- Logging

### 2. **Data Processing**

**Signal Grouping Algorithm:**
```python
def _group_signals_by_candidate(self, raw_signals):
    candidates_map = {}
    for signal in raw_signals:
        key = signal.get("linkedin_url") or signal.get("email")
        if key not in candidates_map:
            candidates_map[key] = {"candidate": {...}, "signals": []}
        candidates_map[key]["signals"].append(signal)
    return list(candidates_map.values())
```

**Features:**
- Deduplication by unique identifier
- Signal aggregation per candidate
- Handles missing data gracefully

### 3. **Error Handling & Resilience**

```python
# Multiple layers of error handling:

# 1. API call level
try:
    response = self.client.messages.create(...)
except Exception as e:
    return self._fallback_score(signals)

# 2. Parsing level
try:
    result = json.loads(json_match.group())
except:
    return fallback_result

# 3. Database level
try:
    self.db.commit()
except:
    self.db.rollback()
```

### 4. **Configuration Management**

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str = "sqlite:///./acquitalent.db"
    min_openness_score: int = 70
    
    class Config:
        env_file = ".env"
```

**Features:**
- Environment variable loading
- Type validation
- Default values
- Centralized configuration

---

## 📊 Data Flow Example

### Complete Flow: Finding a Candidate

1. **Signal Collection** (collectors.py)
   ```python
   # Multiple sources queried in parallel
   linkedin_signals = linkedin_collector.collect(...)
   podcast_signals = podcast_collector.collect(...)
   content_signals = content_collector.collect(...)
   ```

2. **Signal Fusion** (engine.py)
   ```python
   # Group by candidate (deduplication)
   candidates_map = group_signals_by_candidate(all_signals)
   ```

3. **AI Scoring** (scorer.py)
   ```python
   # For each candidate:
   prompt = build_scoring_prompt(candidate, signals)
   response = claude_api.messages.create(prompt)
   score = parse_response(response)
   ```

4. **Database Storage** (database.py)
   ```python
   # Transactional insert
   candidate = Candidate(...)
   db.add(candidate)
   for signal in signals:
       db.add(Signal(candidate_id=candidate.id, ...))
   db.commit()
   ```

5. **API Response** (main.py)
   ```python
   # Serialize to JSON
   return {"candidates": [...], "count": 50}
   ```

6. **Frontend Display** (App.jsx)
   ```javascript
   // React state update
   setCandidates(response.data.candidates)
   calculateStats(candidates)
   ```

---

## 🛠️ Technology Stack Deep Dive

### Backend
- **FastAPI**: Modern Python web framework (async support, automatic OpenAPI docs)
- **SQLAlchemy**: ORM for database abstraction
- **Pydantic**: Data validation and settings management
- **Anthropic SDK**: Claude API client

### Frontend
- **React 18**: Component-based UI library
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client library

### Database
- **SQLite** (MVP): File-based database
- **PostgreSQL** (Production): Ready for migration
- **Alembic**: Database migrations (ready to use)

### AI/ML
- **Claude 3.5 Sonnet**: Latest Anthropic model
- **Prompt Engineering**: Context-aware prompt construction
- **Response Parsing**: Regex + JSON extraction

---

## 🎯 What Makes This Sophisticated

### 1. **Not Just API Calls**
- **Orchestration**: Coordinates multiple data sources
- **Data Processing**: Normalization, deduplication, grouping
- **Error Handling**: Multi-layer fallback logic
- **State Management**: Database transactions, frontend state

### 2. **Intelligent Prompt Engineering**
- **Dynamic Prompts**: Built from multiple data sources
- **Context Injection**: Candidate info, signals, job requirements
- **Format Control**: Structured output parsing
- **Fallback Templates**: Graceful degradation

### 3. **Production-Ready Patterns**
- **Dependency Injection**: Clean architecture
- **Type Safety**: Pydantic models, SQLAlchemy types
- **Error Handling**: Try/catch at every layer
- **Logging**: Ready for production monitoring
- **Configuration**: Environment-based settings

### 4. **Scalability Considerations**
- **Batch Processing**: Scores multiple candidates efficiently
- **Database Indexing**: Optimized queries
- **Async Support**: FastAPI async endpoints
- **Caching Ready**: Can add Redis for signal caching

---

## 🔄 Comparison: Simple vs. This Implementation

### Simple (Just API Calls)
```python
# Naive approach
response = claude_api.call("Score this candidate")
print(response)
```

### This Implementation
```python
# Sophisticated approach
1. Collect signals from 5+ sources
2. Deduplicate and group by candidate
3. Build context-aware prompt with guidelines
4. Call AI with structured prompt
5. Parse response with error handling
6. Store in database with relationships
7. Filter by score threshold
8. Return via REST API
9. Display in React with state management
```

---

## 📈 Performance Optimizations

1. **Batch Processing**: Scores multiple candidates in one loop
2. **Database Indexing**: Fast queries on email, LinkedIn URL
3. **Lazy Loading**: SQLAlchemy relationships loaded on demand
4. **Frontend Memoization**: Ready for React.memo if needed
5. **API Caching**: Can add Redis layer for signal caching

---

## 🚀 Future Enhancements (Architecture Ready)

- **Background Jobs**: Celery for async signal collection
- **Caching Layer**: Redis for frequently accessed data
- **Message Queue**: RabbitMQ for email sending
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging with ELK stack

---

## Summary

**It's not just API calls** - it's a **sophisticated data processing pipeline** with:

- ✅ Multi-source data collection and fusion
- ✅ Intelligent prompt engineering
- ✅ Complex database relationships
- ✅ Error handling and fallbacks
- ✅ RESTful API design
- ✅ Modern React frontend
- ✅ Production-ready patterns

The **real value** is in the **orchestration and intelligence** that makes the AI calls meaningful and reliable.

