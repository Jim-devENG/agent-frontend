# Discovery Job Endless Run Fixes

## Problem
Discovery jobs were running endlessly without timeout or cancellation mechanisms.

## Solutions Implemented

### 1. **Timeout Protection** ✅
- Added 2-hour maximum execution time for discovery jobs
- Job automatically stops and marks as "failed" if it exceeds the timeout
- Timeout checks occur:
  - Before processing each location
  - Before processing each query
  - Allows graceful shutdown with partial results saved

**Location**: `backend/app/tasks/discovery.py`
- Line 108: Records start time
- Line 112: Sets MAX_EXECUTION_TIME = 2 hours
- Lines 173-179: Timeout check before each location
- Lines 195-201: Timeout check before each query

### 2. **Job Cancellation Endpoint** ✅
- New endpoint: `POST /api/jobs/{job_id}/cancel`
- Allows users to manually cancel running or pending jobs
- Discovery task checks cancellation status during execution
- Cancelled jobs stop processing immediately

**Location**: `backend/app/api/jobs.py`
- Lines 330-360: Cancel endpoint implementation

### 3. **Concurrent Job Prevention** ✅
- Prevents starting a new discovery job if one is already running
- Automatically detects and marks stuck jobs (>2 hours) as failed
- Returns clear error message if user tries to start concurrent job

**Location**: `backend/app/api/jobs.py`
- Lines 107-130: Concurrent job check and stuck job detection

### 4. **Cancellation Checks During Execution** ✅
- Discovery task checks job status periodically
- If job is marked as "cancelled", execution stops immediately
- Status checks occur:
  - Before processing each location
  - Before processing each query

**Location**: `backend/app/tasks/discovery.py`
- Lines 101-104: Initial cancellation check
- Lines 182-185: Cancellation check before each location
- Lines 203-206: Cancellation check before each query

## How to Use

### Cancel a Running Job
```bash
POST /api/jobs/{job_id}/cancel
```

**Response:**
```json
{
  "message": "Job cancelled successfully",
  "job_id": "uuid-here",
  "status": "cancelled"
}
```

### Check Job Status
```bash
GET /api/jobs/{job_id}/status
```

### List All Jobs
```bash
GET /api/jobs?skip=0&limit=50
```

## Automatic Protection

1. **Stuck Job Detection**: If a job has been "running" for >2 hours, it's automatically marked as "failed" when a new job is attempted
2. **Timeout Protection**: Jobs automatically stop after 2 hours of execution
3. **Concurrent Prevention**: Only one discovery job can run at a time

## Testing

To test cancellation:
1. Start a discovery job
2. Note the job ID from the response
3. Call `POST /api/jobs/{job_id}/cancel`
4. Verify the job status changes to "cancelled"
5. Check logs to confirm processing stopped

## Notes

- Timeout is set to 2 hours (configurable via `MAX_EXECUTION_TIME`)
- Cancellation is checked at strategic points to minimize delay
- Partial results are saved even if job is cancelled or times out
- All changes are committed to database before stopping

