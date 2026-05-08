# TPA Match Demo - Project Source of Truth

This folder is the working source of truth for the TPA Match Demo project. It is intended to be passed into Cursor/Carly as project context before coding begins.

## Recommended reading order

1. `01_project_brief.md` - what we are building and why
2. `02_data_model.md` - vendor fields, buyer request fields, and normalized data concepts
3. `03_matching_logic.md` - hard filters, scoring, reason codes, and ranking logic
4. `04_validation_rules.md` - data validation, AI validation, testing, and eval rules
5. `05_security_accessibility.md` - security, privacy, and ADA/WCAG accessibility requirements
6. `06_build_checklist.md` - working implementation checklist
7. `07_cursor_agent_instructions.md` - instructions for the coding agent

## Core product principle

Build a structured decision-support system, not a black-box chatbot.

AI may help interpret a buyer request and explain the result, but the actual vendor ranking should be based on inspectable data fields, hard filters, weighted scoring, validation rules, and human review flags.

# TPA Match Demo — Project Vision and Technical Direction

## Project Purpose

This project is a prototype decision-support platform for matching employers/buyers with the most appropriate Third-Party Administrator (TPA) or claims vendor based on operational needs, geography, claims profile, industry fit, service capabilities, reporting expectations, and performance signals.

The purpose is NOT to build a generic chatbot.

The purpose is to build a trustworthy, explainable, structured matching system with AI-assisted interpretation and explanation layers.

The system should demonstrate:

* messy multi-source data ingestion
* canonical data modeling
* relational database design
* SQL querying
* scoring/ranking logic
* explainable AI outputs
* validation/evaluation workflows
* security-conscious design
* accessibility-aware UI development

This project is intended both as:

1. A portfolio/interview project
2. A learning vehicle for Python, SQL, data modeling, and AI workflows

---

# High-Level Architecture

## System Flow

### Step 1 — Buyer Request Intake

User enters:

* natural language request
* structured form fields
* or both

Example:

> "We need a workers compensation TPA for a self-insured manufacturing client in MN/WI/IA with strong return-to-work and reporting capabilities."

---

### Step 2 — Structured Extraction Layer

The system converts natural language into structured buyer criteria.

Example structured output:

```json
{
  "industry": "manufacturing",
  "states_needed": ["MN", "WI", "IA"],
  "claim_type_needed": "workers_comp",
  "required_services": [
    "return_to_work",
    "dashboard_reporting"
  ]
}
```

This may initially be hardcoded/rules-based and later enhanced with AI extraction.

---

### Step 3 — Relational Query Layer

The system queries structured vendor data stored in SQLite/Postgres.

The system should:

* filter vendors
* apply hard exclusions
* compare capabilities
* identify gaps
* calculate scores
* produce structured reason codes

The database is the source of truth.

AI should NOT independently determine vendor rankings.

---

### Step 4 — Matching and Scoring Engine

The system calculates weighted scores across multiple dimensions.

Examples:

* geographic fit
* claim type fit
* industry experience
* service capabilities
* reporting capabilities
* technology fit
* performance metrics
* data quality confidence

The scoring system must remain:

* deterministic
* inspectable
* explainable
* testable

---

### Step 5 — AI Explanation Layer (Phase 9)

After scoring is complete, AI generates human-readable explanations from structured reason codes.

AI explanations MUST:

* only reference existing structured data from vendor records
* never hallucinate capabilities or invent information
* disclose missing or low-confidence data explicitly
* recommend human review when uncertainty exists
* be grounded in reason codes and match results

**Critical principle:** AI is an explanation layer, NOT the decision engine.

The matching engine remains deterministic and rules-based. AI assists with:
1. Parsing natural language buyer requests into structured criteria
2. Converting structured reason codes into plain English explanations
3. Identifying missing information and suggesting follow-up questions

---

### Step 6 — Validation and Evaluation Layer

The platform must support evaluation workflows.

The system should:

* compare expected vs actual recommendations
* log failures
* identify hallucinations
* track missing data issues
* support human review
* allow iterative scoring improvements

Validation is a first-class feature of the system.

---

# Core Design Philosophy

## Primary Principles

### Trust over novelty

The system should prioritize reliable, explainable outputs over “AI magic.”

### Structured-first architecture

Structured data and deterministic logic are the foundation.

### Human-in-the-loop

The system should support review, overrides, and feedback.

### Transparency

The system should expose:

* why vendors ranked
* what data was used
* what data is missing
* where confidence is weak

### Auditability

All recommendations should be explainable and reproducible.

---

# Tech Stack Direction

## Initial Stack

### Backend

* Python
* SQLite
* pandas

### App/UI

* Streamlit

### Database

* SQLite initially
* Postgres later if needed

### AI

* OpenAI API later for explanation generation only

---

# Database Philosophy

The schema should model:

* vendors
* vendor states
* vendor claim types
* vendor industries
* vendor services
* buyer requests
* buyer required states
* buyer required services
* match results
* validation results

The schema should favor:

* normalization
* relational integrity
* inspectable relationships
* clean querying
* future extensibility

---

# Security Considerations

Security should be considered from the beginning.

## Required Practices

### Input validation

Validate:

* user input
* state codes
* scores
* dates
* uploaded files

### SQL injection prevention

Always use parameterized queries.

### Secrets management

Do NOT hardcode:

* API keys
* credentials
* tokens

Use:

* `.env`
* environment variables

### Principle of least privilege

Limit DB access appropriately.

### Logging

Avoid logging sensitive user information.

### Data provenance

Track:

* source
* confidence
* verification status
* last updated date

### Future considerations

Potential future enhancements:

* authentication
* RBAC
* encryption
* audit logs
* SOC2-aligned practices

---

# ADA / Accessibility Considerations

Accessibility should be intentionally designed into the UI from the beginning.

## Requirements

### Keyboard accessibility

All controls should be keyboard navigable.

### Semantic structure

Use:

* proper headings
* labels
* logical hierarchy

### Color contrast

Meet WCAG contrast guidelines.

### Screen reader compatibility

Inputs and buttons should have clear labels.

### Error messaging

Validation errors should:

* be descriptive
* not rely only on color

### Responsive layout

Support different screen sizes and zoom levels.

### Focus states

Visible focus indicators should exist.

---

# MVP Scope

## MVP Features

### Vendor database

Structured vendor records.

### Buyer intake form

Natural language + structured fields.

### Matching engine

Weighted scoring system.

### Match results

Ranked recommendations with reasons.

### AI explanation layer

Optional GPT-generated summaries.

### Validation dashboard

Expected vs actual testing.

### Feedback logging

Capture user review feedback.

---

# Explicit Non-Goals (for MVP)

Do NOT initially build:

* multi-user auth
* cloud infrastructure
* embeddings/vector search
* advanced AI agents
* autonomous workflows
* production-scale APIs
* full React frontend
* real vendor integrations

Focus on:

* clean architecture
* understandable logic
* learning fundamentals
* explainability

---

# What Success Looks Like

The finished MVP should allow a user to:

1. Enter a buyer scenario
2. Retrieve ranked vendor recommendations
3. Understand WHY vendors ranked
4. See missing data or risk flags
5. Validate recommendation quality
6. Demonstrate structured data modeling and AI-assisted workflow design

The project should communicate:

* strong systems thinking
* understanding of messy operational data
* trust-sensitive AI design
* structured data modeling
* validation/evaluation awareness
* practical product thinking

This is NOT intended to demonstrate elite software engineering.

It IS intended to demonstrate:

* practical architecture thinking
* data workflow understanding
* AI product intuition
* operational systems design
* ability to learn technical implementation quickly

