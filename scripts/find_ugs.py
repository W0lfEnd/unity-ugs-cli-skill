#!/usr/bin/env python3
"""Resolve a UGS CLI executable without persisting machine-specific paths."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


PATH_CANDIDATES = (
    "ugs",
    "ugs.exe",
    "ugs-cli",
    "ugs-cli.exe",
    "ugs-windows-x64",
    "ugs-windows-x64.exe",
    "ugs-linux-x64",
    "ugs-linux-arm64",
    "ugs-macos-x64",
    "ugs-macos-arm64",
)


def resolve_file(path: Path) -> str:
    resolved = path.resolve()
    if os.name != "nt" and not os.access(resolved, os.X_OK):
        raise PermissionError(
            f"UGS CLI exists but is not executable: {resolved}. "
            f"Run chmod +x {resolved} and try again."
        )
    return str(resolved)


def resolve_candidate(value: str) -> str | None:
    expanded = Path(value).expanduser()
    if expanded.is_file():
        return resolve_file(expanded)
    located = shutil.which(value)
    return str(Path(located).resolve()) if located else None


def resolve_ugs(explicit: str | None) -> tuple[str, str]:
    if explicit:
        resolved = resolve_candidate(explicit)
        if resolved:
            return resolved, "--cli"
        raise FileNotFoundError(f"UGS CLI not found from --cli value: {explicit}")

    env_value = os.environ.get("UGS_CLI_EXECUTABLE")
    if env_value:
        resolved = resolve_candidate(env_value)
        if resolved:
            return resolved, "UGS_CLI_EXECUTABLE"
        raise FileNotFoundError(
            "UGS_CLI_EXECUTABLE is set, but does not resolve to an executable file"
        )

    for candidate in PATH_CANDIDATES:
        resolved = shutil.which(candidate)
        if resolved:
            return str(Path(resolved).resolve()), "PATH"

    raise FileNotFoundError(
        "UGS CLI was not found. Supply --cli, set UGS_CLI_EXECUTABLE for this "
        "session, or add the executable to PATH."
    )


def verify_version(executable: str) -> str:
    result = subprocess.run(
        [executable, "--version"],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(
            f"UGS CLI version check failed with exit code {result.returncode}: {detail}"
        )
    return result.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve the UGS CLI from an explicit value, a session override, or PATH."
    )
    parser.add_argument(
        "--cli",
        help="Executable path or command name supplied for the current invocation.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run the resolved executable with --version.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit path, discovery source, and optional version as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        executable, source = resolve_ugs(args.cli)
        version = verify_version(executable) if args.verify else None
    except (FileNotFoundError, PermissionError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        payload = {"path": executable, "source": source}
        if version is not None:
            payload["version"] = version
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(executable)
        if version is not None:
            print(version, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
