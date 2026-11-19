cat > Project_2/README.md <<'EOF'
# PersonaForge — CS676 Project 2

**Course:** CS676 Algorithms for Data Science  
**University:** Pace University

## Project Overview

PersonaForge is a Python application that uses large language models to create fictional personas and simulate conversations between them.

This project focused on improving the application's ability to understand natural-language requests and coordinate actions through tool calling.

## My Contributions

The main improvements include:

- Implementing Claude tool calling for natural-language requests.
- Improving the orchestration of persona creation and conversations.
- Updating the application's language model integration.
- Improving conversation handling and persona management.
- Adding automated tests to evaluate the updated functionality.
- Documenting the implementation and testing process.

## Technical Implementation

The application uses Python and the Anthropic Claude API.

The updated orchestrator allows the language model to select appropriate tools based on user requests rather than relying exclusively on predefined text patterns.

Key implementation files include:

- `src/personaforge/orchestrator.py` — Tool definitions and orchestration logic.
- `src/personaforge/llm.py` — Language model integration.
- `src/personaforge/conversation.py` — Conversation functionality.
- `src/personaforge/persona.py` — Persona management.
- `tests/test_orchestrator.py` — Tests for orchestration and tool calling.

## Installation

Install `uv` and configure an Anthropic API key.

Create a `.env` file using `.env.example` as a reference.

Install dependencies:

```bash
uv sync