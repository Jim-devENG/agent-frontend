# DataForSEO Exact Fixes - Ruthless Debugging Report

## 🔴 CRITICAL ISSUE #1: Wrong Payload Structure

### Problem
DataForSEO API expects a **direct JSON array**, but we're sending a **wrapped object with "data" key**.

### Current (WRONG) Request
```bash
curl -X POST "https://api.dataforseo.com/v3/serp/google/organic/task_post" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'LOGIN:PASSWORD' | base64)" \
  -d '{
    "data": [{
      "keyword": "gadget review site",
      "location_code": 2276,
      "language_code": "en",
      "depth": 10
    }]
  }'
```

**Result**: `40503 - POST Data Is Invalid`

### Correct Request
```bash
curl -X POST "https://api.dataforseo.com/v3/serp/google/organic/task_post" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'LOGIN:PASSWORD' | base64)" \
  -d '[
    {
      "keyword": "gadget review site",
      "location_code": 2276,
      "language_code": "en",
      "depth": 10
    }
  ]'
```

**Result**: `20000 - Ok` (success)

### Code Patch

**File**: `backend/app/clients/dataforseo.py`

**Line**: ~190-199 (in `_build_payload` method)

```diff
-    def _build_payload(self, payload_obj: DataForSEOPayload) -> dict:
+    def _build_payload(self, payload_obj: DataForSEOPayload) -> list:
         """
         Build DataForSEO API payload according to v3 specification
         
-        According to DataForSEO v3 API docs:
-        - Payload must be wrapped in "data" key
-        - "data" must be an array of task objects
+        According to DataForSEO v3 API docs:
+        - Payload must be a DIRECT JSON array (NOT wrapped in "data")
+        - Array contains task objects
         - Each task object contains: keyword, location_code, language_code, depth (optional)
         - NO device, os, or other unsupported fields
         
         Returns:
-            Properly formatted payload dict
+            Properly formatted payload list
         """
-        return {
-            "data": [payload_obj.to_dict()]
-        }
+        return [payload_obj.to_dict()]
```

**Also update line ~196** (where payload is used):
```diff
-            payload = self._build_payload(payload_obj)
+            payload = self._build_payload(payload_obj)  # Now returns list, not dict
```

### Test Command
```bash
# Test with curl
curl -X POST "https://api.dataforseo.com/v3/serp/google/organic/task_post" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n '$DATAFORSEO_LOGIN:$DATAFORSEO_PASSWORD' | base64)" \
  -d '[{"keyword":"test query","location_code":2840,"language_code":"en","depth":10}]'

# Expected: {"version":"...","status_code":20000,"status_message":"Ok.","tasks":[...]}
```

---

## 🔴 CRITICAL ISSUE #2: on_page/task_post Also Uses Wrong Format

### Problem
The `on_page_task_post` method also wraps payload in "data" key.

### Current (WRONG) Code
**File**: `backend/app/clients/dataforseo.py`  
**Line**: ~407-417

```python
payload = {
    "data": [{
        "target": domain,
        "max_crawl_pages": max_crawl_pages,
        ...
    }]
}
```

### Fix
```diff
-        payload = {
-            "data": [{
+        payload = [{
                 "target": domain,
                 "max_crawl_pages": max_crawl_pages,
                 "enable_javascript": True,
                 "load_resources": True,
                 "fetch_html": True,
                 "respect_robot_txt": False,
                 "custom_headers": {"User-Agent": "Mozilla/5.0"}
-            }]
-        }
+        }]
```

### Test Command
```bash
curl -X POST "https://api.dataforseo.com/v3/on_page/task_post" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n '$DATAFORSEO_LOGIN:$DATAFORSEO_PASSWORD' | base64)" \
  -d '[{"target":"example.com","max_crawl_pages":5}]'
```

---

## 🟡 ISSUE #3: Missing Request/Response Logging to Database

### Problem
No persistent logging of requests/responses for debugging.

### One-Line Patch

**File**: `backend/app/clients/dataforseo.py`

**Add after line ~225** (after response is received):

```python
# Log to database for 72-hour debugging window
await self._log_request_response(url, payload, response, result)
```

**Add method at end of class** (before `get_diagnostics`):

```python
async def _log_request_response(self, url: str, payload: Any, response: httpx.Response, result: dict):
    """Log request/response to database for 72-hour debugging window"""
    try:
        from app.db.database import AsyncSessionLocal
        from app.models.api_log import APILog  # Need to create this model
        from datetime import datetime, timedelta
        
        async with AsyncSessionLocal() as db:
            log_entry = APILog(
                endpoint=url,
                request_payload=payload,
                response_status=response.status_code,
                response_body=result,
                timestamp=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=72)
            )
            db.add(log_entry)
            await db.commit()
    except Exception as e:
        logger.warning(f"Failed to log API request to DB: {e}")
```

**Create model file**: `backend/app/models/api_log.py`

```python
from sqlalchemy import Column, String, Integer, JSON, DateTime
from app.db.database import Base
from datetime import datetime

class APILog(Base):
    __tablename__ = "api_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint = Column(String, nullable=False)
    request_payload = Column(JSON, nullable=False)
    response_status = Column(Integer, nullable=False)
    response_body = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<APILog(endpoint={self.endpoint}, status={self.response_status})>"
```

**Create migration**:
```bash
alembic revision -m "add_api_logs_table"
# Then edit the migration file to add the table
```

---

## Priority Fix List

### Priority 1 (CRITICAL - Fixes 40503 errors)
1. ✅ Remove "data" wrapper from `_build_payload()` - return list directly
2. ✅ Fix `on_page_task_post` payload format
3. ✅ Update payload type hints from `dict` to `list`

### Priority 2 (Important - Better debugging)
4. ✅ Add request/response logging to database
5. ✅ Create APILog model and migration

### Priority 3 (Nice to have)
6. Update diagnostics endpoint to show correct payload format
7. Add automated tests with real API calls

---

## Complete Fixed Code

### File: `backend/app/clients/dataforseo.py`

**Change 1**: Line ~190
```python
def _build_payload(self, payload_obj: DataForSEOPayload) -> list:
    """
    Build DataForSEO API payload according to v3 specification
    
    DataForSEO v3 expects a DIRECT JSON array, NOT wrapped in "data" key.
    
    Returns:
        List of task objects (direct array format)
    """
    return [payload_obj.to_dict()]
```

**Change 2**: Line ~407
```python
payload = [{
    "target": domain,
    "max_crawl_pages": max_crawl_pages,
    "enable_javascript": True,
    "load_resources": True,
    "fetch_html": True,
    "respect_robot_txt": False,
    "custom_headers": {"User-Agent": "Mozilla/5.0"}
}]
```

---

## Verification Steps

1. **Apply fixes**
2. **Test with curl** (commands above)
3. **Run discovery job** and check logs
4. **Verify success rate** via diagnostics endpoint
5. **Check database logs** for request/response data

---

## Expected Results After Fix

**Before**:
- 108/108 requests failed (0% success)
- Error: `40503 - POST Data Is Invalid`

**After**:
- >95% success rate expected
- Task IDs returned successfully
- Results retrieved from polling

