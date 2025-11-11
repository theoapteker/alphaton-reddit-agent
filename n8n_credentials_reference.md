# n8n Workflow - Quick Credentials Reference

## Quick Setup Checklist

- [ ] Import workflow JSON into n8n
- [ ] Set up FINTER JWT token credential
- [ ] Set up Reddit OAuth2 credential
- [ ] Update email address in scheduler node
- [ ] Test workflow execution
- [ ] Enable automatic scheduling (optional)

---

## Credentials

### FINTER JWT Token

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0NGQ4NGRhYy01MDUxLTcwOGYtMjI2YS01ZDlhOTRiMDQ5OGUiLCJlbWFpbCI6InR3YTIwMTdAbnl1LmVkdSIsIm5hbWUiOiJUaGVvIEFwdGVrZXIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0d2EyMDE3QG55dS5lZHUiLCJjb2duaXRvOmdyb3VwcyI6WyJwYXJ0bmVycy1ueXUiXSwiaWF0IjoxNzYyNzIwMjUzLCJleHAiOjE3NjUzMTIyNTMsImlzcyI6InFhdXRoLXRva2VuLWlzc3VlciJ9.x9pFfVr2whwqW00SqGjZsUT7oW4c0-kjm-QBQKketX0
```

**Token Details:**
- User: Theo Apteker (twa2017@nyu.edu)
- Groups: partners-nyu
- Issued: 2025-11-09
- Expires: 2025-12-09
- Use as: `Bearer TOKEN` in Authorization header

### Reddit API Credentials

```
Client ID: xLLxS77jwhaQOVoblCBAWw
Client Secret: UokXiZV56kjeCYKmkK6UdORTdtJ66w
Username: hackathonQuantit
Password: 3_w+CGE%_&7mti6
```

**OAuth2 Endpoints:**
- Authorization URL: `https://www.reddit.com/api/v1/authorize`
- Access Token URL: `https://www.reddit.com/api/v1/access_token`
- API Base URL: `https://oauth.reddit.com`
- User-Agent: `AlphatonAgent/1.0`

---

## MCP Server URLs & Authentication

### ✅ No Authentication Required

| Server | URL | Trailing Slash |
|--------|-----|----------------|
| DateTime | `https://datetime.mcp.qore.so/mcp/` | ✅ Yes |

### 🔐 Authentication Required (Bearer Token)

| Server | URL | Trailing Slash | Transport |
|--------|-----|----------------|-----------|
| Market Voice | `https://mavo2.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| Screener | `https://screener.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| Stock Screener | `https://stock-screener.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| Theme | `https://theme.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| Stock AI Brief | `https://stock-ai-brief.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| Stock Fundamental | `https://moneytoring-brief.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| Economic Calendar | `https://economic-calendar.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| IPO | `https://ipo.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| Ticker | `https://ticker.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| EDGAR 13F | `https://edgar-13f.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| Market Data | `https://market-data.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| FINTER | `https://finter.mcp.qore.so/mcp` | ❌ No | streamable_http |
| QFlex | `https://mcp-qflex.hilala.ai/mcp` | ❌ No | streamable_http |
| Model Search | `https://mcp-msearch.hilala.ai/mcp` | ❌ No | streamable_http |
| Alpha Simulator | `https://ark-simulator.mcp.qore.so/mcp/` | ✅ Yes | streamable_http |
| Scheduler | `https://mcp-scheduler.hilala.ai/mcp` | ❌ No | streamable_http |

---

## MCP Server Tools Reference

### Ticker MCP
```json
{
  "name": "search_stock",
  "arguments": {
    "keyword": "AAPL"
  }
}
```

### Market Voice MCP
```json
{
  "name": "search_market_voice_topics_by_text",
  "arguments": {
    "text": "Apple stock",
    "market": "US"
  }
}
```

### Stock AI Brief MCP
```json
{
  "name": "get_stock_ai_brief",
  "arguments": {
    "ticker": "AAPL"
  }
}
```

### Stock Fundamental MCP
```json
{
  "name": "get_fundamental_current",
  "arguments": {
    "ticker": "AAPL"
  }
}
```

### Market Data MCP
```json
{
  "name": "get_market_data_current",
  "arguments": {
    "ticker": "AAPL"
  }
}
```

### Theme MCP
```json
{
  "name": "get_popular_theme_list",
  "arguments": {}
}
```

### Screener MCP
```json
{
  "name": "get_screener_filter_list",
  "arguments": {}
}
```

### EDGAR 13F MCP
```json
{
  "name": "get_13f_portfolio",
  "arguments": {
    "cik": "0001067983",
    "filing_date": "2024-12-31"
  }
}
```

### Economic Calendar MCP
```json
{
  "name": "get_events_by_period",
  "arguments": {
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }
}
```

### FINTER MCP - Generate Alpha
```json
{
  "name": "generate_alpha",
  "arguments": {
    "user_request": "Generate a sentiment-based alpha strategy...",
    "additional_context": "Reddit data with sentiment scores..."
  }
}
```

### FINTER MCP - Submit Model
```json
{
  "name": "model_submit",
  "arguments": {
    "model_name": "reddit_sentiment_alpha_v1",
    "model_code": "# Python alpha code here",
    "universe": "us_stock",
    "schedule": "0 16 * * *"
  }
}
```

### QFlex MCP
```json
{
  "name": "backtest_model_parameters",
  "arguments": {
    "model_code": "# Alpha code",
    "parameter_sets": [
      {"leverage": 1.0},
      {"leverage": 1.5}
    ],
    "start_date": "20240101",
    "end_date": "20241231"
  }
}
```

### Alpha Simulator MCP
```json
{
  "name": "run_simulator",
  "arguments": {
    "model_code": "# Alpha code",
    "start_date": "20240101",
    "end_date": "20241231",
    "initial_cash": 100000000
  }
}
```

### Scheduler MCP
```json
{
  "name": "create_notification_schedule",
  "arguments": {
    "schedule_name": "reddit_alpha_daily_report",
    "cron_expression": "0 17 * * *",
    "email": "your-email@example.com",
    "message": "Daily report message"
  }
}
```

---

## n8n HTTP Request Format for MCP Servers

All MCP servers use the same request format:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "TOOL_NAME",
    "arguments": {
      // Tool-specific arguments
    }
  },
  "id": 1
}
```

**Headers:**
```
Authorization: Bearer YOUR_FINTER_JWT_TOKEN
Content-Type: application/json
```

---

## Common n8n Node Configurations

### HTTP Request Node for MCP Servers

```
Method: POST
URL: [MCP Server URL]
Authentication: None (use headers)
Body Content Type: JSON
Send Body: Yes

Headers:
  Authorization: Bearer {{$credentials.finterJWT}}
  Content-Type: application/json

Body Parameters:
  jsonrpc: "2.0"
  method: "tools/call"
  params: {"name":"TOOL_NAME","arguments":{...}}
  id: 1
```

### HTTP Request Node for Reddit API

```
Method: GET
URL: https://oauth.reddit.com/r/wallstreetbets/new
Authentication: OAuth2
Query Parameters:
  limit: 100
  t: week

Headers:
  User-Agent: AlphatonAgent/1.0
```

---

## Performance Thresholds

The workflow uses these thresholds to decide whether to submit:

```javascript
// In "Analyze Backtest Results" node
performanceMetrics.pass_threshold = (
  performanceMetrics.sharpe_ratio > 0.5 &&      // Risk-adjusted returns
  performanceMetrics.total_return > 5 &&        // Minimum 5% return
  performanceMetrics.max_drawdown < 30          // Max 30% drawdown
);
```

**Adjust these values based on your risk tolerance and requirements.**

---

## Cron Schedule Examples

```
0 16 * * *     # Daily at 4 PM UTC
0 */6 * * *    # Every 6 hours
0 9 * * 1      # Every Monday at 9 AM
0 0 1 * *      # First day of every month at midnight
*/30 * * * *   # Every 30 minutes
```

---

## Environment Variables (Alternative to Credentials)

If you prefer environment variables in n8n:

```bash
# In n8n settings or docker-compose.yml
FINTER_JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
REDDIT_CLIENT_ID=xLLxS77jwhaQOVoblCBAWw
REDDIT_CLIENT_SECRET=UokXiZV56kjeCYKmkK6UdORTdtJ66w
REDDIT_USERNAME=hackathonQuantit
REDDIT_PASSWORD=3_w+CGE%_&7mti6
USER_EMAIL=twa2017@nyu.edu
```

Then reference in nodes using: `{{ $env.FINTER_JWT_TOKEN }}`

---

## Troubleshooting Quick Checks

✅ **Before running workflow:**

1. [ ] FINTER JWT token is valid (expires 2025-12-09)
2. [ ] Reddit OAuth2 is configured
3. [ ] All MCP nodes have credentials attached
4. [ ] URLs match exactly (check trailing slashes!)
5. [ ] Email address is updated in scheduler node

❌ **Common errors:**

| Error | Solution |
|-------|----------|
| 401 Unauthorized | Check FINTER JWT token |
| Reddit auth failed | Re-configure Reddit OAuth2 |
| 404 Not Found | Check MCP URL (trailing slash?) |
| No data returned | Check tool name and arguments |
| Workflow timeout | Add rate limiting / reduce parallel calls |

---

## Quick Test Commands

### Test FINTER JWT Token
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://finter.mcp.qore.so/mcp
```

### Test Reddit API
```bash
curl -H "User-Agent: AlphatonAgent/1.0" \
  -H "Authorization: Bearer YOUR_REDDIT_TOKEN" \
  https://oauth.reddit.com/r/wallstreetbets/new?limit=10
```

### Get Reddit Access Token
```bash
curl -X POST \
  -d "grant_type=password&username=hackathonQuantit&password=3_w+CGE%_&7mti6" \
  --user "xLLxS77jwhaQOVoblCBAWw:UokXiZV56kjeCYKmkK6UdORTdtJ66w" \
  https://www.reddit.com/api/v1/access_token
```

---

## File Locations

```
/home/user/alphaton-reddit-agent/
├── n8n_reddit_alpha_workflow.json        # Main workflow file
├── N8N_WORKFLOW_SETUP.md                 # Detailed setup guide
├── n8n_credentials_reference.md          # This file
├── MCP_SERVERS.md                        # MCP server documentation
└── README.md                             # Project overview
```

---

## Support & Resources

- **FINTER Platform**: https://finter.quantit.io/
- **n8n Documentation**: https://docs.n8n.io/
- **Reddit API**: https://www.reddit.com/dev/api
- **Project Repository**: github.com/theoapteker/alphaton-reddit-agent

---

**Last Updated**: 2025-01-11
**Workflow Version**: 1.0
**FINTER Token Expires**: 2025-12-09
