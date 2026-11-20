"""Subagent definitions and the lead-agent builder.

Orchestrator-worker pattern (Anthropic's multi-agent research system):
  - lead agent           -> plans, delegates, synthesizes the report.
  - competitor_discoverer_subagent      -> discovers company's top 3 competitors.
  - product_researcher_subagent -> discovers the released products of the company.
  - size_researcher_subagent -> deep-dives into the size of the company in parallel.
  - fact-checker          -> audits every sourced claim before it ships.
"""

from deepagents import create_deep_agent

from models import LEAD_MODEL, WORKER_MODEL
from prompts import (
    COMPETITOR_DISCOVERER_SUBAGENT,
    PRODUCT_RESEARCHER_SUBAGENT,
    SIZE_RESEARCHER_SUBAGENT,
    FACT_CHECKER_PROMPT,
    LEAD_AGENT_PROMPT,
)
from tools import internet_search, log_tool_calls

competitor_discoverer_subagent = {
    "name": "competitor-discoverer",
    "description": (
        "Use in the DELEGATE step, to identify WHO are the top competitors are for input company/"
        "product in a market. It returns a list of top 3competitors with homepage URLs and one-line reasons for why they are the top competitors."
    ),
    "system_prompt": COMPETITOR_DISCOVERER_SUBAGENT,
    "tools": [internet_search],
    "model": WORKER_MODEL,
}

product_researcher_subagent = {
    "name": "product-researcher",
    "description": (
        "Use in the DELEGATE step, in parallel with size-researcher and "
        "competitor-discoverer. Researches the business overview (what "
        "the company does, the problem it solves, its customers), its "
        "product portfolio, launches in the last 12 months, which "
        "products drive revenue/growth, and its AI features and plans "
        "for the future."
    ),
    "system_prompt": PRODUCT_RESEARCHER_SUBAGENT,
    "tools": [internet_search],
    "model": WORKER_MODEL,
}
size_researcher_subagent = {
    "name": "size-researcher",
    "description": (
        "Use in the DELEGATE step, in parallel with product-researcher and "
        "competitor-discoverer. Researches the size of the company in terms of "
        "revenue, employees, and office locations."
    ),
    "system_prompt": SIZE_RESEARCHER_SUBAGENT,
    "tools": [internet_search],
    "model": WORKER_MODEL,
    "max_steps": 3,
}

# No tools key: audits only what was already gathered into findings/.
fact_checker_subagent = {
    "name": "fact-checker",
    "description": (
        "Use this AFTER drafting the final analysis and BEFORE returning it. "
        "Give it the `notes.md` draft plus a pointer to the `findings/` "
        "directory. It verifies every claim by checking the sources and the dates."
    ),
    "system_prompt": FACT_CHECKER_PROMPT,
    "model": WORKER_MODEL,
}


def build_agent(backend):
    """Wire the lead agent to its subagents and backend."""
    return create_deep_agent(
        model=LEAD_MODEL,
        tools=[internet_search],
        system_prompt=LEAD_AGENT_PROMPT,
        subagents=[
            competitor_discoverer_subagent,
            product_researcher_subagent,
            size_researcher_subagent,
            fact_checker_subagent,
        ],
        middleware=[log_tool_calls],
        backend=backend,
    )
