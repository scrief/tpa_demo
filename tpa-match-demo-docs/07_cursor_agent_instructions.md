# Cursor/Carly Agent Instructions

## Role

You are helping build the TPA Match Demo. Prioritize learning, clean structure, explainability, validation, security, and accessibility over speed or fancy features.

## Build philosophy

Do not create a black-box AI chatbot.

Build a structured decision-support app where:

- data cleaning is explicit
- matching logic is inspectable
- scores are explainable
- reason codes are generated
- missing/stale/conflicting data is flagged
- AI is optional and grounded
- validation tests prove behavior

## Important behavior rules

1. Do not build everything in one giant file.
2. Do not skip documentation.
3. Do not hardcode API keys or secrets.
4. Do not use real client or claim data.
5. Do not let the AI explanation invent unsupported facts.
6. Do not rely only on color for warnings.
7. Do not concatenate raw user input into SQL queries.
8. Do not move to AI features until the rules-based matching engine works.

## Recommended build order

Follow this order:

1. Project setup
2. Synthetic messy CSVs
3. Data inspection script
4. Cleaning/canonicalization script
5. SQLite loading and basic queries
6. Buyer scenarios
7. Matching engine
8. Validation/eval script
9. Streamlit app
10. Optional AI parser/explanation layer
11. Security/accessibility polish
12. Documentation and interview prep

## Preferred tech stack

- Python
- pandas
- SQLite
- Streamlit
- Optional OpenAI API for parsing/explanation
- pytest optional for tests

## Code structure

Use this structure:

```text
tpa-match-demo/
  README.md
  requirements.txt
  .gitignore
  .env.example
  data/
    raw/
    clean/
  database/
  scripts/
    inspect_data.py
    clean_data.py
    load_database.py
    score_matches.py
    run_evals.py
  app/
    streamlit_app.py
  prompts/
    buyer_request_parser_prompt.md
    recommendation_explanation_prompt.md
  docs/
  tests/
```

## Learning mode requirements

When adding code, include clear comments explaining:

- what the function does
- what inputs it expects
- what it returns
- why the step matters

Prefer simple readable code over advanced clever code.

When a major script is created, include a short explanation in comments at the top.

## Matching engine requirements

The matching engine must return:

- ranked vendors
- total score
- category score breakdown
- reason codes
- warning codes
- human-review flag
- disqualified vendors and reasons

## AI requirements

AI features must be optional.

If no API key is present, the app should still work using:

- structured form fields
- rules-based matching
- template-based explanations

AI parser output must be valid JSON and match the expected schema.

AI explanation input should be limited to:

- buyer criteria
- vendor name
- score breakdown
- reason codes
- warning codes
- selected vendor fields

AI explanation must not invent facts.

## Security requirements

- Use synthetic data only.
- Use `.env` for secrets.
- Include `.env.example`.
- Exclude `.env` from Git.
- Avoid unsafe SQL string concatenation.
- Validate user input.
- Send minimal data to AI.

## Accessibility requirements

- Use clear labels for every input.
- Use headings in logical order.
- Use text-based warnings.
- Do not rely on color alone.
- Provide specific error messages.
- Use clear table headers.
- Keep advanced details expandable.

## Definition of done for MVP

The MVP is done when:

- synthetic messy data exists
- canonical vendor dataset is generated
- SQLite database loads successfully
- matching engine returns ranked results
- validation script runs at least 20 scenarios
- Streamlit app displays recommendations
- feedback can be saved
- security/accessibility checklist is mostly complete
- README explains the project clearly
