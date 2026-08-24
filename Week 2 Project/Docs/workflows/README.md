# n8n Workflows

These workflows implement a retrieval-augmented data catalog and read-only Text-to-SQL assistant for the AdventureWorksDW Internet Sales domain.

## Workflow Overview

| File | Purpose | Trigger |
|---|---|---|
| [`02 Generate Catalog Documents.json`](02%20Generate%20Catalog%20Documents.json) | Reads AdventureWorksDW table metadata and foreign-key relationships, then indexes catalog documents. | Manual n8n execution |
| [`03_Generate Curated Internet Sales Knowledge.json`](03_Generate%20Curated%20Internet%20Sales%20Knowledge.json) | Creates business glossary definitions and approved SQL examples, then indexes them. | Manual n8n execution |
| [`Intelligent Data Catalog and Text-to-SQL Assistant.json`](Intelligent%20Data%20Catalog%20and%20Text-to-SQL%20Assistant.json) | Classifies chat questions, retrieves relevant catalog context, answers catalog questions, or generates and safely executes read-only SQL. | n8n Chat Trigger |

The first two workflows populate the shared Pinecone collection. The assistant workflow depends on that indexed content, so run the ingestion workflows before using chat.

## Architecture

```text
AdventureWorksDW
  |-- table and relationship metadata --> Catalog document ingestion
  |-- glossary and SQL examples -------> Curated knowledge ingestion
                                           |
                                           v
                              Pinecone: adventureworks-catalog
                              Namespace: adventureworks-v1
                                           |
Chat question --> classify --> retrieve context --> catalog answer
                                      |
                                      +--> structured SQL --> validate --> execute or block
```

## Prerequisites

- n8n with the LangChain nodes used by the exported workflows.
- SQL Server hosting the `AdventureWorksDW` database.
- A read-only SQL Server credential named `AdventureWorks-ReadOnly`.
- An OpenAI credential named `OpenAI Credential`.
- A Pinecone credential named `Pinecone AdventureWorks`.
- A Pinecone index named `adventureworks-catalog` configured for the same embedding dimensions used by the workflows: `1536`.
- Access to the AdventureWorksDW Internet Sales tables:
  `DimCurrency`, `DimCustomer`, `DimDate`, `DimGeography`, `DimProduct`,
  `DimProductCategory`, `DimProductSubcategory`, `DimPromotion`,
  `DimSalesTerritory`, and `FactInternetSales`.

The credential names are the names stored in the exports; credential IDs are instance-specific and must be mapped when importing into another n8n instance.

## Setup and Execution

1. Import all three JSON files into n8n.
2. Map or create the SQL Server, OpenAI, and Pinecone credentials listed above.
3. Confirm the Pinecone index and namespace are available:
   - Index: `adventureworks-catalog`
   - Namespace: `adventureworks-v1`
   - Embedding dimensions: `1536`
4. Execute `02 Generate Catalog Documents` manually. It reads table definitions and active foreign-key relationships, normalizes the records, splits documents into 4,000-character chunks with 200-character overlap, and inserts them into Pinecone.
5. Execute `03_Generate Curated Internet Sales Knowledge` manually. It adds glossary documents for Internet Sales concepts and curated read-only SQL examples to the same namespace.
6. Open the chat trigger for `Intelligent Data Catalog and Text-to-SQL Assistant` and submit a question about the catalog or Internet Sales data.

The exported workflows are inactive (`active: false`), so they require manual execution or explicit activation in the target n8n instance.

## Assistant Behavior

The chat workflow retrieves catalog documents from Pinecone and includes document IDs, document types, table names, similarity scores, and content in the grounded prompt.

Questions are classified into three categories:

- **catalog**: table and column discovery, definitions, grain, keys, relationships, join paths, and metric explanations. The answer is grounded in retrieved context and cites document IDs.
- **sql**: read-only analytical requests such as totals, counts, rankings, comparisons, and grouped summaries. The model returns structured status, answer, SQL, tables, assumptions, and citations.
- **unsupported**: requests outside the AdventureWorksDW Internet Sales scope or requests that modify data or database objects. These receive a response without SQL generation or execution.

Catalog retrieval uses up to 5 results for catalog answers and up to 8 results for SQL generation. Both paths use the shared `adventureworks-v1` namespace and OpenAI embeddings with 1,536 dimensions.

## SQL Safety

Generated SQL is independently checked by the `Validate SQL Safety` code node before execution. Execution requires all of the following:

- The generated status is `ready`.
- The query is a single read-only statement beginning with `SELECT` or `WITH`.
- The query does not contain blocked data-modification, administrative, permission, or dynamic-SQL keywords.
- The query uses only the allowlisted, schema-qualified AdventureWorksDW tables.
- The validated SQL is non-empty.

Blocked, unsupported, clarification, and database-error paths return a formatted chat response. Successful results are formatted as Markdown with at most 20 displayed rows and 8 displayed columns.

## Model Configuration

- Classifier: `gpt-5.4-nano`
- SQL and catalog response generation: `gpt-5-mini`
- Embeddings: OpenAI embeddings configured for `1536` dimensions
- Text splitting: Recursive Character Text Splitter, chunk size `4000`, overlap `200`

## Example Questions

- Which table contains Internet sales?
- How does `FactInternetSales` connect to `DimProductCategory`?
- What is Internet Sales Revenue?
- Show Internet sales revenue by year.
- List the top 10 products by sales.

Requests such as `DELETE`, `UPDATE`, `DROP`, database administration, employee payroll, or unrelated domains are intentionally rejected.

## Related Documentation

- [Solution architecture](../docs/architecture.md)
- [Project screenshots](../screenshots/README.md)
