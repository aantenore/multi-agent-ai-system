import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from multi_agent.shared.llm_factory import create_llm
from langchain_core.messages import HumanMessage


def test_ollama():
    print("Testing Ollama connection...")
    try:
        llm = create_llm()
        print(f"LLM created: {llm}")

        # Simple invocation
        messages = [HumanMessage(content="Hello, are you working?")]
        print("Invoking LLM...")
        response = llm.invoke(messages)
        print(f"Response: {response.content}")

    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    test_ollama()
