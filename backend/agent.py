"""
Agent loop: receives a goal and a list of planned steps, executes them via tools,
persists each step/result in memory, and returns aggregated results.
"""
from __future__ import annotations
from typing import List, Dict, Any

from . import memory, tools, utils

logger = utils.logger

def execute(goal: str, steps: List[str]) -> Dict[str, Any]:
    results: List[str] = []
    details: List[Dict[str, str]] = []
    for i, step in enumerate(steps, start=1):
        logger.info("Executing step %d/%d: %s", i, len(steps), step)
        tool_name, result = tools.route_tool(step)
        # Save to memory
        memory.save_entry(goal=goal, step=step, result=result)
        results.append(result)
        details.append({"step": step, "tool": tool_name, "result": result})
    # Optionally return last memory rows for context
    recent = memory.load_last(20)
    return {"results": results, "details": details, "recent_memory": recent}
