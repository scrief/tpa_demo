# Project Brief: TPA Match Demo

## Working name

TPA Match Demo

## Purpose

Build a small, credible demo app that matches a buyer/client with TPA or claims vendors based on structured vendor data, buyer needs, scoring logic, AI-assisted explanations, and validation controls.

This project is designed to demonstrate practical competency in:

- messy multi-source data intake
- data cleaning and canonicalization
- SQL/data modeling fundamentals
- matching and ranking logic
- AI-assisted request parsing and explanation
- validation/evals
- human-in-the-loop review
- security-aware and accessible app design

## Product thesis

The app should answer:

> Given this buyer's risk profile, claims needs, geography, service expectations, and priorities, which TPA/vendor is the best fit, and why?

## What this is not

This is not a black-box AI agent that decides everything.

This is a structured matching system with optional AI assistance.

AI can help with:

- interpreting natural language buyer requests into structured criteria
- summarizing recommendation explanations from structured reason codes
- helping identify missing information or follow-up questions

AI should not be the sole decision-maker for vendor ranking.

## MVP user flow

1. User enters a buyer request in natural language.
2. App extracts or asks for structured buyer criteria.
3. App applies hard filters to remove disqualified vendors.
4. App scores eligible vendors using weighted categories.
5. App displays ranked vendor matches.
6. App shows reason codes, warnings, missing data, and confidence indicators.
7. App generates a plain-English explanation grounded only in available vendor data.
8. User can rate the match and provide feedback.
9. Feedback is saved for future validation and scoring improvements.

## Example buyer request

> We need a workers' compensation TPA for a self-insured manufacturing client with locations in Minnesota, Wisconsin, and Iowa. Return-to-work support, reporting, and faster claim response are major priorities. They currently have service issues with their existing TPA.

## Example output

1. NorthStar Claims - Score: 88/100
   - Serves MN, WI, and IA
   - Workers' compensation is a primary focus
   - Manufacturing experience documented
   - Strong return-to-work support
   - Reporting data is available
   - Human review recommended because API integration information is missing

## Success criteria

A successful version 1 should:

- use realistic but fake data
- clean messy raw vendor files into a canonical vendor dataset
- allow structured matching against buyer needs
- produce ranked results with scores and reason codes
- clearly flag missing/stale/conflicting data
- include basic validation tests with expected good and bad matches
- have security and accessibility considered from the start
- be simple enough that Scott can explain the architecture in an interview

## Interview story

The project should support this explanation:

> I built this to practice the core workflow of a trust-sensitive AI/data product: ingest messy data, normalize it into a canonical model, apply transparent matching logic, generate grounded explanations, validate the outputs, and improve the system with feedback.
