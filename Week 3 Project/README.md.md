# Ask Jarvis – Intelligent SCM Agent

## 1. Project overview

Ask Jarvis is a multi-agent supply-chain analytics solution built with n8n, Microsoft SQL Server, Pinecone, and the OpenAI API. It accepts a natural-language business question, decomposes it into one or more specialist tasks, runs the appropriate agents, and returns a consolidated response.

The solution uses `AdventureWorksDW2022` and supports sales forecasts, customer intelligence, campaign drafting, and overlapping requests that require both specialists.

## 2. Business objectives

- Forecast Internet and Reseller revenue by month and product subcategory.
- Explain seasonal patterns for inventory and budget planning.
- Segment customers using recency, frequency, and monetary-value signals.
- Assess inactivity-based churn risk.
- Select campaign audiences from purchase history.
- Draft controlled re-engagement and cross-sell emails.
- Combine sales and customer insights in one response.

Forecasts and churn assessments are decision-support indicators, not statistically validated predictions or churn probabilities.

## 3. Solution components

![alt text](<Project Overview.png>)

### Multi-Intent Agent Router

The router is the public entry point. It validates the webhook request, retrieves approved routing guidance from Pinecone, and asks OpenAI for a structured task decomposition. It can enable either specialist agent or both agents, waits for their results, and returns a single response.

The routing contract includes `run_sales`, `sales_task`, `run_customer`, `customer_task`, `customer_actions`, `forecast_months`, `product_subcategory`, `purchase_period`, `promotion_category`, `customer_key`, and `top_n`.

### Sales Forecast and Trend Analysis Agent

This agent reads historical data from `FactInternetSales`, `FactResellerSales`, `DimDate`, `DimProduct`, and `DimProductSubcategory`. Its fixed T-SQL template aggregates revenue by month, channel, and subcategory and calculates an explainable seasonal baseline. OpenAI explains the calculated rows and provides inventory and budgeting implications.

The LLM does not generate or execute SQL.

### Customer Intelligence and Campaign Agent

This agent uses `DimCustomer`, `FactInternetSales`, `DimDate`, and the product hierarchy. It calculates purchase recency, order frequency, total spend, preferred category, segment, churn-risk level, and campaign eligibility.

Supported actions are:

- `segment_customers`
- `assess_churn_risk`
- `select_campaign_audience`
- `draft_reengagement_email`
- `draft_cross_sell_email`

Generated email content is a draft and requires human approval before use.

### Pinecone grounding store

Pinecone namespace `AskJarvisSCM` stores durable knowledge: approved table and relationship definitions, metrics, forecast methods, segmentation rules, communication policies, data-quality rules, and verified SQL patterns. SQL Server remains authoritative for current sales and customer facts.

### Browser client

The dependency-free web client captures a question, calls the n8n webhook, displays errors and progress, and formats both single-agent and combined responses. Serve it through VS Code Live Server or another HTTP server rather than `file://`.

## 4. Repository structure

```text
Week 3 AI Agents/
├── docs/
│   ├── Architecture.md
│   └── Project-Documentation.md
├── PineCone Seed/
│   ├── METADATA.md
│   └── Seed AskJarvisSCM Agent Knowledge.json
├── Sql/
│   ├── customer_segments.sql
│   └── sales_forecast.sql
├── web-client/
│   ├── assets/ask-jarvis-hero.png
│   ├── app.js
│   ├── index.html
│   ├── README.md
│   └── styles.css
├── Workflows/
│   ├── Jarvis - Multi-Intent Agent Router.json
│   ├── Jarvis - Sales Forecast and Trend Analysis Agent.json
│   └── Jarvis - Customer Intelligence and Campaign Agent.json
└── README.md
```

## 5. Prerequisites

- n8n Community Edition.
- SQL Server with `AdventureWorksDW2022`, reachable from n8n.
- A read-only Microsoft SQL credential in n8n.
- An OpenAI API credential in n8n.
- A Pinecone index compatible with `text-embedding-3-small`.
- Pinecone API credentials and index host.
- VS Code Live Server or another static HTTP server.

## 6. Installation and configuration

1. Import and run the Pinecone seeder once to populate namespace `AskJarvisSCM`.
2. Import the Sales Forecast and Customer Intelligence workflows.
3. Select the working SQL Server and OpenAI credentials in both workflows.
4. Save the specialists so their Execute Workflow Trigger schemas are available.
5. Import the Multi-Intent Agent Router.
6. Select the correct specialist in each Execute Sub-workflow node.
7. Map router fields to specialist inputs while preserving Boolean, number, and array types.
8. Configure the router's OpenAI nodes with the existing OpenAI credential.
9. Configure the Pinecone query with its credential, index host, and `AskJarvisSCM` namespace.
10. Activate the router for its production URL, or use **Listen for test event** with its test URL.
11. Serve `web-client/index.html` and save the webhook URL under **Connection**.

Configure the Webhook node's allowed origin when the client and n8n use different origins.

## 7. Subworkflow input contracts

### Sales specialist

| Input | Type |
|---|---|
| `message` | String |
| `run_sales` | Boolean |
| `sales_task` | String |
| `forecast_months` | Number |
| `product_subcategory` | String |

### Customer specialist

| Input | Type |
|---|---|
| `message` | String |
| `run_customer` | Boolean |
| `customer_task` | String |
| `customer_actions` | Array of strings |
| `product_subcategory` | String |
| `purchase_period` | String |
| `promotion_category` | String |
| `customer_key` | Number |
| `top_n` | Number |

Do not turn Boolean or array values into quoted strings. After changing a specialist trigger schema, refresh or reselect the specialist in the router node.

## 8. Running the solution

Sales-only request:

```json
{
  "message": "Forecast Internet and Reseller revenue for the next 6 months and explain seasonal trends."
}
```

Combined request:

```json
{
  "message": "Forecast Mountain Bikes for next month and draft a promotional email for customers who purchased Mountain Bikes last quarter about an upcoming bike accessory sale."
}
```

The combined request should set both routing flags to `true`, execute both specialists, and return `multi_agent_fan_out`.

## 9. Output contract

```json
{
  "request": "Original user question",
  "execution_mode": "single_specialist or multi_agent_fan_out",
  "results": [],
  "skipped_agents": [],
  "human_approval_required": false
}
```

Each completed result identifies its agent and status. Campaign results can contain an audience description and reusable email drafts. `human_approval_required` becomes `true` when generated campaign content requires review.

## 10. Security and governance

- Limits the SQL credential to `SELECT` on required warehouse objects.
- Stores API secrets in n8n credentials, never workflow exports or browser code.
- Keeps live customer and sales facts in SQL Server rather than Pinecone.
- Do not store customer contact data, individual purchases, or generated drafts in Pinecone.
- Retrieve only Pinecone records with `approved = true`.
- Require human review before sending any generated campaign.
- Use HTTPS, authentication, appropriate CORS, and rate limits for production exposure.

## 11. Testing checklist

- Sales-only requests complete the sales agent and skip the customer agent.
- Customer-only requests complete the customer agent and skip the sales agent.
- Combined requests execute and aggregate both specialists.
- `Internet` and `Reseller` are treated as channels, not product subcategories.
- Named subcategories such as `Mountain Bikes` remain filters.
- Empty SQL results produce a clear no-data response.
- Pinecone uses namespace `AskJarvisSCM` and `approved = true`.
- SQL, OpenAI, and Pinecone nodes use working n8n credentials.
- Test URLs are used while listening; production URLs are used while the router is active.

## 12. Limitations and future enhancements

- The forecast is a transparent seasonal baseline rather than a trained model.
- Churn risk is an inactivity heuristic rather than a calibrated probability.
- Relative dates should use the warehouse's latest transaction date because AdventureWorks contains historical sample data.
- Add forecast backtesting, error metrics, confidence intervals, and automated evaluation.
- Add authentication, observability, retry policies, and rate limiting.
- Add a formal campaign approval workflow and audit trail.

