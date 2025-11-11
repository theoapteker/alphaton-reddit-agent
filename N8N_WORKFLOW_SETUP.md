# n8n Reddit Alpha Agent Workflow - Setup Guide

This guide will help you set up and run the complete Reddit Alpha Agent workflow in n8n.

## Overview

The workflow automatically:
1. **Scrapes Reddit** for stock mentions from r/wallstreetbets
2. **Extracts tickers** using regex pattern matching ($TICKER)
3. **Analyzes sentiment** using keyword-based analysis
4. **Enriches data** using 17+ MCP servers for market data, fundamentals, themes, etc.
5. **Generates alpha code** using FINTER's AI-powered alpha generator
6. **Optimizes parameters** using QFlex parameter testing
7. **Backtests** the strategy using Alpha Simulator
8. **Evaluates performance** against threshold criteria
9. **Submits to FINTER** for live trading (if performance is good)
10. **Schedules daily reports** via email

## Prerequisites

- Access to n8n (web version or self-hosted)
- Reddit API credentials
- FINTER JWT token
- Basic understanding of n8n workflows

## Step 1: Set Up Credentials in n8n

### 1.1 FINTER JWT Token

1. In n8n, go to **Credentials** → **+ Add Credential**
2. Search for "Header Auth" or create a custom credential type
3. Configure:
   - **Name**: `FINTER JWT Token`
   - **Credential Type**: `Header Auth` (or HTTP Basic Auth)
   - **Header Name**: `Authorization`
   - **Header Value**: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0NGQ4NGRhYy01MDUxLTcwOGYtMjI2YS01ZDlhOTRiMDQ5OGUiLCJlbWFpbCI6InR3YTIwMTdAbnl1LmVkdSIsIm5hbWUiOiJUaGVvIEFwdGVrZXIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0d2EyMDE3QG55dS5lZHUiLCJjb2duaXRvOmdyb3VwcyI6WyJwYXJ0bmVycy1ueXUiXSwiaWF0IjoxNzYyNzIwMjUzLCJleHAiOjE3NjUzMTIyNTMsImlzcyI6InFhdXRoLXRva2VuLWlzc3VlciJ9.x9pFfVr2whwqW00SqGjZsUT7oW4c0-kjm-QBQKketX0`

**Alternative Setup:**
If n8n doesn't support custom credential types well, you can:
- Store the token as a static variable in the workflow
- Use environment variables
- Hard-code it in each HTTP Request node's header (not recommended for production)

### 1.2 Reddit OAuth2 Credentials

**Option A: Using n8n's Reddit Node (Recommended)**

If n8n has a built-in Reddit node:
1. Go to **Credentials** → **+ Add Credential**
2. Search for "Reddit"
3. Configure:
   - **Client ID**: `xLLxS77jwhaQOVoblCBAWw`
   - **Client Secret**: `UokXiZV56kjeCYKmkK6UdORTdtJ66w`
   - **Username**: `hackathonQuantit`
   - **Password**: `3_w+CGE%_&7mti6`

**Option B: Using HTTP Request with OAuth2**

If n8n doesn't have a Reddit node:
1. Create an OAuth2 credential
2. Configure:
   - **Authorization URL**: `https://www.reddit.com/api/v1/authorize`
   - **Access Token URL**: `https://www.reddit.com/api/v1/access_token`
   - **Client ID**: `xLLxS77jwhaQOVoblCBAWw`
   - **Client Secret**: `UokXiZV56kjeCYKmkK6UdORTdtJ66w`
   - **Scope**: `read`
   - **Auth Type**: `Basic Auth`

**Option C: Manual Token (Simplest for Testing)**

For the simplest setup, you can manually get a Reddit access token:

```bash
# Get Reddit access token
curl -X POST -d "grant_type=password&username=hackathonQuantit&password=3_w+CGE%_&7mti6" \
  --user "xLLxS77jwhaQOVoblCBAWw:UokXiZV56kjeCYKmkK6UdORTdtJ66w" \
  https://www.reddit.com/api/v1/access_token
```

Then use the returned `access_token` in the HTTP Request node headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Note: Reddit access tokens expire after 1 hour, so Option A or B is better for production.

## Step 2: Import the Workflow

1. Open n8n web interface
2. Click **Workflows** → **+ Add Workflow**
3. Click the **⋮** menu → **Import from File**
4. Select `n8n_reddit_alpha_workflow.json`
5. Click **Import**

## Step 3: Configure Workflow Credentials

After importing, you need to link the credentials to each node:

### Nodes that Need FINTER JWT Token:
- Ticker Lookup (MCP)
- Market Voice Analysis
- Stock AI Brief
- Get Fundamentals
- Get Market Data
- Get Popular Themes
- Stock Screener
- EDGAR 13F Analysis
- Economic Calendar
- Generate Alpha (FINTER MCP)
- Optimize Parameters (QFlex)
- Backtest Alpha (Simulator)
- Submit to FINTER
- Schedule Daily Reports

**For each of these nodes:**
1. Click on the node
2. Find the "Credentials" section
3. Select your FINTER JWT Token credential

### Node that Needs Reddit OAuth:
- Scrape Reddit Posts

**Configure:**
1. Click on "Scrape Reddit Posts" node
2. Select your Reddit OAuth2 credential

## Step 4: Adjust Workflow Parameters (Optional)

You can customize various parameters:

### Reddit Scraping
- **Subreddit**: Change `wallstreetbets` to other finance subreddits
- **Limit**: Adjust from 100 to fetch more/fewer posts
- **Time range**: Change `t=week` to `t=day`, `t=month`, etc.

### Sentiment Thresholds
In the "Analyze Backtest Results" node, adjust:
- **Sharpe Ratio threshold**: Currently 0.5 (higher = better risk-adjusted returns)
- **Total Return threshold**: Currently 5% (minimum acceptable return)
- **Max Drawdown threshold**: Currently 30% (maximum acceptable loss)

### Position Sizing
In the "Optimize Parameters (QFlex)" node, adjust leverage values:
```json
"parameter_sets": [
  {"leverage": 0.5},
  {"leverage": 1.0},
  {"leverage": 1.5},
  {"leverage": 2.0}
]
```

### Email Notifications
In the "Schedule Daily Reports" node, change:
- **Email**: Update from `twa2017@nyu.edu` to your email
- **Schedule**: Modify `0 17 * * *` (5 PM UTC) to your preferred time

## Step 5: Test the Workflow

### Manual Test Run

1. Click **Execute Workflow** button
2. Watch the execution progress
3. Each node will light up as it executes
4. Check node outputs by clicking on them after execution

### Debug Common Issues

**Issue: Reddit authentication fails**
- Solution: Re-configure Reddit OAuth credentials
- Alternative: Use manual token method (see Step 1.2 Option C)

**Issue: MCP server returns 401 Unauthorized**
- Solution: Check that FINTER JWT token is correct
- Solution: Ensure token hasn't expired (check expiry: 2025-12-09)

**Issue: No ticker mentions found**
- Solution: Try a different time range (e.g., `t=day` instead of `t=week`)
- Solution: Lower the limit to recent posts (e.g., `limit=50`)

**Issue: Backtest performance is poor**
- This is expected! The workflow will NOT submit if performance is below thresholds
- You'll get a "Not Submitted Summary" with recommendations

## Step 6: Schedule Automatic Execution

To run the workflow automatically:

1. Replace the "Manual Trigger" node with a "Cron" or "Schedule Trigger" node
2. Configure the schedule:
   - **Expression**: `0 16 * * *` (daily at 4 PM UTC)
   - **Expression**: `0 */6 * * *` (every 6 hours)
   - **Expression**: `0 9 * * 1` (every Monday at 9 AM)

3. Save the workflow
4. Activate the workflow using the toggle in the top-right

## Workflow Node Details

### Data Collection Nodes

| Node | Purpose | MCP Server |
|------|---------|------------|
| Get Current DateTime (KST) | Gets current time in Korean timezone | datetime |
| Scrape Reddit Posts | Fetches posts from r/wallstreetbets | Reddit API |
| Extract Ticker Mentions | Parses $TICKER mentions | JavaScript |
| Analyze Sentiment | Calculates sentiment scores | JavaScript |

### Data Enrichment Nodes

| Node | Purpose | MCP Server |
|------|---------|------------|
| Ticker Lookup (MCP) | Maps tickers to FINTER IDs | ticker |
| Market Voice Analysis | Gets news/social sentiment | market_voice |
| Stock AI Brief | Gets AI stock analysis | stock_ai_brief |
| Get Fundamentals | Gets financial metrics | stock_fundamental |
| Get Market Data | Gets price data | market-data |
| Get Popular Themes | Gets thematic data | theme |
| Stock Screener | Screens stocks | screener |
| EDGAR 13F Analysis | Gets institutional holdings | edgar-13f |
| Economic Calendar | Gets economic events | economic_calendar |

### Alpha Generation Nodes

| Node | Purpose | MCP Server |
|------|---------|------------|
| Aggregate All Data | Combines all data sources | JavaScript |
| Generate Alpha (FINTER MCP) | Generates alpha code | finter |
| Extract Alpha Code | Parses alpha code | JavaScript |
| Optimize Parameters (QFlex) | Tests parameter sets | qflex |
| Backtest Alpha (Simulator) | Runs backtest | alpha-simulator |
| Analyze Backtest Results | Evaluates performance | JavaScript |

### Submission Nodes

| Node | Purpose | MCP Server |
|------|---------|------------|
| Check If Should Submit | Decision gate | n8n IF node |
| Submit to FINTER | Submits model for live trading | finter |
| Schedule Daily Reports | Sets up email notifications | scheduler |

## Understanding the Output

### Success Path (Performance Good)

If the alpha passes performance thresholds, you'll get:

```json
{
  "workflow": "Reddit Alpha Agent - Complete",
  "status": "SUCCESS",
  "model_name": "reddit_sentiment_alpha_v1",
  "performance": {
    "sharpe_ratio": 1.2,
    "total_return": 15.5,
    "max_drawdown": 12.3,
    "pass_threshold": true
  },
  "submitted_to_finter": true,
  "model_id": "abc123xyz",
  "scheduled": true,
  "next_steps": [...]
}
```

### Failure Path (Performance Poor)

If the alpha doesn't meet thresholds:

```json
{
  "workflow": "Reddit Alpha Agent - Complete",
  "status": "NOT_SUBMITTED",
  "reason": "Performance metrics below threshold",
  "thresholds": {
    "sharpe_ratio": { "required": 0.5, "actual": 0.2 },
    "total_return": { "required": 5, "actual": 2.1 },
    "max_drawdown": { "required": 30, "actual": 15.2 }
  },
  "recommendations": [...]
}
```

## Advanced Customization

### Adding More Data Sources

You can add more MCP server nodes in parallel after "Analyze Sentiment":

1. Duplicate an existing MCP node (e.g., "Market Voice Analysis")
2. Change the URL to a different MCP server
3. Adjust the tool name and arguments
4. Connect it to "Aggregate All Data"

### Modifying Alpha Generation Prompt

In the "Generate Alpha (FINTER MCP)" node, edit the `user_request` parameter:

```json
{
  "user_request": "Your custom alpha strategy description here..."
}
```

### Custom Performance Metrics

In the "Analyze Backtest Results" node, modify the decision criteria:

```javascript
performanceMetrics.pass_threshold = (
  performanceMetrics.sharpe_ratio > YOUR_THRESHOLD &&
  performanceMetrics.total_return > YOUR_THRESHOLD &&
  performanceMetrics.max_drawdown < YOUR_THRESHOLD
);
```

## Troubleshooting

### Workflow stops at a node

1. Click on the failed node
2. Check the error message
3. Verify credentials are configured
4. Check that the MCP server URL is correct (note trailing slashes!)

### MCP Server URL Formatting

⚠️ **IMPORTANT**: Some MCP servers have trailing slashes, some don't!

**With trailing slash:**
- `https://market-voice.mcp.qore.so/mcp/`
- `https://datetime.mcp.qore.so/mcp/`
- `https://screener.mcp.qore.so/mcp/`

**Without trailing slash:**
- `https://finter.mcp.qore.so/mcp`
- `https://mcp-qflex.hilala.ai/mcp`
- `https://mcp-msearch.hilala.ai/mcp`

### Rate Limiting

If you hit rate limits:
1. Add "Wait" nodes between MCP calls
2. Reduce the number of parallel requests
3. Add retry logic with exponential backoff

### Memory Issues

If n8n runs out of memory:
1. Reduce Reddit post limit (from 100 to 50)
2. Add pagination/batching for large datasets
3. Use "Split In Batches" node for MCP calls

## Next Steps

After your first successful run:

1. **Monitor FINTER dashboard** for live performance
2. **Check email** for daily reports (if scheduled)
3. **Iterate on parameters** based on performance
4. **Add more data sources** for better signals
5. **Experiment with different subreddits** or time ranges

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [FINTER Platform](https://finter.quantit.io/)
- [MCP Servers Documentation](./MCP_SERVERS.md)
- [Reddit API](https://www.reddit.com/dev/api)

## Support

For issues:
- n8n: Check n8n community forum
- FINTER: Contact FINTER support
- Workflow-specific: Review the JavaScript code nodes for custom logic

## License

This workflow is part of the Alphaton Reddit Agent project.
