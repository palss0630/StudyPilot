"""
StudyPilot CLI - Run the agent from the terminal.

Usage:
    python cli.py "your study goal here"
    python cli.py --demo "teach me about black holes"

Prints the agent trace (plan, tool calls, reflection, final answer) to stdout.
"""

import argparse
import json
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.studypilot.config import logger, GROQ_API_KEY, LLM_MODEL, LLM_PROVIDER
from src.studypilot.memory.store import MemoryStore
from src.studypilot.agent.orchestrator import Orchestrator


def print_separator() -> None:
    """Print a visual separator line."""
    print("─" * 60)


def format_tool_result(result: str, max_len: int = 200) -> str:
    """Truncate a tool result for display."""
    if len(result) > max_len:
        return result[:max_len] + "..."
    return result


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="StudyPilot - AI Study & Research Agent (CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py "Teach me about black holes"
  python cli.py "Compare solar vs wind energy"
  python cli.py "What is the weather in London?"
        """,
    )
    parser.add_argument("goal", help="Your study goal or research question")
    args = parser.parse_args()

    if not GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY is missing. Please set it in your .env file.")
        sys.exit(1)

    print(f"🚀 Using LLM Provider: {LLM_PROVIDER.upper()} ({LLM_MODEL})")
    print_separator()
    print(f"🎯 Goal: {args.goal}")
    print_separator()

    # Create orchestrator and run
    memory = MemoryStore()
    orchestrator = Orchestrator(memory_store=memory)

    try:
        for event in orchestrator.run(args.goal):
            event_type = event.get("type", "")

            if event_type == "guardrail_blocked":
                print(f"\n🛡️  {event.get('message', 'Blocked by guardrails.')}")
                return

            elif event_type == "plan_created":
                plan = event.get("plan", {})
                steps = plan.get("steps", []) if isinstance(plan, dict) else []
                print("\n📋 PLAN:")
                for step in steps:
                    if isinstance(step, dict):
                        num = step.get("step", "?")
                        desc = step.get("description", "")
                        tools = step.get("tools_needed", [])
                        tool_str = f" [{', '.join(tools)}]" if tools else ""
                        print(f"   {num}. {desc}{tool_str}")
                print_separator()

            elif event_type == "step_start":
                step = event.get("step", {})
                if isinstance(step, dict):
                    print(f"\n▶️  Step {step.get('step', '?')}: {step.get('description', '')}")

            elif event_type == "tool_called":
                name = event.get("name", "?")
                args_str = json.dumps(event.get("args", {}), indent=None)
                if len(args_str) > 100:
                    args_str = args_str[:100] + "..."
                print(f"   🔧 {name}({args_str})")

            elif event_type == "tool_result":
                result = event.get("result", "")
                print(f"   📎 {format_tool_result(result)}")

            elif event_type == "step_complete":
                content = event.get("content", "")
                if content:
                    preview = content[:300] + "..." if len(content) > 300 else content
                    print(f"   ✅ {preview}")

            elif event_type == "reflection":
                result = event.get("result", {})
                if isinstance(result, dict):
                    ok = result.get("ok", True)
                    issues = result.get("issues", [])
                    status = "✅ Passed" if ok else "🔄 Revision needed"
                    print(f"\n🤔 REFLECTION: {status}")
                    if issues:
                        for issue in issues:
                            print(f"   ⚠️  {issue}")

            elif event_type == "final_answer":
                answer = event.get("answer", "")
                sources = event.get("sources", [])
                print_separator()
                print("\n📝 FINAL ANSWER:\n")
                print(answer)
                if sources:
                    print("\n📚 Sources:")
                    for src in sources:
                        print(f"   • {src}")
                print_separator()

            elif event_type == "error":
                print(f"\n❌ ERROR: {event.get('message', 'Unknown error')}")

    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception("CLI error")
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    print("\n✨ Done! Run `npm run dev` in frontend/ for the full React UI experience.")

if __name__ == "__main__":
    main()
