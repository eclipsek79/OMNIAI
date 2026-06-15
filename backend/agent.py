import openai
from config import OPENAI_API_KEY, MODEL
from tools import calculator, write_file, build_app
from toolschema import TOOLS

client = openai.OpenAI(api_key=OPENAI_API_KEY)


def run_agent(goal: str):
    messages = [
        {"role": "system", "content": "You are an autonomous AI agent. Use tools when needed."},
        {"role": "user", "content": goal}
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        # If model gives final answer
        if not msg.tool_calls:
            return {"final": msg.content}

        # Execute tools
        messages.append(msg)

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = eval(tool_call.function.arguments)

            if name == "calculator":
                result = calculator(**args)

            elif name == "write_file":
                result = write_file(**args)

            elif name == "build_app":
                result = build_app(**args)

            else:
                result = {"error": "unknown tool"}

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })