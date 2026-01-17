# Phase 4 Complete - Scoring Algorithm

## ✅ What's Been Built

### 1. Scoring Service (`worker/services/scoring.py`)
- `ProspectScorer` class with configurable weights
- Multi-factor scoring algorithm
- Factors considered:
  - **Domain Authority** (30% weight) - From DataForSEO or estimated
  - **Email Presence** (25% weight) - Has contact email or not
  - **Email Confidence** (15% weight) - Hunter.io confidence score
  - **Topical Relevance** (15% weight) - Keyword matching
  - **Data Quality** (10% weight) - Completeness of data
  - **Recency** (5% weight) - How recent the prospect is

### 2. Scoring Task (`worker/tasks/scoring.py`)
- RQ task that processes scoring jobs
- Calculates scores for all prospects (or specified ones)
- Updates prospect records with new scores
- Updates job status

### 3. Backend Integration
- New endpoint: `POST /api/jobs/score` to queue scoring jobs
- Prospects automatically sorted by score in list endpoint

### 4. Worker Updates
- Worker now listens to `discovery`, `enrichment`, and `scoring` queues

## 🎯 Scoring Algorithm Details

### Score Calculation
```
Final Score = Σ (Factor Score × Weight)

Factors:
- Domain Authority: 0-100 (30% weight)
- Has Email: 0 or 100 (25% weight)
- Email Confidence: 0-100 (15% weight)
- Topical Relevance: 0-100 (15% weight)
- Data Quality: 0-100 (10% weight)
- Recency: 0-100 (5% weight)
```

### Example Score Calculation
```
Prospect with:
- DA: 60
- Has Email: Yes
- Email Confidence: 80
- Relevance: 70
- Data Quality: 90
- Recency: 100

Score = (60 × 0.30) + (100 × 0.25) + (80 × 0.15) + 
        (70 × 0.15) + (90 × 0.10) + (100 × 0.05)
      = 18 + 25 + 12 + 10.5 + 9 + 5
      = 79.5
```

## 🔄 How It Works

1. **User creates scoring job** via `POST /api/jobs/score`
   - Can specify specific prospect IDs or score all prospects
2. **Backend creates Job record** in database
3. **Backend queues RQ task** to Redis `scoring` queue
4. **Worker picks up task** and calls `score_prospects_task(job_id)`
5. **Task processes job**:
   - Fetches prospects to score
   - Calculates score for each using `ProspectScorer`
   - Updates prospect records
   - Updates job status

## 📊 Scoring Factors Explained

### Domain Authority (30%)
- From DataForSEO metrics if available
- Estimated from backlinks if no direct DA
- Default: 20 if no data

### Email Presence (25%)
- 100 if prospect has contact email
- 0 if no email

### Email Confidence (15%)
- From Hunter.io confidence score (0-100)
- Default: 50 if email exists but no confidence data
- 0 if no email

### Topical Relevance (15%)
- Based on keyword matching in page title/URL
- Matches category keywords
- Score: 50-100 based on match ratio

### Data Quality (10%)
- Based on available data fields
- Factors: title, URL, DataForSEO payload, Hunter.io payload
- More complete data = higher score

### Recency (5%)
- Currently all prospects get 100 (can be enhanced)
- Could factor in creation date

## 📁 Project Structure

```
worker/
├── services/
│   └── scoring.py         ✅ NEW - Scoring service
├── tasks/
│   ├── discovery.py        ✅
│   ├── enrichment.py      ✅
│   └── scoring.py         ✅ NEW - Scoring task
└── worker.py              ✅ Updated
```

## 🚀 Next Steps

**Phase 5**: Implement Gemini compose endpoint
- Generate email content using Google Gemini
- Save drafts to database
- Allow manual review/editing

## ⚙️ Configuration

Scoring weights can be adjusted in `ProspectScorer.WEIGHTS`:
```python
WEIGHTS = {
    "domain_authority": 0.30,
    "has_email": 0.25,
    "email_confidence": 0.15,
    "topical_relevance": 0.15,
    "data_quality": 0.10,
    "recency": 0.05
}
```

## 🧪 Testing

To test locally:
1. Ensure prospects exist (from discovery + enrichment)
2. Start worker: `cd worker && python worker.py`
3. Create scoring job: `POST /api/jobs/score`
4. Watch worker process the job
5. Check prospects: `GET /api/prospects` (sorted by score)

