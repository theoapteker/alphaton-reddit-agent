# 🚀 n8n Reddit Alpha Agent - Quick Start

> **Complete automated workflow for generating and deploying trading alphas using Reddit sentiment analysis**

## What This Does

This n8n workflow automatically:

1. ✅ **Scrapes Reddit** (r/wallstreetbets) for stock mentions
2. ✅ **Extracts tickers** ($AAPL, $TSLA, etc.)
3. ✅ **Analyzes sentiment** (positive/negative/neutral)
4. ✅ **Enriches with 17+ data sources** (fundamentals, market data, themes, etc.)
5. ✅ **Generates alpha code** using FINTER's AI
6. ✅ **Optimizes parameters** using QFlex
7. ✅ **Backtests strategy** using Alpha Simulator
8. ✅ **Submits to FINTER** for live trading (if performance is good)
9. ✅ **Schedules daily reports** via email

**Total Time to Set Up**: ~10 minutes
**Lines of Code You Need to Write**: 0
**Click Execute and It Works**: ✅ Yes

---

## 📦 Files You Need

| File | Purpose |
|------|---------|
| `n8n_reddit_alpha_workflow.json` | The complete workflow (import this into n8n) |
| `N8N_WORKFLOW_SETUP.md` | Detailed setup instructions |
| `n8n_credentials_reference.md` | All credentials and MCP server URLs |
| `N8N_QUICK_START.md` | This file (quick start guide) |

---

## ⚡ 3-Step Quick Start

### Step 1: Import Workflow

1. Open n8n web interface
2. Click **Import from File**
3. Select `n8n_reddit_alpha_workflow.json`
4. Click **Import**

### Step 2: Add Credentials

**FINTER JWT Token:**
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0NGQ4NGRhYy01MDUxLTcwOGYtMjI2YS01ZDlhOTRiMDQ5OGUiLCJlbWFpbCI6InR3YTIwMTdAbnl1LmVkdSIsIm5hbWUiOiJUaGVvIEFwdGVrZXIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0d2EyMDE3QG55dS5lZHUiLCJjb2duaXRvOmdyb3VwcyI6WyJwYXJ0bmVycy1ueXUiXSwiaWF0IjoxNzYyNzIwMjUzLCJleHAiOjE3NjUzMTIyNTMsImlzcyI6InFhdXRoLXRva2VuLWlzc3VlciJ9.x9pFfVr2whwqW00SqGjZsUT7oW4c0-kjm-QBQKketX0
```

**Reddit OAuth2:**
- Client ID: `xLLxS77jwhaQOVoblCBAWw`
- Client Secret: `UokXiZV56kjeCYKmkK6UdORTdtJ66w`
- Username: `hackathonQuantit`
- Password: `3_w+CGE%_&7mti6`

### Step 3: Execute

1. Click **Execute Workflow**
2. Watch it run automatically
3. Check the final output node for results

**That's it! 🎉**

---

## 🎯 What to Expect

### If Performance is Good ✅

```json
{
  "status": "SUCCESS",
  "submitted_to_finter": true,
  "model_id": "abc123xyz",
  "performance": {
    "sharpe_ratio": 1.2,
    "total_return": 15.5,
    "max_drawdown": 12.3
  }
}
```

Your alpha is now **LIVE** on FINTER! 🚀

### If Performance is Poor ❌

```json
{
  "status": "NOT_SUBMITTED",
  "reason": "Performance below threshold",
  "recommendations": [
    "Review sentiment analysis",
    "Adjust parameters",
    "Add more data sources"
  ]
}
```

Don't worry - this is expected! You can adjust parameters and try again.

---

## 🔧 Configuration

### Change Email for Reports

In the **"Schedule Daily Reports"** node:
```json
{
  "email": "YOUR_EMAIL@example.com"
}
```

### Adjust Performance Thresholds

In the **"Analyze Backtest Results"** node:
```javascript
performanceMetrics.pass_threshold = (
  performanceMetrics.sharpe_ratio > 0.5 &&  // Change this
  performanceMetrics.total_return > 5 &&    // Change this
  performanceMetrics.max_drawdown < 30      // Change this
);
```

### Change Reddit Subreddit

In the **"Scrape Reddit Posts"** node:
```
URL: https://oauth.reddit.com/r/SUBREDDIT_NAME/new
```

Popular options:
- `wallstreetbets` (high activity, meme stocks)
- `stocks` (general discussion)
- `investing` (long-term focus)
- `options` (options trading)

---

## 📊 Workflow Overview

```
Manual Trigger
    ↓
Get Current Time (KST)
    ↓
Scrape Reddit Posts
    ↓
Extract Ticker Mentions ($AAPL, $TSLA, etc.)
    ↓
Analyze Sentiment (positive/negative)
    ↓
    ├─→ Ticker Lookup (MCP)
    ├─→ Market Voice Analysis
    ├─→ Stock AI Brief
    ├─→ Get Fundamentals
    ├─→ Get Market Data
    ├─→ Get Themes
    ├─→ Stock Screener
    ├─→ EDGAR 13F Analysis
    └─→ Economic Calendar
         ↓
    Aggregate All Data
         ↓
    Generate Alpha (FINTER MCP)
         ↓
    Extract Alpha Code
         ↓
    Optimize Parameters (QFlex)
         ↓
    Backtest Alpha (Simulator)
         ↓
    Analyze Results
         ↓
    Decision: Submit?
         ↓
    ├─→ YES: Submit to FINTER + Schedule Reports
    └─→ NO: Return Recommendations
```

**Total Nodes**: 25
**MCP Servers Used**: 17
**API Calls**: ~50-100 per execution

---

## 🛠️ Troubleshooting

### "401 Unauthorized" Error

**Problem**: FINTER JWT token expired or incorrect
**Solution**: Check token expiry (expires 2025-12-09), update if needed

### Reddit Authentication Failed

**Problem**: OAuth2 not configured correctly
**Solution**: Use manual token method (see `N8N_WORKFLOW_SETUP.md`)

### No Ticker Mentions Found

**Problem**: Time range too narrow or no activity
**Solution**: Change `t=week` to `t=day` or increase `limit`

### Workflow Takes Too Long

**Problem**: Too many parallel API calls
**Solution**: Add rate limiting or reduce Reddit post limit

---

## 📈 Performance Metrics Explained

| Metric | What It Means | Good Value |
|--------|---------------|------------|
| **Sharpe Ratio** | Risk-adjusted returns | > 0.5 |
| **Total Return** | Overall profit percentage | > 5% |
| **Max Drawdown** | Worst loss from peak | < 30% |

**Note**: These thresholds are conservative. Adjust based on your risk tolerance.

---

## 🔄 Automation

To run automatically every day:

1. Replace **"Manual Trigger"** with **"Cron"** node
2. Set schedule: `0 16 * * *` (daily at 4 PM UTC)
3. Save and activate workflow

---

## 📚 Additional Resources

- **Detailed Setup**: See `N8N_WORKFLOW_SETUP.md`
- **Credentials Reference**: See `n8n_credentials_reference.md`
- **MCP Servers**: See `MCP_SERVERS.md`
- **Project Documentation**: See `README.md`

---

## 🎓 How It Works (Simple Explanation)

1. **Reddit Scraping**: Gets recent posts mentioning stocks (e.g., "$AAPL to the moon!")
2. **Sentiment Analysis**: Scores each mention as positive, negative, or neutral
3. **Data Enrichment**: Fetches fundamentals, news, themes, institutional holdings, etc.
4. **Alpha Generation**: AI generates Python code for a trading strategy
5. **Optimization**: Tests different parameters (leverage, thresholds, etc.)
6. **Backtesting**: Simulates the strategy on historical data
7. **Evaluation**: Checks if Sharpe ratio, returns, and drawdown are acceptable
8. **Deployment**: If good, submits to FINTER for live trading

---

## ✨ Features

- ✅ **Zero code required** - just import and configure
- ✅ **17+ data sources** - comprehensive market intelligence
- ✅ **AI-powered alpha generation** - using FINTER's LLM
- ✅ **Automatic parameter optimization** - finds best settings
- ✅ **Built-in risk management** - enforces position limits
- ✅ **Performance gating** - only submits if metrics are good
- ✅ **Email notifications** - daily reports automatically
- ✅ **Production-ready** - connects directly to FINTER live trading

---

## 🚀 Next Steps After First Run

1. **Monitor Performance**: Check FINTER dashboard
2. **Review Email Reports**: Daily at 5 PM UTC
3. **Iterate Parameters**: Adjust thresholds based on results
4. **Add Data Sources**: Integrate more MCP servers
5. **Experiment**: Try different subreddits, time ranges, universes

---

## 💡 Pro Tips

1. **Start Conservative**: Use `leverage=1.0` initially
2. **Monitor Closely**: Check performance daily for first week
3. **Diversify Signals**: Add more data sources beyond Reddit
4. **Test Thoroughly**: Run multiple backtests before live trading
5. **Stay Updated**: Check FINTER for new MCP servers

---

## ⚠️ Important Notes

- **Token Expiry**: FINTER JWT expires 2025-12-09 (get new token after)
- **Reddit Rate Limits**: Don't scrape too frequently (max every 30 mins)
- **MCP URLs**: Some have trailing slashes, some don't - be exact!
- **Performance**: Not all strategies will pass thresholds - this is good!
- **Paper Trading**: Test thoroughly before deploying real capital

---

## 📞 Support

**Questions?**
- Check `N8N_WORKFLOW_SETUP.md` for detailed troubleshooting
- Review `n8n_credentials_reference.md` for all credentials
- See `MCP_SERVERS.md` for server documentation

**Issues?**
- Verify credentials are correct
- Check n8n node error messages
- Ensure MCP server URLs match exactly

---

## 🎉 Success Checklist

- [ ] Workflow imported successfully
- [ ] FINTER JWT token configured
- [ ] Reddit OAuth2 configured
- [ ] Email updated in scheduler node
- [ ] First test execution successful
- [ ] Performance metrics visible
- [ ] Understood output format
- [ ] (Optional) Automatic scheduling enabled

**If all checked, you're ready to go! 🚀**

---

**Version**: 1.0
**Last Updated**: 2025-01-11
**Author**: Theo Apteker (twa2017@nyu.edu)
**Project**: Alphaton Reddit Agent
