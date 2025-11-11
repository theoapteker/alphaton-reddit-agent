# n8n FINTER Workflow Setup Guide

This guide will help you set up the automated Reddit Sentiment → FINTER trading pipeline using n8n.

## 📋 What This Workflow Does

```
1. Schedule Trigger (3:30 PM UTC daily)
   ↓
2. Run Python Script (scrape Reddit, analyze sentiment)
   ↓
3. Parse Results (extract tickers, positions, metrics)
   ↓
4. Call MCP Servers in Parallel:
   - AI Stock Analysis (stock_ai_brief)
   - Market Voice Sentiment (market_voice)
   - Latest Market Data (market-data)
   ↓
5. Merge All Data Sources
   ↓
6. Backtest with Alpha Simulator
   ↓
7. Check: Sharpe > 1.5 AND Max Drawdown < 15%?
   ├─ YES → Submit to FINTER + Send Success Email
   └─ NO → Send Failure Email (don't submit)
```

## 🚀 Quick Start

### Step 1: Install n8n

**Option A: Docker (Recommended)**
```bash
docker run -d --restart unless-stopped \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Option B: npm**
```bash
npm install n8n -g
n8n start
```

**Option C: n8n Cloud**
- Sign up at https://n8n.io/cloud

### Step 2: Access n8n

Open your browser and go to:
```
http://localhost:5678
```

### Step 3: Import Workflow

1. Click **Workflows** in the sidebar
2. Click **Import from File**
3. Select `n8n_finter_workflow.json`
4. Click **Import**

### Step 4: Configure Credentials

#### A. Set Environment Variables

In n8n, go to **Settings → Variables** and add:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `FINTER_JWT_TOKEN` | `your_token_here` | FINTER API authentication token |
| `REDDIT_CLIENT_ID` | `your_id_here` | Reddit API client ID |
| `REDDIT_CLIENT_SECRET` | `your_secret_here` | Reddit API secret |
| `REDDIT_USERNAME` | `your_username` | Reddit username |
| `REDDIT_PASSWORD` | `your_password` | Reddit password |

#### B. Configure Email Credentials

1. Go to **Credentials** → **Create New**
2. Select **SMTP**
3. Fill in your email settings:

**For Gmail:**
```
Host: smtp.gmail.com
Port: 587
User: your@gmail.com
Password: your-app-password
Secure: true
```

**To get Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to **App Passwords**
4. Generate password for "Mail"

#### C. Configure HTTP Auth for MCP Servers

The workflow uses Bearer token authentication for MCP servers.

1. Each MCP HTTP Request node is configured to use:
```
Authorization: Bearer {{ $env.FINTER_JWT_TOKEN }}
```

This pulls the token from your environment variables automatically.

### Step 5: Update File Paths

Edit the "Run Python: Generate Positions" node:

Change this path to match your system:
```bash
cd /home/user/alphaton-reddit-agent
```

To your actual path:
```bash
cd /Users/theoapteker/alphaton-reddit-agent
```

### Step 6: Test the Workflow

#### Test Individual Nodes

1. Click on "Run Python: Generate Positions" node
2. Click **Execute Node** (the play button)
3. Check the output

#### Test Full Workflow

1. Click **Execute Workflow** in the top right
2. Watch each node execute in sequence
3. Check for any errors (red indicators)

### Step 7: Activate Schedule

1. Toggle **Active** switch in top right to ON
2. The workflow will now run daily at 3:30 PM UTC

## 🔧 Configuration Options

### Adjust Schedule

Edit the "Schedule Trigger" node:

```json
{
  "cronExpression": "30 15 * * *"  // Current: 3:30 PM UTC
}
```

Change to:
```
"0 14 * * *"   // 2:00 PM UTC
"45 15 * * *"  // 3:45 PM UTC
"0 9 * * 1-5"  // 9:00 AM UTC, weekdays only
```

### Adjust Backtest Criteria

Edit the "Check: Backtest Passes Criteria?" node:

Current criteria:
- Sharpe Ratio > 1.5
- Max Drawdown < 15%

To make it stricter:
- Sharpe Ratio > 2.0
- Max Drawdown < 10%

To make it looser:
- Sharpe Ratio > 1.0
- Max Drawdown < 20%

### Change Email Recipients

Edit both email nodes and change:
```
"toEmail": "your@email.com"
```

To your actual email address.

### Adjust Python Script Parameters

Edit the "Run Python: Generate Positions" node command:

```bash
# Current
python submit_to_finter.py --dry-run --days 7 --model-name reddit_sentiment_v1

# More historical data
python submit_to_finter.py --dry-run --days 30 --model-name reddit_sentiment_v1

# Higher leverage
python submit_to_finter.py --dry-run --days 7 --leverage 1.5 --model-name reddit_sentiment_v2

# Live submission (CAREFUL!)
python submit_to_finter.py --days 7 --model-name reddit_sentiment_v1
```

## 📊 Understanding the Workflow

### Node Details

#### 1. Schedule Trigger
- **Runs**: Daily at 3:30 PM UTC
- **Why 3:30 PM**: FINTER executes at 4:00 PM, so this gives 30 minutes for data processing

#### 2. Run Python Script
- **Does**: Executes your complete pipeline
- **Output**: Position data, tickers, metrics
- **Duration**: ~3-5 minutes (depends on Reddit API)

#### 3. Parse Python Results
- **Does**: Extracts structured data from script output
- **Extracts**: Tickers, positions, file paths, metrics

#### 4. MCP: Get AI Stock Analysis
- **Server**: `stock-ai-brief.mcp.qore.so`
- **Does**: Gets AI-powered analysis for each detected stock
- **Returns**: AI insights, predictions, key metrics

#### 5. MCP: Get Market Voice Sentiment
- **Server**: `mavo2.mcp.qore.so`
- **Does**: Aggregates sentiment from news, YouTube, Telegram
- **Returns**: Multi-source sentiment scores

#### 6. MCP: Get Latest Market Data
- **Server**: `market-data.mcp.qore.so`
- **Does**: Fetches current prices and order book
- **Returns**: Real-time market data

#### 7. Merge All Data Sources
- **Does**: Combines Reddit + AI + News + Market data
- **Output**: Enriched dataset for backtesting

#### 8. MCP: Backtest with Alpha Simulator
- **Server**: `ark-simulator.mcp.qore.so`
- **Does**: Runs historical simulation
- **Returns**: Sharpe ratio, max drawdown, total return

#### 9. Check: Backtest Passes Criteria?
- **Logic**: IF (Sharpe > 1.5 AND Drawdown < 15%)
- **True Branch**: Submit to FINTER
- **False Branch**: Send warning email

#### 10. Submit to FINTER Production
- **API**: `api.finter.quantit.io/submission`
- **Does**: Registers model for live trading
- **Returns**: model_id, validation_url

#### 11. Email Notifications
- **Success**: Sent when model is submitted
- **Failure**: Sent when backtest fails

## 🐛 Troubleshooting

### Error: "Command not found: python"

**Solution**: Update node to use `python3`:
```bash
cd /home/user/alphaton-reddit-agent && source venv/bin/activate && python3 submit_to_finter.py --dry-run
```

### Error: "Module not found: pandas"

**Solution**: Virtual environment not activated. Check path in command:
```bash
source venv/bin/activate  # Must be included in command
```

### Error: "401 Unauthorized" from MCP servers

**Solution**: Check FINTER_JWT_TOKEN is set correctly:
1. Go to Settings → Variables
2. Verify token is present
3. Test token: `curl -H "Authorization: Bearer $TOKEN" https://finter.mcp.qore.so/mcp/`

### Error: Email not sending

**Solution**:
1. Check SMTP credentials
2. For Gmail, use App Password (not regular password)
3. Enable "Less secure app access" (if not using App Password)

### Workflow runs but doesn't submit

**Solution**: Check backtest criteria:
1. Click "MCP: Backtest with Alpha Simulator" node
2. Check output: `sharpe_ratio` and `max_drawdown`
3. If values don't meet criteria, adjust thresholds or improve strategy

## 📈 Monitoring & Logs

### View Execution History

1. Go to **Executions** in sidebar
2. Click on any execution to see details
3. Check each node's input/output

### Set Up Alerts

Add Slack or Discord webhook for real-time alerts:

1. Add new node: **Slack** or **Discord**
2. Connect after "Check: Backtest Passes Criteria?"
3. Send notification with results

### Monitor Performance

Track over time:
- Sharpe ratios
- Stocks detected
- Submission success rate

## 🚀 Advanced Usage

### Add More MCP Servers

#### Theme-Based Filtering
Add after "Parse Python Results":
```json
{
  "node": "MCP: Get Theme Stocks",
  "url": "https://theme.mcp.qore.so/mcp/",
  "body": {
    "themes": ["AI", "Cloud Computing", "EVs"]
  }
}
```

#### Stock Screening
Add before Python script:
```json
{
  "node": "MCP: Screen Stocks",
  "url": "https://screener.mcp.qore.so/mcp/",
  "body": {
    "filters": {
      "market_cap_min": 10000000000,
      "pe_ratio_max": 30
    }
  }
}
```

### Optimize with QFlex

Replace static parameters with optimized ones:
```json
{
  "node": "MCP: Optimize Parameters",
  "url": "https://mcp-qflex.hilala.ai/mcp",
  "body": {
    "alpha_code": "{{ $json.alpha_code }}",
    "parameter_ranges": {
      "leverage": [0.5, 1.0, 1.5, 2.0],
      "lookback_days": [3, 7, 14, 30]
    }
  }
}
```

### Build Ensemble Model

Combine multiple strategies:
```json
{
  "node": "MCP: Model Search",
  "url": "https://mcp-msearch.hilala.ai/mcp",
  "body": {
    "search_criteria": {
      "min_sharpe": 1.5,
      "max_correlation": 0.7
    }
  }
}
```

## 📝 Best Practices

1. **Test in Dry-Run First**: Always use `--dry-run` until confident
2. **Monitor Daily**: Check execution logs daily for first week
3. **Start Conservative**: Begin with Sharpe > 2.0 threshold
4. **Version Your Models**: Use model names like `reddit_sentiment_v1`, `v2`, etc.
5. **Keep Backups**: Export workflow JSON regularly
6. **Set Up Alerts**: Get notified of failures immediately
7. **Review Weekly**: Check performance metrics every Friday

## 🔗 Useful Links

- **n8n Documentation**: https://docs.n8n.io
- **FINTER API Docs**: https://docs.finter.quantit.io
- **Reddit API Docs**: https://www.reddit.com/dev/api
- **Your Position Files**: `/home/user/alphaton-reddit-agent/positions_*.json`

## 🎯 Next Steps

1. ✅ Import workflow into n8n
2. ✅ Configure all credentials
3. ✅ Test individual nodes
4. ✅ Run full workflow test
5. ✅ Verify email notifications work
6. ✅ Activate schedule
7. 📊 Monitor first execution
8. 🚀 Go live!

---

**Questions?** Check the n8n community forum or FINTER documentation.

**Ready to go live?** Remove `--dry-run` from the Python command node!
