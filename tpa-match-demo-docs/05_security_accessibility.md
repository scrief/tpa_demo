# Security, Privacy, and Accessibility Requirements

## Purpose

Security and accessibility should be considered from the start, even in a demo app. This shows mature product thinking and avoids building bad habits into the architecture.

## Security principles

### Use fake data for the demo

Do not use real client, claim, loss run, vendor contract, broker, employee, claimant, or medical data.

All demo data should be synthetic.

### Protect secrets

API keys and secrets must never be hardcoded in source code.

Use environment variables or a local `.env` file that is excluded from Git.

Required files:

- `.env.example` with placeholder values
- `.gitignore` that excludes `.env`

Example `.gitignore` entries:

```text
.env
__pycache__/
*.db
*.sqlite
.DS_Store
```

### Minimize data sent to AI

If using an AI API, send only the fields needed to generate explanations.

Do not send unnecessary raw notes, personal data, confidential details, or full datasets.

For the MVP, AI should receive:

- buyer request summary
- vendor name
- match score
- reason codes
- missing data flags
- selected structured vendor fields needed for explanation

### Keep matching logic outside the AI

The AI should not make the final recommendation decision.

The deterministic scoring engine should produce the ranking. AI may explain it.

### Validate AI output

AI output should be checked for:

- unsupported capabilities
- overconfident language
- missing required warnings
- invalid or fabricated facts

### Input handling

Treat user input as untrusted.

For MVP:

- avoid executing user-provided code
- validate parsed JSON
- sanitize displayed text
- handle blank/invalid inputs gracefully

### Database safety

Use parameterized queries where applicable. Avoid string-concatenated SQL based on raw user input.

### Local-first MVP

Build locally first using:

- Python
- Streamlit
- SQLite
- synthetic CSV data

Avoid authentication, cloud deployment, and real user accounts in MVP unless truly needed.

### Auditability

Save enough structured output to explain what happened:

- buyer request
- parsed criteria
- vendors considered
- hard filters applied
- scores by category
- reason codes
- warnings
- final result
- user feedback

This supports debugging and trust.

## Privacy considerations

Even though the demo uses synthetic data, design as if future versions could contain sensitive claim or client data.

Avoid storing:

- claimant names
- medical details
- SSNs
- dates of birth
- personal addresses
- confidential client financials
- sensitive claim descriptions

If future real data is used, add:

- access control
- data retention rules
- encryption at rest/in transit
- least privilege access
- logging and monitoring
- documented data handling process

## Accessibility / ADA programming principles

The app should be designed to be usable by people with disabilities. Use WCAG-style practices even in the prototype.

### Keyboard accessibility

All interactive elements should be usable by keyboard.

- forms
- buttons
- tabs
- dropdowns
- feedback controls

### Labels and instructions

Every form input should have a clear label.

Avoid placeholder-only instructions.

Good:

- Label: States needed
- Help text: Enter two-letter state codes such as MN, WI, IA.

### Color contrast

Do not rely only on color to communicate meaning.

For warnings, include text labels/icons such as:

- Warning: Missing reporting data
- Human review recommended

### Screen reader structure

Use clear heading order:

- H1: App title
- H2: Buyer request
- H2: Recommended vendors
- H2: Validation details
- H2: Feedback

### Error messages

Error messages should be specific and text-based.

Poor:

> Invalid input.

Better:

> States needed is required. Use two-letter state codes such as MN, WI, IA.

### Tables

Results tables should have clear column headers.

Recommended columns:

- Rank
- Vendor
- Score
- Match summary
- Warnings
- Human review

### Plain language

Use plain, direct language in recommendations.

Avoid unnecessary technical jargon for end users.

### Reduced cognitive load

Do not overwhelm the user with everything at once.

Use expandable sections for:

- score breakdown
- raw reason codes
- validation details
- source data

### Focus management

After a user submits a buyer request, the page should clearly show results and not leave the user unsure whether anything happened.

### Accessible feedback form

Feedback questions should be direct:

- Was this recommendation useful?
- Was the explanation accurate?
- What was missing?
- Should a different vendor have ranked higher?

## Additional product considerations

### Explainability

Every recommendation should answer:

- Why this vendor?
- What data supports this match?
- What is missing or uncertain?
- What should a human verify next?

### Human-in-the-loop review

The app should clearly flag cases requiring human review.

Examples:

- low score
- stale data
- conflicting source data
- missing required fields
- ambiguous buyer request

### Bias and fairness

Avoid ranking vendors purely on incomplete or stale relationship notes.

Make sure missing data is not treated the same as negative data.

Example:

- `api_access = false` means no API access.
- `api_access = unknown` means missing data and should be flagged, not assumed false.

### Observability for demo

Create simple logs or downloadable result records showing:

- input
- parsed criteria
- scoring breakdown
- final output

This makes the project easier to debug and explain.
