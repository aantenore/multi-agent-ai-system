#!/usr/bin/env python3
"""
Launcher script for Multi-Agent System Examples.
"""
import os
import sys
import subprocess
from pathlib import Path

# ANSI colors
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"

# Global state
CURRENT_MODEL = os.getenv("LLM_MODEL", "mistral")


def print_header():
    print(f"\n{BLUE}{BOLD}" + "=" * 60)
    print("   🤖 Multi-Agent System - Example Launcher")
    print("=" * 60 + f"{RESET}")
    print(f"   Current Model: {CYAN}{CURRENT_MODEL}{RESET}")
    print(f"{BLUE}" + "=" * 60 + f"{RESET}\n")


def get_examples():
    """Get list of example scripts."""
    examples_dir = Path("examples")
    files = sorted(examples_dir.glob("[0-9]*.py"))
    return [f for f in files]


def run_script(script_path):
    """Run a python script."""
    print(f"\n{YELLOW}▶ Running {script_path} with model {CURRENT_MODEL}...{RESET}\n")

    # Inject current model into environment
    env = os.environ.copy()
    env["LLM_MODEL"] = CURRENT_MODEL

    try:
        subprocess.run([sys.executable, str(script_path)], env=env, check=False)
    except KeyboardInterrupt:
        print(f"\n{RED}❌ Execution interrupted.{RESET}")
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}")

    input(f"\n{GREEN}Press Enter to continue...{RESET}")


def pull_model():
    """Pull the Ollama model."""
    model = "lfm2.5-thinking:1.2b"
    print(f"\n{YELLOW}⬇️  Pulling model {model}...{RESET}\n")
    try:
        subprocess.run(["ollama", "pull", model], check=True)
        print(f"\n{GREEN}✅ Model pulled successfully!{RESET}")

        # Auto-switch to this model
        global CURRENT_MODEL
        CURRENT_MODEL = model
        print(f"\n{CYAN}ℹ️  Switched to model: {CURRENT_MODEL}{RESET}")

    except FileNotFoundError:
        print(f"\n{RED}❌ Ollama not found. Is it installed and in your PATH?{RESET}")
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}")

    input(f"\n{GREEN}Press Enter to continue...{RESET}")


def select_model():
    """Select LLM Model."""
    global CURRENT_MODEL
    print(f"\n{BOLD}Select Model:{RESET}")
    print(f"  {GREEN}[1]{RESET} mistral (Default)")
    print(f"  {GREEN}[2]{RESET} lfm2.5-thinking:1.2b (Reasoning)")
    print(f"  {GREEN}[3]{RESET} gpt-4o-mini (OpenAI)")
    print(f"  {GREEN}[4]{RESET} Custom...")

    choice = input(f"\n{BOLD}Select > {RESET}").strip()

    if choice == "1":
        CURRENT_MODEL = "mistral"
    elif choice == "2":
        CURRENT_MODEL = "lfm2.5-thinking:1.2b"
    elif choice == "3":
        CURRENT_MODEL = "gpt-4o-mini"
    elif choice == "4":
        custom = input("Enter model name: ").strip()
        if custom:
            CURRENT_MODEL = custom
    else:
        print(f"{RED}Invalid selection.{RESET}")
        input("Press Enter...")


def main():
    while True:
        # Clear screen (windows/linux)
        os.system("cls" if os.name == "nt" else "clear")

        print_header()

        examples = get_examples()

        print(f"{BOLD}Examples:{RESET}")
        for i, ex in enumerate(examples, 1):
            print(f"  {GREEN}[{i}]{RESET} {ex.name}")

        print(f"\n{BOLD}Tools:{RESET}")
        print(f"  {BLUE}[S]{RESET} Select/Change Model")
        print(f"  {BLUE}[M]{RESET} Pull Model (lfm2.5-thinking:1.2b)")
        print(f"  {RED}[Q]{RESET} Quit")

        choice = input(f"\n{BOLD}Select an option > {RESET}").strip().lower()

        if choice == "q":
            print("Goodbye! 👋")
            break
        elif choice == "m":
            pull_model()
            continue
        elif choice == "s":
            select_model()
            continue

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                run_script(examples[idx])
            else:
                print(f"{RED}Invalid selection.{RESET}")
                input("Press Enter...")
        except ValueError:
            print(f"{RED}Invalid input.{RESET}")
            input("Press Enter...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
