# AskJarvisSCM Pinecone metadata

Index: `adventureworks-catalog`  
Namespace: `AskJarvisSCM`

The namespace contains durable grounding knowledge, not live warehouse rows.
SQL Server remains authoritative for all sales, products and customer values etc

## Metadata fields

| Field | Purpose |
|---|---|
| `document_id` | Stable, unique document identifier |
| `document_type` | Catalog, relationship, metric, rule, policy, or SQL example |
| `domain` | `shared`, `sales_forecasting`, or `customer_analytics` |
| `agent` | `sales_forecast`, `customer_intelligence_campaign`, or `both` |
| `source_database` | `AdventureWorksDW2022` |
| `source_system` | `AdventureWorksDW` |
| `schema_name` | SQL schema |
| `table_name` | Unqualified primary table name when applicable |
| `qualified_table_name` | Schema-qualified primary table |
| `relevant_tables` | String array of tables needed for the definition |
| `analysis_type` | String array such as `forecast`, `seasonality`, or `rfm` |
| `metric` | String array of calculated measures |
| `sales_channel` | String array containing `internet`, `reseller`, or `combined` |
| `time_grain` | String array of supported date groupings |
| `product_level` | String array containing product, subcategory, or category |
| `segment` | String array of applicable customer segments |
| `risk_level` | String array of applicable churn-risk levels |
| `communication_type` | String array such as `re_engagement_email` |
| `forecast_method` | String array of approved forecasting methods |
| `contains_pii` | Whether the source table can contain personal information |
| `approved` | Only approved documents should ground production responses |
| `sql_dialect` | `tsql` |
| `catalog_version` | Knowledge-definition version |
| `language` | Document language |

The seeder's **Normalize Filter Arrays** node converts all multi-value fields to
Pinecone-compatible arrays of strings before they reach the Default Data Loader.
Empty multi-value fields are stored as empty arrays. Scalar identifiers,
booleans, versions, and language fields remain scalar values.

## Document types seeded

- `table_catalog`
- `relationship_catalog`
- `metric_definition`
- `forecast_definition`
- `segmentation_rule`
- `communication_policy`
- `data_quality_rule`
- `verified_sql_example`

## Recommended retrieval filters

Sales specialist:

```json
{
  "$and": [
    {"approved": {"$eq": true}},
    {"agent": {"$in": ["sales_forecast", "both"]}}
  ]
}
```

Customer specialist:

```json
{
  "$and": [
    {"approved": {"$eq": true}},
    {"agent": {"$in": ["customer_intelligence_campaign", "both"]}}
  ]
}
```

Customer RFM retrieval:

```json
{
  "$and": [
    {"approved": {"$eq": true}},
    {"agent": {"$in": ["customer_intelligence_campaign", "both"]}},
    {"analysis_type": {"$in": ["rfm"]}}
  ]
}
```

Sales seasonality retrieval:

```json
{
  "$and": [
    {"approved": {"$eq": true}},
    {"agent": {"$in": ["sales_forecast", "both"]}},
    {"analysis_type": {"$in": ["seasonality"]}}
  ]
}
```

If the Pinecone/n8n version does not accept `$in`, issue two filtered searches
(`agent = specialist` and `agent = both`) and merge the highest-scoring matches.

## Security boundary

Do not upsert customer names, email addresses, demographics, individual purchase
rows, current revenue, or generated email drafts. Retrieve changing facts from
SQL Server for each request and use Pinecone only to ground definitions, joins,
policies, and approved query patterns.
