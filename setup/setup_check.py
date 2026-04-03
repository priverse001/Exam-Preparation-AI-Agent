#!/usr/bin/env python3
"""
IIT BHU AI Workshop - Setup Verification Script
Checks Docker, Git, .env, and container config files.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


class Colors:
    HEADER = "\033[95m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

    @staticmethod
    def disable() -> None:
        Colors.HEADER = ""
        Colors.OKCYAN = ""
        Colors.OKGREEN = ""
        Colors.FAIL = ""
        Colors.ENDC = ""
        Colors.BOLD = ""


if platform.system() == "Windows":
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        Colors.disable()


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    ok: bool
    details: str


def print_header(text: str) -> None:
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 72}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^72}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 72}{Colors.ENDC}\n")


def print_success(text: str) -> None:
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def run_command(cmd: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=20)
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except FileNotFoundError:
        return False, "Command not found"
    except Exception as exc:
        return False, str(exc)


def ensure_env_file(root: Path) -> None:
    env_file = root / ".env"
    template_file = root / ".env.template"
    if env_file.exists():
        return

    if template_file.exists():
        env_file.write_text(template_file.read_text(encoding="utf-8"), encoding="utf-8")
        print_info("Created `.env` from `.env.template`.")
    else:
        env_file.write_text("OPENAI_API_KEY=\n", encoding="utf-8")
        print_info("Created minimal `.env` file.")


def check_env(root: Path) -> CheckResult:
    env_file = root / ".env"
    if not env_file.exists():
        return CheckResult(".env", False, "Missing `.env` file")

    values: dict[str, str] = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")

    key = values.get("OPENAI_API_KEY", "")
    if key and key != "sk-proj-your-openai-api-key-here":
        return CheckResult(".env", True, "OPENAI_API_KEY is configured")
    return CheckResult(".env", False, "Set OPENAI_API_KEY in `.env`")


def check_docker() -> CheckResult:
    path = shutil.which("docker")
    if not path:
        return CheckResult("Docker CLI", False, "Install Docker Desktop or another Docker runtime")

    ok, output = run_command(["docker", "--version"])
    if not ok:
        return CheckResult("Docker CLI", False, output or "Docker is installed but not responding")
    return CheckResult("Docker CLI", True, output.split(",")[0] if output else "docker found")


def check_docker_compose() -> CheckResult:
    ok, output = run_command(["docker", "compose", "version"])
    if not ok:
        return CheckResult("Docker Compose", False, "Docker Compose is not available")
    return CheckResult("Docker Compose", True, output.splitlines()[0])


def check_git() -> CheckResult:
    ok, output = run_command(["git", "--version"])
    if not ok:
        return CheckResult("Git", False, "Install Git")
    return CheckResult("Git", True, output)


def check_devcontainer_files(root: Path) -> CheckResult:
    needed = [
        root / "docker-compose.yml",
        root / "Dockerfile",
        root / ".devcontainer" / "devcontainer.json",
    ]
    missing = [str(path.relative_to(root)) for path in needed if not path.exists()]
    if missing:
        return CheckResult("Container config", False, f"Missing: {', '.join(missing)}")
    return CheckResult("Container config", True, "Docker/devcontainer files found")


def check_optional_local_tooling() -> list[CheckResult]:
    results: list[CheckResult] = []
    for label, command in [
        ("Python", ["python3", "--version"] if platform.system() != "Windows" else ["python", "--version"]),
        ("Node", ["node", "--version"]),
        ("uv", ["uv", "--version"]),
    ]:
        ok, output = run_command(command)
        results.append(CheckResult(label, ok, output or "Not installed"))
    return results


def print_results(title: str, results: list[CheckResult]) -> None:
    print(f"{Colors.BOLD}{title}{Colors.ENDC}")
    for result in results:
        line = f"{result.name}: {result.details}"
        if result.ok:
            print_success(line)
        else:
            print_error(line)
    print()


def main() -> int:
    root = project_root()
    ensure_env_file(root)

    print_header("IIT BHU AI Workshop Setup Check")
    print_info(f"Project root: {root}")
    print_info("Recommended workflow: open the repo in the devcontainer and run `npm run start` inside it.\n")

    required_results = [
        check_git(),
        check_docker(),
        check_docker_compose(),
        check_devcontainer_files(root),
        check_env(root),
    ]
    optional_results = check_optional_local_tooling()

    print_results("Required for workshop path", required_results)
    print_results("Optional local tooling (only needed outside containers)", optional_results)

    failures = [result for result in required_results if not result.ok]
    if failures:
        print_error("Setup is not ready for the recommended container-based workflow.")
        print_info("Fix the failed checks above, then rerun this script.")
        return 1

    print_success("Container-based workshop setup looks good.")
    print_info("Next steps:")
    print("  1. Open the repo in the devcontainer, or run `docker compose up -d`.")
    print("  2. Start a shell in the container.")
    print("  3. Run `npm run start`.")
    print("  4. Open http://localhost:5173 in your browser.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
