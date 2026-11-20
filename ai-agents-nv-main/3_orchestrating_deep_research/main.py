"""A Company research agent built on `deepagents`.

A lead agent plans and delegates to subagents (competitor_discoverer_subagent, product_researcher_subagent, size_researcher_subagent)
that fan out over the web, then synthesizes a company brief.

Each run gets its own folder under `runs/<run_id>/` holding the agent's files
(plan.md, notes.md, findings/), so you can inspect exactly what happened.

Usage:
    python main.py "Research the company: Notion"
    python main.py "Research the company: Slack"
"""

import logging
import os
import sys
import uuid

from deepagents.backends import FilesystemBackend

from agents import build_agent

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

RUNS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")


def main():
    company = " ".join(sys.argv[1:]).strip()
    while not company:
        company = input("Which company should I research? ").strip()

    question = (
        f"Research the company: {company}. "
        "I am preparing for a job interview with them."
    )
    run_id = f"company-{uuid.uuid4().hex[:12]}"

    run_dir = os.path.join(RUNS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    # virtual_mode anchors every agent path under run_dir and blocks traversal.
    backend = FilesystemBackend(root_dir=run_dir, virtual_mode=True)
    agent = build_agent(backend)

    logger.info("Interview Company research: %s", question)
    logger.info("Run folder: %s", run_dir)

    agent_input = {
        "messages": [{"role": "user", "content": question}]
    }

    try:
        result = agent.invoke(agent_input)
        final = result["messages"][-1].content
        print(final if isinstance(final, str) else str(final))
    except Exception:
        logger.exception("Agent run failed")


if __name__ == "__main__":
    main()
