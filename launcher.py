#!/usr/bin/env python3
"""
Launcher script for Multi-Agent System Examples.
"""
import os
import sys
import subprocess
import glob
from pathlib import Path

# ANSI colors
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header():
    print(f"\n{BLUE}{BOLD}" + "=" * 60)
    print("   🤖 Multi-Agent System - Example Launcher")
    print("=" * 60 + f"{RESET}\n")


def get_examples():
    """Get list of example scripts."""
    examples_dir = Path("examples")
    files = sorted(examples_dir.glob("[0-9]*.py"))
    return [f for f in files]


def run_script(script_path):
    """Run a python script."""
    print(f"\n{YELLOW}▶ Running {script_path}...{RESET}\n")
    try:
        subprocess.run([sys.executable, str(script_path)], check=False)
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

        print(f"\n{YELLOW}ℹ️  To use this model, set it in your .env file:{RESET}")
        print(f"{BLUE}LLM_MODEL={model}{RESET}")

    except FileNotFoundError:
        print(f"\n{RED}❌ Ollama not found. Is it installed and in your PATH?{RESET}")
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}")

    input(f"\n{GREEN}Press Enter to continue...{RESET}")


def main():
    while True:
        # Clear screen (windows/linux)
        os.system("cls" if os.name == "nt" else "clear")

        print_header()

        examples = get_examples()

        print(f"{BOLD}Available Examples:{RESET}")
        for i, ex in enumerate(examples, 1):
            print(f"  {GREEN}[{i}]{RESET} {ex.name}")

        print(f"\n{BOLD}Tools:{RESET}")
        print(f"  {BLUE}[M]{RESET} Pull Model (lfm2.5-thinking:1.2b)")
        print(f"  {RED}[Q]{RESET} Quit")

        choice = input(f"\n{BOLD}Select an option > {RESET}").strip().lower()

        if choice == "q":
            print("Goodbye! 👋")
            break
        elif choice == "m":
            pull_model()
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
