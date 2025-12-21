# AcquiTalent AI - Quick Start Guide 🚀

## Setup (5 minutes)

### 1. Install Dependencies

```bash
cd acquitalent-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys:
# - ANTHROPIC_API_KEY (required for AI scoring & email generation)
# - APIFY_API_TOKEN (optional, for LinkedIn scraping)
# - INSTANTLY_API_KEY (optional, for email sending)
```

**Minimum required**: `ANTHROPIC_API_KEY` from Anthropic (get at https://console.anthropic.com)

### 3. Initialize Database

```bash
python scripts/init_db.py
```

### 4. Start the Application

**Terminal 1 - Backend API:**
```bash
python main.py
# API runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:3000
```

## Week 1: Manual Validation

Before automating, validate the concept manually:

```bash
# Find 10 VP Engineering candidates in fintech
python scripts/manual_validation.py --industry "fintech" --role "VP Engineering" --limit 10
```

This will:
1. Run signal fusion (currently returns empty - you need to implement data collectors)
2. Generate personalized outreach emails
3. Show you candidates with their contact info

**Target**: Get 3+ positive replies (30%+ reply rate) before automating.

## Week 2-4: Implement Data Collectors

The signal collectors are stubbed out. You need to implement:

1. **LinkedIn Collector** (`src/signal_fusion/collectors.py`):
   - Integrate Apify LinkedIn scraper
   - Or use PhantomBuster API
   - Detect job changes in network

2. **Podcast Collector**:
   - Use Listen Notes API or Podchaser
   - Scrape podcast transcripts
   - Look for "what's next" language

3. **Content Collector**:
   - Scrape Substack/Medium for thought leaders
   - Twitter API for follows/engagement

4. **Conference Collector**:
   - Scrape conference websites
   - Event databases (Eventbrite, etc.)

## Using the API

### Run Signal Fusion

```bash
# Via script
python scripts/run_signal_fusion.py --industry "fintech" --role-level "VP" --limit 50

# Via API
curl -X POST http://localhost:8000/api/signal-fusion/run \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "fintech",
    "role_level": "VP",
    "min_score": 70,
    "limit": 50
  }'
```

### Generate Outreach

```bash
# Generate for specific candidate
python scripts/generate_outreach.py --candidate-id 1

# Generate for all high-score candidates
python scripts/generate_outreach.py --batch --min-score 70
```

### View Candidates

```bash
# Via API
curl http://localhost:8000/api/candidates?min_score=70
```

## Next Steps

1. ✅ **Week 1**: Manual validation (find 10, get 3+ replies)
2. 🔨 **Week 2-4**: Implement data collectors
3. 📧 **Week 3-4**: Set up email automation (Instantly.ai)
4. 🤝 **Week 5-6**: Land 3 pilot clients
5. 💰 **Week 7-10**: Close first $50k deal

## Troubleshooting

### "No candidates found"
- Data collectors are stubbed - you need to implement them
- Check API keys in `.env`
- Verify database is initialized

### "Claude API error"
- Check `ANTHROPIC_API_KEY` in `.env`
- Verify API key is valid at https://console.anthropic.com

### Frontend not loading
- Make sure backend is running on port 8000
- Check browser console for errors
- Verify CORS settings in `src/api/main.py`

## Project Structure

```
acquitalent-ai/
├── src/
│   ├── signal_fusion/    # Signal collection & AI scoring
│   ├── outreach/         # Email generation
│   ├── database/         # Models & DB connection
│   └── api/              # FastAPI endpoints
├── frontend/             # React dashboard
├── scripts/               # Utility scripts
└── main.py               # Entry point
```

## Support

For issues or questions, check:
- README.md for full documentation
- Code comments for implementation details
- TODO comments for integration points

