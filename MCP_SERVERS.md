# FINTER MCP Servers Documentation

This document provides comprehensive information about all available Model Context Protocol (MCP) servers on the FINTER platform, as well as the n8n server provided by our professor.

## Overview

MCP servers provide specialized functionality for financial data analysis, stock screening, alpha generation, and backtesting. These servers are accessed via HTTP endpoints and offer various tools for quantitative finance research.

**Important Note**: Some URLs have a trailing slash ("/") and some don't. Please enter them exactly as specified.

---

## Available MCP Servers

### 1. Market Voice
- **URL**: `https://mavo2.mcp.qore.so/mcp/`
- **Function**: Provide summarized information (MCP) on U.S. and Korean stocks from multiple data sources
- **Data Sources**:
  - News
  - YouTube
  - Telegram
  - Investor Relations (IR)
  - Disclosure data
- **Use Cases**: Sentiment analysis, market intelligence, multi-source data aggregation

---

### 2. Screener
- **URL**: `https://screener.mcp.qore.so/mcp/`
- **Function**: Provide stock screening functionality for Korean and U.S. stocks
- **Use Cases**: Filter stocks based on various criteria, identify investment opportunities

---

### 3. Stock Screener
- **URL**: `https://stock-screener.mcp.qore.so/mcp/`
- **Function**: Provide stock screening functionality for Korean and U.S. stocks #2
- **Use Cases**: Alternative stock screening interface with potentially different filtering options

---

### 4. Theme
- **URL**: `https://theme.mcp.qore.so/mcp/`
- **Function**: List of themes for Korean and U.S. stocks, along with theme-related stock information
- **Use Cases**: Thematic investing, sector rotation strategies, trend identification

---

### 5. Stock AI Brief
- **URL**: `https://stock-ai-brief.mcp.qore.so/mcp/`
- **Function**: AI-powered stock analysis information for top Korean and U.S. stocks
- **Use Cases**: Quick stock analysis, AI-generated insights, fundamental research

---

### 6. Stock Fundamental
- **URL**: `https://moneytoring-brief.mcp.qore.so/mcp/`
- **Function**: Corporate financial factor data
- **Use Cases**: Fundamental analysis, financial ratio calculations, value investing research

---

### 7. Economic Calendar
- **URL**: `https://economic-calendar.mcp.qore.so/mcp/`
- **Function**: Economic indicator release dates and figures
- **Use Cases**: Macro analysis, event-driven strategies, economic data monitoring

---

### 8. IPO
- **URL**: `https://ipo.mcp.qore.so/mcp/`
- **Function**: (Korea) IPO information
- **Use Cases**: New listing tracking, IPO analysis, early-stage investment research
- **Market Coverage**: Korean market

---

### 9. Ticker
- **URL**: `https://ticker.mcp.qore.so/mcp/`
- **Function**: Search for stock names and tickers
- **Use Cases**: Symbol lookup, ticker conversion, company name resolution

---

### 10. EDGAR 13F
- **URL**: `https://edgar-13f.mcp.qore.so/mcp/`
- **Function**: 13F filing portfolio information
- **Use Cases**: Institutional investor tracking, portfolio analysis, smart money following
- **Data Source**: SEC EDGAR filings

---

### 11. Market Data
- **URL**: `https://market-data.mcp.qore.so/mcp/`
- **Function**: Stock price data and order book data
- **Use Cases**: Price analysis, order flow analysis, market microstructure research

---

### 12. DateTime
- **URL**: `https://datetime.mcp.qore.so/mcp/`
- **Function**: Current time (KST - Korean Standard Time)
- **Use Cases**: Time synchronization, timezone conversion, timestamp generation

---

### 13. FINTER
- **URL**: `https://finter.mcp.qore.so/mcp`
- **Function**: FINTER user manual and alpha generation
- **Key Features**:
  - Generate investment ideas as alpha codes
  - Create parameters
  - Register model code in FINTER
  - Alpha code follows an executable format within FINTER
- **Use Cases**: Alpha strategy development, quantitative strategy creation, model registration

---

### 14. QFlex
- **URL**: `https://mcp-qflex.hilala.ai/mcp`
- **Function**: Conduct parameter testing by combining alpha codes with parameter sets
- **Key Features**:
  - Optimizes hyperparameters of alphas generated in FINTER MCP
  - Should be used together with FINTER MCP
- **Use Cases**: Parameter optimization, hyperparameter tuning, alpha refinement
- **Note**: Complementary to FINTER - use both together for optimal results

---

### 15. Model Search
- **URL**: `https://mcp-msearch.hilala.ai/mcp`
- **Function**: Browse models registered in FINTER and build meta-models
- **Key Features**:
  - Browse existing models
  - Combine multiple models
  - Build meta-models
- **Use Cases**: Model discovery, ensemble strategies, meta-learning

---

### 16. Alpha Simulator
- **URL**: `https://ark-simulator.mcp.qore.so/mcp/`
- **Function**: Backtest FINTER models
- **Use Cases**: Strategy validation, performance analysis, risk assessment

---

### 17. Scheduler
- **URL**: `https://mcp-scheduler.hilala.ai/mcp`
- **Function**: Schedule ark agent calls and send email results
- **Key Features**:
  - Automated task scheduling
  - Email notifications
  - Result delivery
- **Use Cases**: Automated reporting, scheduled analysis, workflow automation

---

## Additional Infrastructure

### n8n Server
- **Provider**: Course professor
- **Function**: Workflow automation and integration platform
- **Use Cases**: Custom workflows, data pipeline automation, integration between different MCP servers

---

## Typical Workflows

### Alpha Development Workflow
1. **FINTER** - Generate alpha code
2. **QFlex** - Optimize alpha parameters
3. **Alpha Simulator** - Backtest the optimized alpha
4. **Model Search** - Combine with other models if needed
5. **Scheduler** - Schedule regular execution and reporting

### Research Workflow
1. **Ticker** - Look up stock symbols
2. **Stock Fundamental** - Get fundamental data
3. **Market Voice** - Gather market sentiment
4. **Theme** - Identify relevant themes
5. **Stock AI Brief** - Get AI analysis
6. **Economic Calendar** - Check upcoming events

### Institutional Analysis Workflow
1. **EDGAR 13F** - Get institutional holdings
2. **Market Data** - Analyze price action
3. **Stock Fundamental** - Review fundamentals
4. **Alpha Simulator** - Test follow strategies

---

## Best Practices

1. **URL Accuracy**: Pay careful attention to trailing slashes in URLs
2. **Combined Usage**: Many servers work best when used together (e.g., FINTER + QFlex)
3. **Time Awareness**: Use DateTime server for KST synchronization
4. **Data Validation**: Cross-reference data from multiple servers for accuracy
5. **Automation**: Leverage Scheduler for regular tasks and reporting

---

## Server Categories

### Data Sources
- Market Voice
- Stock Fundamental
- Market Data
- Economic Calendar
- EDGAR 13F

### Stock Discovery
- Screener
- Stock Screener
- Theme
- IPO
- Ticker

### Analysis & Intelligence
- Stock AI Brief
- Stock Fundamental
- Market Voice

### Alpha Development & Testing
- FINTER
- QFlex
- Alpha Simulator
- Model Search

### Utilities
- DateTime
- Scheduler

---

## Support and Resources

For more information about specific MCP servers, refer to their individual documentation or contact the FINTER platform administrators.

**Note**: This documentation is current as of the project setup date. Server URLs and functionality may be updated over time.
