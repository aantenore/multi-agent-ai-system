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
# Try to get default from env, otherwise fallback to Gemini Flash
CURRENT_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")
if Path(".env").exists():
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("LLM_MODEL="):
                CURRENT_MODEL = line.split("=", 1)[1].strip()
                break


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


def get_ollama_models():
    """Get list of available Ollama models."""
    try:
        # Run ollama list
        # output format is: NAME    ID    SIZE    MODIFIED
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")[1:]  # Skip header
        return [line.split()[0] for line in lines if line.strip()]
    except (FileNotFoundError, subprocess.SubprocessError):
        return []


def get_remote_models():
    """Get list of configured remote models."""
    models = []
    # Check for API keys in env
    env_content = ""
    if Path(".env").exists():
        try:
            env_content = Path(".env").read_text(encoding="utf-8")
        except Exception:
            pass

    has_google = "GOOGLE_API_KEY" in os.environ or "GOOGLE_API_KEY" in env_content
    has_openai = "OPENAI_API_KEY" in os.environ or "OPENAI_API_KEY" in env_content
    has_anthropic = (
        "ANTHROPIC_API_KEY" in os.environ or "ANTHROPIC_API_KEY" in env_content
    )

    if has_google:
        models.extend(
            [
                "gemini-3-flash-preview",
                "gemini-3-pro-preview",
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash",
                "gemini-1.5-pro",
            ]
        )

    if has_openai:
        models.extend(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"])
    if has_anthropic:
        models.extend(["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"])

    return models


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
    """Pull an Ollama model."""
    print(f"\n{BOLD}Pull Model:{RESET}")
    print(
        "Enter the model name to pull (e.g., 'mistral', 'llama3', 'lfm2.5-thinking:1.2b')"
    )
    model_name = input(f"{BOLD}Model Name > {RESET}").strip()

    if not model_name:
        print(f"{RED}No model name entered.{RESET}")
        input("Press Enter...")
        return

    print(f"\n{YELLOW}⬇️  Pulling model {model_name}...{RESET}\n")
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"\n{GREEN}✅ Model {model_name} pulled successfully!{RESET}")

        # Ask if user wants to switch to it
        switch = input(f"\nSwitch to {model_name}? (Y/n) > ").strip().lower()
        if switch != "n":
            global CURRENT_MODEL
            CURRENT_MODEL = model_name
            print(f"\n{CYAN}ℹ️  Switched to model: {CURRENT_MODEL}{RESET}")

    except FileNotFoundError:
        print(f"\n{RED}❌ Ollama not found. Is it installed and in your PATH?{RESET}")
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}")

    input(f"\n{GREEN}Press Enter to continue...{RESET}")


def select_model():
    """Select LLM Model."""
    global CURRENT_MODEL

    print(f"\n{BOLD}Fetching available models...{RESET}")
    ollama_models = get_ollama_models()
    remote_models = get_remote_models()

    all_models = sorted(list(set(ollama_models + remote_models)))

    if not all_models:
        print(
            f"{RED}No models found. Please pull a model with Ollama or configure API keys.{RESET}"
        )
        print(f"{YELLOW}(You can still enter a custom model name){RESET}")

    print(f"\n{BOLD}Available Models:{RESET}")
    for i, m in enumerate(all_models, 1):
        if m == CURRENT_MODEL:
            print(f"  {GREEN}[{i}]{RESET} {m} {CYAN}(Current){RESET}")
        else:
            print(f"  {GREEN}[{i}]{RESET} {m}")

    print(f"  {GREEN}[C]{RESET} Custom...")

    choice = input(f"\n{BOLD}Select > {RESET}").strip().lower()

    if choice == "c":
        custom = input("Enter model name: ").strip()
        if custom:
            CURRENT_MODEL = custom
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(all_models):
                CURRENT_MODEL = all_models[idx]
            else:
                print(f"{RED}Invalid selection.{RESET}")
                input("Press Enter...")
        except ValueError:
            print(f"{RED}Invalid input.{RESET}")
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
        print(f"  {BLUE}[M]{RESET} Pull New Model")
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
