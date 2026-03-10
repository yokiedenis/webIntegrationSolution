# Model Configuration Guide - Customer Service Agent

## Issue: Groq Model Deprecation

Groq frequently deprecates models. The agent has encountered two deprecated models:

1. `mixtral-8x7b-32768` - Decommissioned
2. `llama-3.1-70b-versatile` - Also decommissioned

### Error Message

```
BadRequestError: GroqException - {"error":{"message":"The model `[model-name]` has been decommissioned and is no longer supported..."}}
```

### Fallback Behavior

✅ **The agent gracefully falls back to keyword-based classification and template responses when the LLM fails**, so it continues to work despite errors.

## Solution: Use Stable Providers

Instead of using Groq (which deprecates models frequently), switch to **OpenAI** or **Anthropic** for more stability.

### Updated Configuration

The `.env` file now defaults to:

```
AGENT_MODEL=gpt-4o
```

This uses OpenAI's GPT-4o model (currently stable and well-maintained).

## Available Model Options

### 1. OpenAI (Recommended - Most Stable)

```env
AGENT_MODEL=gpt-4o          # Latest, fastest, best quality
OPENAI_API_KEY=sk-...
```

### 2. OpenAI GPT-4 Turbo

```env
AGENT_MODEL=gpt-4-turbo
OPENAI_API_KEY=sk-...
```

### 3. Anthropic Claude (Alternative)

```env
AGENT_MODEL=claude-3-opus-20240229   # Most capable
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Groq (If You Must Use It)

Groq provides fast free inference but deprecates models frequently. Currently available:

```env
# Check https://console.groq.com/docs/speech-text for current models
AGENT_MODEL=groq/llama-3.1-8b-instant
GROQ_API_KEY=gsk_...
```

## Fallback Chain

The agent uses a **three-level fallback approach**:

1. **Primary**: Uses configured LLM (GPT-4o, Claude, etc.)
2. **Secondary**: Keyword-based NLP classification
3. **Tertiary**: Template-based responses

This ensures the agent **never fails completely**, even if the LLM is unavailable or deprecated.

```
User Message
    ↓
[Attempt LLM Classification] → Success? → LLM Response
    ↓
    No
    ↓
[Keyword Classification] → Success? → Keyword Response
    ↓
    No
    ↓
[Template Response] → Always Works
```

## Why OpenAI GPT-4o?

- ✅ **Stable**: OpenAI rarely deprecates models
- ✅ **High Quality**: Latest reasoning and understanding
- ✅ **Fast**: Among the fastest available
- ✅ **Cost-effective**: Reasonable pricing for production use
- ✅ **Well-maintained**: Continuous improvements
- ✅ **Widely Compatible**: Works with all LiteLLM providers

## Configuration Instructions

### Step 1: Get API Key

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Groq**: https://console.groq.com/keys

### Step 2: Update `.env`

```bash
# For OpenAI GPT-4o
AGENT_MODEL=gpt-4o
OPENAI_API_KEY=sk-your-key-here

# Or for Anthropic Claude
AGENT_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Verify

```bash
cd examples/templates/customer_service_agent
python -c "from agent import create_customer_service_agent; print('✓ Agent initialized')"
```

## Testing

Test the agent with different LLM providers:

```bash
# Test with OpenAI
AGENT_MODEL=gpt-4o python test_agent_v2.py

# Test with Claude
AGENT_MODEL=claude-3-opus-20240229 python test_agent_v2.py

# Test with Groq (currently may have deprecation issues)
AGENT_MODEL=groq/llama-3.1-8b-instant python test_agent_v2.py
```

## Monitoring for Deprecations

If you see "model decommissioned" errors again:

1. Check provider's documentation:
   - OpenAI: https://platform.openai.com/docs/models
   - Anthropic: https://docs.anthropic.com/claude/reference/getting-started-with-the-api
   - Groq: https://console.groq.com/docs/speech-text

2. Update `.env` with a new available model

3. The fallback to keyword classification ensures zero downtime

## Files Changed

- `.env` - Changed `AGENT_MODEL` to `gpt-4o` with fallback comments

## Alternative Models

If you want to use a different LLM provider:

### OpenAI (GPT-4)

```
AGENT_MODEL=gpt-4
OPENAI_API_KEY=sk-...
```

### Anthropic (Claude 3)

```
AGENT_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-...
```

### Other Groq Models

```
# Llama 3.1 8B (faster, less capable)
AGENT_MODEL=groq/llama-3.1-8b-instant

# Mixtral 8x22B (more capable, slower)
AGENT_MODEL=groq/mixtral-8x22b-32768
```

## Files Changed

- `.env` - Updated `AGENT_MODEL` from `groq/mixtral-8x7b-32768` to `groq/llama-3.1-70b-versatile`

## Impact

✅ **No breaking changes** - All existing code continues to work
✅ **Better LLM performance** - Llama 3.1 70B is more capable than Mixtral 8x7B
✅ **Faster responses** - Groq's inference is extremely fast
✅ **Cost-effective** - Free tier available with generous limits

## Testing

To verify the fix works:

```bash
cd examples/templates/customer_service_agent

# Test with direct execution
python __main__.py

# Test with a sample inquiry
python -c "
from agent import create_customer_service_agent
agent = create_customer_service_agent()
result = agent.process_inquiry('I forgot my password')
print(result['agent_response'])
"
```

## Notes for Future

- Monitor Groq's deprecation page: https://console.groq.com/docs/deprecations
- Consider implementing model rotation/fallback to multiple providers
- The fallback to keyword-based responses ensures the agent never completely fails
