# Problem Statement: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Overview

The objective of this project is to build a **facts-only FAQ assistant** for mutual fund schemes, using **Groww** as the reference product context. The assistant will answer objective, verifiable queries related to mutual funds by retrieving information exclusively from official public sources, such as AMC (Asset Management Company) websites, AMFI, and SEBI.

> [!IMPORTANT]
> The system must **strictly avoid** providing investment advice, opinions, or recommendations. Every response must include a single, clear source link and adhere to defined constraints around clarity, accuracy, and compliance.

---

## Objective

Design and implement a lightweight **Retrieval-Augmented Generation (RAG)**-based assistant that:

- Answers factual queries about mutual fund schemes
- Uses a curated corpus of official documents
- Provides concise, source-backed responses

---

## Target Users

| User Segment | Use Case |
|---|---|
| Retail investors | Comparing mutual fund schemes |
| Customer support & content teams | Handling repetitive mutual fund queries |

---

## Scope of Work

### 1. Corpus Definition

- **Selected AMC:** HDFC Mutual Fund
- **Number of Schemes:** 5 (covering diverse fund categories)

#### Source URLs (Confirmed)

The following **5 Groww fund pages** have been identified as the primary corpus sources:

| # | Fund Name | Category | Expense Ratio | Source URL |
|---|---|---|---|---|
| 1 | HDFC Gold ETF Fund of Fund – Direct Plan Growth | Commodity – Gold | 0.20% | https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth |
| 2 | HDFC Large Cap Fund – Direct Growth | Equity – Large Cap | 1.02% | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 3 | HDFC Small Cap Fund – Direct Growth | Equity – Small Cap | 0.76% | https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth |
| 4 | HDFC Silver ETF FoF – Direct Growth | Commodity – Silver | 0.22% | https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth |
| 5 | HDFC Mid Cap Fund – Direct Growth | Equity – Mid Cap | 0.75% | https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth |

#### Additional Official Sources to Collect

Beyond the Groww pages above, the corpus should also include the following official document types (sourced from AMC / AMFI / SEBI):

- **Scheme Factsheets** – monthly PDFs from HDFC AMC website
- **KIM (Key Information Memorandum)** – per scheme, from HDFC AMC
- **SID (Scheme Information Document)** – per scheme, from HDFC AMC
- **AMC FAQ / Help Pages** – [HDFC Mutual Fund Help Centre](https://www.hdfcfund.com)
- **AMFI Guidance Pages** – [amfiindia.com](https://www.amfiindia.com)
- **SEBI Investor Education** – [sebi.gov.in](https://www.sebi.gov.in)
- **Statement & Tax Document Guides** – Capital gains report download guides

> [!NOTE]
> These 5 schemes span **Equity** (Large Cap, Mid Cap, Small Cap) and **Commodity** (Gold ETF FoF, Silver ETF FoF) categories, providing meaningful diversity for the FAQ corpus. Groww pages serve as the primary reference; supplementary official documents ensure factual completeness.

### 2. FAQ Assistant Requirements

The assistant must answer **facts-only queries**, such as:

- Expense ratio of a scheme
- Exit load details
- Minimum SIP amount
- ELSS lock-in period
- Riskometer classification
- Benchmark index
- Process to download statements or capital gains reports

**Response rules:**

| Rule | Detail |
|---|---|
| Length | Maximum of **3 sentences** per response |
| Citation | Exactly **one citation link** per response |
| Footer | `"Last updated from sources: <date>"` |

### 3. Refusal Handling

The assistant must **refuse** non-factual or advisory queries, such as:

- *"Should I invest in this fund?"*
- *"Which fund is better?"*

Refusal responses should:

- Be polite and clearly worded
- Reinforce the facts-only limitation
- Provide a relevant educational link (e.g., AMFI or SEBI resource)

### 4. User Interface (Minimal)

The solution should include a simple interface with:

- A **welcome message**
- **Three example questions**
- A visible disclaimer: `"Facts-only. No investment advice."`

---

## Constraints

### Data and Sources

- Use **only** official public sources (AMC, AMFI, SEBI)
- Do **not** use third-party blogs or aggregator websites

### Privacy and Security

> [!CAUTION]
> Do **not** collect, store, or process any of the following:
> - PAN or Aadhaar numbers
> - Account numbers
> - OTPs
> - Email addresses or phone numbers

### Content Restrictions

- No investment advice or recommendations
- No performance comparisons or return calculations
- For performance-related queries, provide a link to the official factsheet only

### Transparency

- Responses must be short, factual, and verifiable
- Every answer must include a **source link** and **last updated date**

---

## Expected Deliverables

### README Document

- Setup instructions
- Selected AMC and schemes
- Architecture overview (RAG approach)
- Known limitations

### Disclaimer Snippet

```
"Facts-only. No investment advice."
```

---

## Success Criteria

- [x] Accurate retrieval of factual mutual fund information
- [x] Strict adherence to facts-only responses
- [x] Consistent inclusion of valid source citations
- [x] Proper refusal of advisory queries
- [x] Clean, minimal, and user-friendly interface

---

## Summary

> The goal is to build a **trustworthy, transparent, and compliant** mutual fund FAQ assistant that prioritizes **accuracy over intelligence**. The system should ensure that users receive only verified, source-backed financial information, without any advisory bias or speculative content.
