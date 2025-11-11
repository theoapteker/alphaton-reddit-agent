# Quick Start Guide: Connect to Online n8n

## Step-by-Step Instructions

### Step 1: Start Your Local MCP Server

Open a terminal and run:

```bash
./start_server.sh
```

You should see:
```
🚀 Starting MCP server on http://localhost:8000...
```

**Keep this terminal open!** Your server needs to keep running.

---

### Step 2: Start ngrok (in a NEW terminal)

Open a **second terminal** and run:

```bash
ngrok http 8000
```

You'll see output like this:
```
Session Status                online
Forwarding                    https://abc-xyz-123.ngrok-free.dev -> http://localhost:8000
```

**Copy the HTTPS URL** (the one that starts with `https://`)

**Important Notes:**
- Free ngrok URLs change every time you restart ngrok
- ngrok sessions expire after 2 hours on the free tier
- **Keep this terminal open too!**

---

### Step 3: Test Your Public URL

In a **third terminal** (or your browser), test the health endpoint:

```bash
curl -H "ngrok-skip-browser-warning: true" https://YOUR-NGROK-URL/health
```

Replace `YOUR-NGROK-URL` with your actual ngrok URL.

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-11T04:02:36",
  "reddit_connected": true,
  "finter_connected": true
}
```

---

### Step 4: Configure n8n

In your professor's n8n instance:

#### Create HTTP Request Node

1. **Node Type:** HTTP Request
2. **Method:** POST
3. **URL:** `https://YOUR-NGROK-URL/tools/scrape_reddit`
4. **Headers:** Add these 3 headers:
   - `Content-Type`: `application/json`
   - `ngrok-skip-browser-warning`: `true`
   - `User-Agent`: `Mozilla/5.0`

5. **Body (JSON):**
```json
{
  "start_date": "20241104",
  "end_date": "20241111",
  "subreddit": "wallstreetbets"
}
```

#### Test the Node

Click "Execute Node" in n8n. You should see a successful response with Reddit data.

---

## Available Endpoints

Once your server and ngrok are running, these endpoints are available:

### 1. Health Check
```
GET https://YOUR-NGROK-URL/health
```

### 2. Scrape Reddit
```
POST https://YOUR-NGROK-URL/tools/scrape_reddit

Body:
{
  "start_date": "20241104",
  "end_date": "20241111",
  "subreddit": "wallstreetbets"
}
```

### 3. Analyze Sentiment
```
POST https://YOUR-NGROK-URL/tools/analyze_sentiment

Body:
{
  "mentions_data": [ ... array from step 2 ... ]
}
```

### 4. Generate Alpha
```
POST https://YOUR-NGROK-URL/tools/generate_alpha

Body:
{
  "sentiment_data": [ ... array from step 3 ... ],
  "start_date": "20241104",
  "end_date": "20241111",
  "leverage": 1.0
}
```

---

## Troubleshooting

### "Connection Refused"
- Make sure **both** terminals are running (server AND ngrok)
- Check that ngrok is forwarding to port 8000

### "403 Access Denied" from ngrok
- Make sure you're including the headers in n8n:
  - `ngrok-skip-browser-warning: true`
  - `User-Agent: Mozilla/5.0`

### "Ticker not mapped"
- Only 50 hardcoded tickers are supported (AAPL, TSLA, NVDA, etc.)
- See N8N_CONNECTION_GUIDE.md for the full list

### ngrok URL keeps changing
- This is normal for free tier
- Upgrade to ngrok paid plan for permanent URL
- Or deploy to cloud (Heroku, Railway, Render)

---

## Complete n8n Workflow Example

Here's a simple 3-node workflow:

**Node 1: Scrape Reddit**
- Type: HTTP Request
- URL: `https://YOUR-NGROK-URL/tools/scrape_reddit`
- Method: POST
- Headers: (see above)
- Body: `{"start_date": "20241104", "end_date": "20241111", "subreddit": "wallstreetbets"}`

**Node 2: Analyze Sentiment**
- Type: HTTP Request
- URL: `https://YOUR-NGROK-URL/tools/analyze_sentiment`
- Method: POST
- Headers: (see above)
- Body: `{"mentions_data": {{$json["data"]}}}`

**Node 3: Generate Alpha**
- Type: HTTP Request
- URL: `https://YOUR-NGROK-URL/tools/generate_alpha`
- Method: POST
- Headers: (see above)
- Body:
```json
{
  "sentiment_data": {{$json["data"]}},
  "start_date": "20241104",
  "end_date": "20241111",
  "leverage": 1.0
}
```

Connect: Node 1 → Node 2 → Node 3

---

## Keeping It Running

**For Development:**
- Run both terminals (server + ngrok)
- Restart ngrok after 2 hours (free tier limit)
- Update n8n URL when ngrok URL changes

**For Production:**
- Deploy server to cloud (Heroku, Railway, Render)
- Get permanent URL (no ngrok needed)
- See N8N_CONNECTION_GUIDE.md for deployment instructions

---

## Next Steps

1. ✅ Start your server: `./start_server.sh`
2. ✅ Start ngrok: `ngrok http 8000`
3. ✅ Copy your ngrok HTTPS URL
4. ✅ Test with: `curl -H "ngrok-skip-browser-warning: true" https://YOUR-URL/health`
5. ✅ Share URL with your professor
6. ✅ Configure n8n workflow
7. ✅ Test the workflow

---

## Documentation

- **Full Guide:** See `N8N_CONNECTION_GUIDE.md` for detailed setup
- **API Docs:** Visit `https://YOUR-NGROK-URL/docs` for interactive API docs
- **Test Script:** Run `python test_n8n_endpoints.py` to test all endpoints

---

**Questions?** Check the troubleshooting section or refer to N8N_CONNECTION_GUIDE.md
