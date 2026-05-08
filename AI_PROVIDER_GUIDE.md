# AI Provider Guide: OpenAI vs Google Gemini

## Quick Comparison

| Feature | OpenAI GPT | Google Gemini | Recommendation |
|---------|-----------|---------------|----------------|
| **Parsing** | gpt-4o | gemini-1.5-pro | Either (Gemini cheaper) |
| **Explanations** | gpt-4o-mini | gemini-1.5-flash | Gemini (much cheaper) |
| **Cost per 1K tokens (input)** | $2.50-$5.00 | $0.00-$1.25 | Gemini wins |
| **Cost per 1K tokens (output)** | $10.00-$15.00 | $0.00-$5.00 | Gemini wins |
| **Setup complexity** | Easy | Easy | Tie |
| **Free tier** | $5 credit | Generous | Gemini wins |
| **Rate limits** | Strict | Generous | Gemini wins |

## Cost Comparison (Per Match Request)

### OpenAI Pricing
- **Parsing (gpt-4o):** ~$0.02-0.03
- **Explanations (gpt-4o-mini, 3-5 vendors):** ~$0.015-0.05
- **Total: $0.035-0.08 per request**

### Gemini Pricing
- **Parsing (gemini-1.5-pro):** ~$0.005-0.01
- **Explanations (gemini-1.5-flash, 3-5 vendors):** ~$0.001-0.005
- **Total: $0.006-0.015 per request**

**Gemini is 5-8x cheaper!** 💰

### Monthly Estimates (100 requests)
- **OpenAI:** $3.50-8.00/month
- **Gemini:** $0.60-1.50/month

---

## Setup Instructions

### Option 1: Using Google Gemini (Recommended)

**Step 1: Get API Key**
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Get API key"
4. Copy your API key

**Step 2: Configure**
```bash
# Copy template
cp .env.template .env

# Edit .env file:
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_actual_key_here
GEMINI_PARSING_MODEL=gemini-1.5-pro
GEMINI_EXPLANATION_MODEL=gemini-1.5-flash
```

**Step 3: Install**
```bash
pip install google-generativeai
```

**Step 4: Launch**
```bash
streamlit run app.py
```

### Option 2: Using OpenAI

**Step 1: Get API Key**
1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy your API key

**Step 2: Configure**
```bash
# Copy template
cp .env.template .env

# Edit .env file:
AI_PROVIDER=openai
OPENAI_API_KEY=your_actual_key_here
OPENAI_PARSING_MODEL=gpt-4o
OPENAI_EXPLANATION_MODEL=gpt-4o-mini
```

**Step 3: Install**
```bash
pip install openai
```

**Step 4: Launch**
```bash
streamlit run app.py
```

---

## Model Selection Guide

### For Parsing (Converting Natural Language to Structured Data)

**Best Choice: Gemini 1.5 Pro**
- Excellent accuracy on structured extraction
- 5-10x cheaper than GPT-4o
- Generous free tier
- Better JSON formatting

**Alternative: GPT-4o**
- Slightly better on ambiguous inputs
- More expensive
- Good if you already have OpenAI credits

### For Explanations (Generating Plain-English Text)

**Best Choice: Gemini 1.5 Flash**
- Fast and cheap
- Quality sufficient for explanations
- Great for high-volume usage

**Alternative: GPT-4o-mini**
- Slightly more consistent tone
- More expensive
- Good if you need OpenAI ecosystem

---

## Quality Comparison

### Parsing Accuracy (Expected)
- **Gemini 1.5 Pro:** 80-85% on core fields
- **GPT-4o:** 85-90% on core fields
- **Winner:** GPT-4o (slight edge)

### Explanation Quality
- **Gemini 1.5 Flash:** Clear, professional, grounded
- **GPT-4o-mini:** Clear, professional, grounded
- **Winner:** Tie (both excellent)

### Hallucination Rate
- **Gemini:** Slightly higher (need good prompting)
- **GPT:** Slightly lower
- **Winner:** GPT (but hallucination detector catches both)

---

## Switching Between Providers

You can switch anytime by changing the `.env` file:

```bash
# Switch to Gemini
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_key

# Switch to OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=your_key
```

Restart the app after changing.

---

## Recommendations

### For Development/Testing
**Use: Gemini**
- Cheaper for experimentation
- Generous free tier
- Fast iteration

### For Production (Low Volume < 100/month)
**Use: Either**
- Both work well
- Cost difference minimal at low volume
- Pick based on existing account

### For Production (High Volume > 1000/month)
**Use: Gemini**
- Significant cost savings
- Better rate limits
- Quality is excellent

### For Maximum Accuracy
**Use: OpenAI GPT-4o for parsing only**
- Use Gemini Flash for explanations
- Best quality where it matters
- Optimize cost where it doesn't

---

## Troubleshooting

### Gemini Issues

**"Invalid API key"**
- Check key copied correctly from https://aistudio.google.com/
- No spaces before/after key
- Key should start with "AIza..."

**"Quota exceeded"**
- Free tier: 15 requests per minute
- Paid tier: 360 requests per minute
- Add billing to increase limits

**"Model not found"**
- Use `gemini-1.5-pro` or `gemini-1.5-flash`
- Don't use older model names

### OpenAI Issues

**"Invalid API key"**
- Check key copied correctly from https://platform.openai.com/
- Key should start with "sk-..."

**"Rate limit exceeded"**
- Free tier: 60 requests per minute
- Add payment method to increase
- Or switch to Gemini

**"Insufficient quota"**
- Add credits to account
- Or switch to Gemini (free tier)

---

## Cost Optimization Tips

1. **Use Gemini for both parsing and explanations**
   - 5-8x cheaper overall
   - Quality is excellent

2. **Cache parsed results**
   - Already implemented in session state
   - Avoids re-parsing same text

3. **Generate explanations on-demand only**
   - Already implemented (button click)
   - User only generates what they need

4. **Use Flash for explanations**
   - 10x cheaper than Pro
   - Quality is sufficient

5. **Monitor usage**
   ```bash
   python scripts/add_ai_interactions_table.py stats
   ```

---

## Free Tier Comparison

### Google Gemini Free Tier
- **15 requests per minute**
- **1,500 requests per day**
- **Unlimited monthly (within rate limits)**
- **Perfect for demos and testing**

### OpenAI Free Tier (New Accounts)
- **$5 credit (expires in 3 months)**
- **~60-150 requests at typical usage**
- **Then requires payment**

**Winner: Gemini** (for free usage)

---

## Final Recommendation

**For this TPA Match Demo:**

```bash
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
GEMINI_PARSING_MODEL=gemini-1.5-pro
GEMINI_EXPLANATION_MODEL=gemini-1.5-flash
```

**Why:**
- ✅ 5-8x cheaper
- ✅ Generous free tier
- ✅ Better rate limits
- ✅ Quality is excellent
- ✅ Great for demos

**When to use OpenAI:**
- You already have credits
- Maximum accuracy critical
- Prefer established platform

---

## Testing Both Providers

Want to compare? Test both:

```bash
# Test with Gemini
AI_PROVIDER=gemini python scripts/test_ai_features.py --test parsing

# Test with OpenAI
AI_PROVIDER=openai python scripts/test_ai_features.py --test parsing

# Compare results
```

---

**Bottom Line:** Use Gemini unless you have a specific reason to use OpenAI. The cost savings are significant and quality is excellent for this use case.
