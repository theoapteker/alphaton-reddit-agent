# n8n Connection Guide for Reddit Sentiment MCP Server

## Your Server Details

**Local Server:** http://localhost:8000
**Public URL (ngrok):** https://dirk-intrinsic-echoingly.ngrok-free.dev
**Health Check:** https://dirk-intrinsic-echoingly.ngrok-free.dev/health

## Quick Start

### 1. Verify Server is Running

Test your public URL in a browser or with curl:
```bash
curl https://dirk-intrinsic-echoingly.ngrok-free.dev/health
```

Expected response:
```json
{
    "status": "healthy",
    "timestamp": "2025-11-11T04:02:36.358971",
    "reddit_connected": true,
    "finter_connected": true
}
```

### 2. Available MCP Tools

Your server exposes 4 tools for the Reddit → Sentiment → Alpha workflow:

| Tool | Endpoint | Method |
|------|----------|--------|
| Scrape Reddit | `/tools/scrape_reddit` | POST |
| Analyze Sentiment | `/tools/analyze_sentiment` | POST |
| Generate Alpha | `/tools/generate_alpha` | POST |
| Submit to FINTER | `/tools/submit_to_finter` | POST |

---

## n8n Workflow Setup

### Workflow 1: Complete Reddit → Alpha Pipeline

This workflow scrapes Reddit, analyzes sentiment, and generates alpha signals.

#### Node 1: Schedule Trigger (Optional)
- **Node Type:** Schedule Trigger
- **Schedule:** Every day at 9:00 AM
- **Purpose:** Automate daily analysis

#### Node 2: Scrape Reddit
- **Node Type:** HTTP Request
- **Method:** POST
- **URL:** `https://dirk-intrinsic-echoingly.ngrok-free.dev/tools/scrape_reddit`
- **Headers:**
  ```
  Content-Type: application/json
  ngrok-skip-browser-warning: true
  User-Agent: Mozilla/5.0
  ```
  **Note:** The ngrok headers are required for free tier ngrok URLs
- **Body (JSON):**
  ```json
  {
    "start_date": "20241104",
    "end_date": "20241111",
    "subreddit": "wallstreetbets"
  }
  ```
- **Expected Response:**
  ```json
  {
    "status": "success",
    "records": 150,
    "date_range": "20241104 to 20241111",
    "subreddit": "wallstreetbets",
    "data": [
      {
        "ticker": "AAPL",
        "date": "2024-11-10",
        "score": 100,
        "text": "AAPL is going to the moon!",
        "post_id": "abc123"
      }
    ]
  }
  ```

#### Node 3: Analyze Sentiment
- **Node Type:** HTTP Request
- **Method:** POST
- **URL:** `https://dirk-intrinsic-echoingly.ngrok-free.dev/tools/analyze_sentiment`
- **Headers:**
  ```
  Content-Type: application/json
  ngrok-skip-browser-warning: true
  User-Agent: Mozilla/5.0
  ```
  **Note:** The ngrok headers are required for free tier ngrok URLs
- **Body (JSON - using data from Node 2):**
  ```json
  {
    "mentions_data": {{$json["data"]}}
  }
  ```
- **Expected Response:**
  ```json
  {
    "status": "success",
    "records": 120,
    "gvkeyiid_mapped": 45,
    "data": [
      {
        "gvkeyiid": "000169001",
        "date": "2024-11-10",
        "sentiment": 0.75,
        "mention_count": 5,
        "ticker": "AAPL"
      }
    ]
  }
  ```

#### Node 4: Generate Alpha
- **Node Type:** HTTP Request
- **Method:** POST
- **URL:** `https://dirk-intrinsic-echoingly.ngrok-free.dev/tools/generate_alpha`
- **Headers:**
  ```
  Content-Type: application/json
  ngrok-skip-browser-warning: true
  User-Agent: Mozilla/5.0
  ```
  **Note:** The ngrok headers are required for free tier ngrok URLs
- **Body (JSON - using data from Node 3):**
  ```json
  {
    "sentiment_data": {{$json["data"]}},
    "start_date": "20241104",
    "end_date": "20241111",
    "leverage": 1.0
  }
  ```
- **Expected Response:**
  ```json
  {
    "status": "success",
    "validation_passed": true,
    "validation_details": {
      "passed": true,
      "checks": {
        "has_gvkeyiid": true,
        "has_dates": true,
        "max_position_ok": true
      }
    },
    "position_shape": [7, 45],
    "position_json": "..."
  }
  ```

#### Node 5: Send Email/Notification (Optional)
- **Node Type:** Send Email / Slack / Discord
- **Content:** Results from Node 4
- **Purpose:** Notify when alpha generation completes

---

## Testing Your Connection

### Test 1: Health Check
```bash
curl https://dirk-intrinsic-echoingly.ngrok-free.dev/health
```

### Test 2: Scrape Reddit (7 days)
```bash
curl -X POST https://dirk-intrinsic-echoingly.ngrok-free.dev/tools/scrape_reddit \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "20241104",
    "end_date": "20241111",
    "subreddit": "wallstreetbets"
  }'
```

### Test 3: Analyze Sentiment (Mock Data)
```bash
curl -X POST https://dirk-intrinsic-echoingly.ngrok-free.dev/tools/analyze_sentiment \
  -H "Content-Type: application/json" \
  -d '{
    "mentions_data": [
      {
        "ticker": "AAPL",
        "date": "2024-11-10",
        "score": 100,
        "text": "AAPL is amazing!",
        "post_id": "test1"
      },
      {
        "ticker": "TSLA",
        "date": "2024-11-10",
        "score": 50,
        "text": "TSLA is crashing",
        "post_id": "test2"
      }
    ]
  }'
```

---

## Supported Tickers (50 stocks)

The system now uses hardcoded mappings for these 50 popular stocks:

**Tech:** AAPL, MSFT, GOOGL, META, NVDA, AMD, INTC, ORCL, CRM, TSLA, UBER, NFLX, AVGO, QCOM, TXN, LRCX, ASML

**Finance:** JPM, BAC, WFC, V, MA

**Consumer:** AMZN, WMT, COST, HD, NKE, MCD, PG, PEP, KO, DIS

**Healthcare:** JNJ, UNH, LLY, ABBV, TMO, AMGN, MRK

**Energy:** XOM, CVX

**Industrial:** HON, CAT, GE

**Telecom:** T

**Other:** BRK.B, LIN, ANET, BABA, IBM

Any ticker not in this list will be filtered out during sentiment analysis.

---

## Environment Variables (Required)

Make sure your local server has these environment variables set in `.env`:

```bash
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password

# FINTER API (if using submit_to_finter)
FINTER_API_KEY=your_finter_api_key
```

---

## Troubleshooting

### Issue: "Connection Refused"
- **Solution:** Make sure both your local server AND ngrok are running
  ```bash
  # Terminal 1
  source venv/bin/activate
  python src/mcp_server.py

  # Terminal 2
  ngrok http 8000
  ```

### Issue: "404 Not Found"
- **Solution:** Check the endpoint URL - make sure you're using the correct path
  - ✅ Correct: `/tools/scrape_reddit`
  - ❌ Wrong: `/scrape_reddit`

### Issue: "Ticker not mapped"
- **Solution:** Only the 50 hardcoded tickers are supported. Check the list above.

### Issue: ngrok URL changes every restart
- **Solution:**
  - Free ngrok accounts get new URLs each time
  - Upgrade to ngrok paid plan for permanent URLs
  - Or deploy to a cloud service (Heroku, Railway, Render)

### Issue: "FINTER authentication failed"
- **Solution:** Add your FINTER API key to `.env` file

---

## API Documentation

View interactive API documentation at:
- **Swagger UI:** https://dirk-intrinsic-echoingly.ngrok-free.dev/docs
- **ReDoc:** https://dirk-intrinsic-echoingly.ngrok-free.dev/redoc

---

## Production Deployment (Optional)

For a permanent solution instead of ngrok:

### Option 1: Heroku
```bash
heroku login
heroku create reddit-sentiment-mcp
git push heroku main
```

### Option 2: Railway
1. Connect GitHub repo to Railway
2. Auto-deploy on push
3. Get permanent URL: `https://your-app.railway.app`

### Option 3: University Server
Ask your professor if they can host the MCP server on the same infrastructure as n8n.

---

## Example n8n Workflow JSON

Save this as a `.json` file and import into n8n:

```json
{
  "name": "Reddit Sentiment Alpha Pipeline",
  "nodes": [
    {
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300],
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "days",
              "daysInterval": 1
            }
          ]
        }
      }
    },
    {
      "name": "Scrape Reddit",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "url": "https://dirk-intrinsic-echoingly.ngrok-free.dev/tools/scrape_reddit",
        "method": "POST",
        "jsonParameters": true,
        "options": {},
        "bodyParametersJson": "={\n  \"start_date\": \"{{ $now.minus({days: 7}).toFormat('yyyyMMdd') }}\",\n  \"end_date\": \"{{ $now.toFormat('yyyyMMdd') }}\",\n  \"subreddit\": \"wallstreetbets\"\n}"
      }
    },
    {
      "name": "Analyze Sentiment",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 300],
      "parameters": {
        "url": "https://dirk-intrinsic-echoingly.ngrok-free.dev/tools/analyze_sentiment",
        "method": "POST",
        "jsonParameters": true,
        "bodyParametersJson": "={{ { \"mentions_data\": $json.data } }}"
      }
    },
    {
      "name": "Generate Alpha",
      "type": "n8n-nodes-base.httpRequest",
      "position": [850, 300],
      "parameters": {
        "url": "https://dirk-intrinsic-echoingly.ngrok-free.dev/tools/generate_alpha",
        "method": "POST",
        "jsonParameters": true,
        "bodyParametersJson": "={{ {\n  \"sentiment_data\": $json.data,\n  \"start_date\": $now.minus({days: 7}).toFormat('yyyyMMdd'),\n  \"end_date\": $now.toFormat('yyyyMMdd'),\n  \"leverage\": 1.0\n} }}"
      }
    }
  ],
  "connections": {
    "Schedule": {
      "main": [
        [
          {
            "node": "Scrape Reddit",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Scrape Reddit": {
      "main": [
        [
          {
            "node": "Analyze Sentiment",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Analyze Sentiment": {
      "main": [
        [
          {
            "node": "Generate Alpha",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## Support

If you encounter issues:
1. Check the server logs: Look at the terminal where `python src/mcp_server.py` is running
2. Test endpoints with curl commands above
3. Verify ngrok is still running (free tier times out after 2 hours)
4. Check environment variables are set correctly

**Server Status:** Your server is currently running at `https://dirk-intrinsic-echoingly.ngrok-free.dev`

**Last Updated:** 2025-11-11
