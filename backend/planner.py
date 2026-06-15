"""
Planner module: turns a goal into step-by-step plan.

If OPENAI_API_KEY is set, uses OpenAI chat completions API to generate steps.
Otherwise falls back to a simple heuristic splitter.
"""
from __future__ import annotations
from typing import List
import requests
import re

from . import config, utils

logger = utils.logger

def _parse_steps_from_text(text: str) -> List[str]:
    # Try split by numbered list or newlines
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # remove leading "1." or "- " etc
        line = re.sub(r'^[\-\*\d\.\)\s]+', '', line)
        lines.append(line)
    if not lines:
        # fallback split by sentences
        lines = [s.strip() for s in re.split(r'[.?!]\s+', text) if s.strip()]
    return lines

def plan(goal: str, max_steps: int = 8) -> List[str]:
    """
    Produce step-by-step plan for a goal.
    Uses OpenAI if configured; otherwise uses simple heuristics.
    """
    logger.info("Planning for goal: %s", goal)
    if config.OPENAI_API_KEY:
        try:
            payload = {
                "model": config.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful planner that breaks user goals into a concise sequence of actionable steps."},
                    {"role": "user", "content": f"Break the following goal into {max_steps} clear sequential steps. Keep each step short (1-2 lines). Goal: {goal}"}
                ],
                "temperature": 0.2,
                "max_tokens": 600
            }
            headers = {
                "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            resp = requests.post(config.OPENAI_API_URL, json=payload, headers=headers, timeout=config.HTTP_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            # expected structure: choices[0].message.content
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                raise ValueError("No content from OpenAI planner")
            steps = _parse_steps_from_text(content)
            if steps:
                logger.debug("Planner (OpenAI) returned %d steps", len(steps))
                return steps[:max_steps]
        except Exception as exc:
            logger.warning("OpenAI planner failed, falling back to local planner: %s", exc)

    # Local heuristic fallback
    # naive strategy: split by clauses, create 3-6 steps
    parts = [p.strip() for p in re.split(r'[.;]\s*', goal) if p.strip()]
    steps: List[str] = []
    if len(parts) == 1:
        # Break goal into generic phases
        steps = [
            f"Clarify goal and expected outcome for: {goal}",
            "Research requirements and gather necessary assets",
            "Design simple implementation plan",
            "Implement core functionality",
            "Test and iterate",
            "Save and deliver results"
        ]
    else:
        steps = [f"Work on: {p}" for p in parts]
    return steps[:max_steps]
