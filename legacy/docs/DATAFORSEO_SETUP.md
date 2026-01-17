# DataForSEO Integration Setup

## ✅ Integration Complete!

DataForSEO has been integrated into the website discovery system. The system will now:

1. **Use DataForSEO SERP API** for website discovery (if configured)
2. **Fallback to DuckDuckGo** if DataForSEO is not available
3. **Get quality metrics** (rank, traffic estimates) with search results

## 🔑 Add Credentials to .env

Add these lines to your `.env` file:

```bash
DATAFORSEO_LOGIN=jeremiah@liquidcanvas.art
DATAFORSEO_PASSWORD=b85d55cf567939e7
```

## 📊 What DataForSEO Provides

### 1. **Better Search Results**
- Real Google SERP data (not just DuckDuckGo)
- Includes rank position
- Traffic estimates (ETV - Estimated Traffic Value)
- More accurate results

### 2. **Quality Metrics** (Available via API)
- Domain Authority
- Page Authority  
- Backlinks count
- Spam score
- Referring domains

## 🚀 How It Works

### **Discovery Process:**
```
1. Check if DataForSEO is configured
2. If YES → Use DataForSEO SERP API
   - Get Google search results
   - Include quality metrics
   - Filter by location
3. If NO → Fallback to DuckDuckGo (free)
```

### **Location Mapping:**
- USA → Location Code 2840
- Canada → Location Code 2124
- UK/London → Location Code 2826
- Germany → Location Code 2276
- France → Location Code 2250

## 📝 Next Steps

1. **Add credentials to .env** (see above)
2. **Restart the backend** to load new credentials
3. **Run a discovery** - it will automatically use DataForSEO
4. **Check logs** - you'll see "Using DataForSEO API for website discovery"

## 🔍 Testing

After adding credentials, you can test by:
1. Triggering a manual search from the dashboard
2. Checking the logs for "Using DataForSEO API"
3. Verifying results include rank and metrics

## ⚠️ API Limits

DataForSEO has API rate limits based on your plan. The system:
- Uses 2-second delay between queries (vs 1 second for DuckDuckGo)
- Limits to 15 queries per run
- Will fallback to DuckDuckGo if API limit is reached

## 🎯 Benefits

✅ **Higher quality results** - Real Google SERP data
✅ **Better targeting** - Location-specific searches
✅ **Quality metrics** - Rank, traffic estimates included
✅ **Automatic fallback** - Still works if API unavailable

