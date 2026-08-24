# Solution Architecture

## 1. Objective

The project combines an intelligent data catalog and a Text-to-SQL assistant for Microsoft AdventureWorksDW. Retrieval provides relevant schema definitions, relationships, glossary entries, and curated SQL examples before the language model answers a question or generates SQL.

## 2. Major components

### SQL Server Express

Hosts `AdventureWorksDW`. n8n connects through a dedicated read-only login. The account is the final database-level control even if an earlier application check fails.

### Catalog ingestion workflow

The ingestion workflow generates table and relationship documents, merges them with curated glossary definitions and SQL examples, normalizes the document structure, splits content when required, creates embeddings, and writes the records to Pinecone namespace `adventureworks-v1`.

The completed namespace contains 43 records: generated schema documents plus curated business glossary and SQL-example documents.

### Pinecone retrieval

The question is embedded using the same embedding family used during ingestion. Pinecone returns ranked catalog documents. n8n aggregates `document.pageContent` values and builds a grounded context block for downstream prompts.

### Question classifier

The classifier routes each question into one of three paths:

1. `catalog` - schema discovery, definitions, columns, and relationships.
2. `sql` - analytical requests that should produce read-only T-SQL.
3. `unsupported` - destructive, administrative, unrelated, or otherwise out-of-scope requests.

### Catalog answer path

The model answers only from retrieved context. Insufficient context produces a safe insufficiency response rather than an invented schema answer.

### SQL generation path

The model returns structured output containing status, answer, SQL, tables used, assumptions, and citations. A separate validation step checks the SQL before an execution decision is made.

### SQL safety validation

The validation layer enforces the following invariants:

- Only read-only queries can become execution-eligible.
- Non-ready statuses must contain empty validated SQL.
- Destructive or administrative keywords are blocked.
- Multi-statement or disguised data-modification attempts are blocked.
- Referenced tables must be permitted AdventureWorksDW objects.
- Execution requires both successful validation and non-empty `validated_sql`.

### Result formatting

Eligible SQL is executed by the SQL Server node. A formatting step converts database rows into a user-facing response and preserves relevant citations. Blocked and clarification responses bypass the database.

## 3. Data flow

```text
Chat question
  -> Normalize question
  -> Classify intent
  -> Retrieve ranked Pinecone documents
  -> Aggregate document.pageContent
  -> Build grounded context
  -> Catalog answer OR structured SQL generation
  -> Independent SQL validation
  -> Execute only when eligible
  -> Format final chat response
```

## 4. Trust boundaries

| Boundary | Control |
|---|---|
| User to model | Intent classification and scoped prompts |
| Model to SQL | Structured output and independent JavaScript validation |
| n8n to database | Dedicated read-only SQL Server credential |
| Retrieval to response | Context-only answering and source identifiers |
| Unsupported request | No execution branch and safe response |

## 5. Configuration inventory

| Item | Current MVP value |
|---|---|
| Database | AdventureWorksDW on SQL Server Express |
| n8n deployment | Local Docker container |
| Docker-to-host connection | `host.docker.internal` or verified reachable host value |
| Vector namespace | `adventureworks-v1` |
| Indexed records | 43 |
| Embedding model | `text-embedding-3-small` |
| Classifier model | `gpt-5.4-nano`, with tested fallback to `gpt-5-mini` |
| Generation model | Tested OpenAI chat model configured in n8n |
| Database authorization | Read-only account |

## 6. Future enhancements

- Schedule catalog refreshes and detect schema changes.
- Add automated batch evaluation and retrieval-quality metrics.
- Add conversation memory for follow-up analytical questions.
- Introduce query cost limits, timeouts, and row-limit enforcement.
- Expand the curated glossary and approved SQL examples.
- Add user feedback capture and failed-question review.

