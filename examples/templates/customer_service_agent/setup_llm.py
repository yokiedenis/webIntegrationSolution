#!/usr/bin/env python3
"""
Quick setup script to add API key for customer service agent.
Run this to configure your LLM provider credentials.
"""

import sys
from pathlib import Path


def main():
    print("\n" + "=" * 70)
    print("  Customer Service Agent - LLM Configuration")
    print("=" * 70 + "\n")

    print("Choose your LLM provider:\n")
    print("  1) Groq (recommended - free tier, fast)")
    print("  2) OpenAI (GPT-4, requires paid account)")
    print("  3) Anthropic Claude (requires paid account)")
    print("  4) View available models\n")

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        setup_groq()
    elif choice == "2":
        setup_openai()
    elif choice == "3":
        setup_anthropic()
    elif choice == "4":
        show_models()
    else:
        print("Invalid choice")
        sys.exit(1)


def setup_groq():
    """Set up Groq API key"""
    print("\n" + "-" * 70)
    print("Groq Setup")
    print("-" * 70 + "\n")
    print("1. Visit: https://console.groq.com/keys")
    print("2. Create a new API key (free)")
    print("3. Copy the key below\n")

    api_key = input("Paste your Groq API key: ").strip()
    if not api_key:
        print("Cancelled")
        return

    update_env("GROQ_API_KEY", api_key)
    update_env("AGENT_MODEL", "groq/gemma-7b-it")
    print("\n✓ Groq API key configured!")
    print("  Model: Gemma 7B (lightweight, stable)")


def setup_openai():
    """Set up OpenAI API key"""
    print("\n" + "-" * 70)
    print("OpenAI Setup")
    print("-" * 70 + "\n")
    print("1. Visit: https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Copy the key below\n")

    api_key = input("Paste your OpenAI API key: ").strip()
    if not api_key:
        print("Cancelled")
        return

    update_env("OPENAI_API_KEY", api_key)
    update_env("AGENT_MODEL", "gpt-4o-mini")
    print("\n✓ OpenAI API key configured!")
    print("  Model: GPT-4o Mini (fast and capable)")


def setup_anthropic():
    """Set up Anthropic API key"""
    print("\n" + "-" * 70)
    print("Anthropic Claude Setup")
    print("-" * 70 + "\n")
    print("1. Visit: https://console.anthropic.com/settings/keys")
    print("2. Create a new API key")
    print("3. Copy the key below\n")

    api_key = input("Paste your Anthropic API key: ").strip()
    if not api_key:
        print("Cancelled")
        return

    update_env("ANTHROPIC_API_KEY", api_key)
    update_env("AGENT_MODEL", "claude-3-5-sonnet-20241022")
    print("\n✓ Anthropic API key configured!")
    print("  Model: Claude 3.5 Sonnet (most capable)")


def show_models():
    """Show available models"""
    print("\nAvailable Models by Provider:\n")
    print(
        "Groq (Free tier - Check https://console.groq.com/docs/speech-text for current models):"
    )
    print("  - groq/gemma-7b-it (recommended - stable)")
    print("  - groq/mixtral-8x7b-32768 (may be deprecated)")
    print("  - groq/llama-3.1-70b-versatile (may be deprecated)\n")

    print("OpenAI (Paid):")
    print("  - gpt-4o (most capable)")
    print("  - gpt-4o-mini (fast, affordable)")
    print("  - gpt-4-turbo\n")

    print("Anthropic (Paid):")
    print("  - claude-3-5-sonnet-20241022 (most capable)")
    print("  - claude-3-5-haiku-20241022 (fast)\n")


def update_env(key, value):
    """Update .env file"""
    env_path = Path(__file__).parent / ".env"

    lines = []
    found = False

    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()

    # Update or add the key
    updated_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            updated_lines.append(f"{key}={value}\n")
            found = True
        else:
            updated_lines.append(line)

    if not found:
        # Add new key
        if updated_lines and not updated_lines[-1].endswith("\n"):
            updated_lines.append("\n")
        updated_lines.append(f"{key}={value}\n")

    # Write back
    with open(env_path, "w") as f:
        f.writelines(updated_lines)

    print(f"✓ Updated {env_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled")
        sys.exit(1)
