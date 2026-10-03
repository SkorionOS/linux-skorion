#!/usr/bin/env python3
"""Fail when Kconfig normalization drops a requested Skorion setting."""

import argparse
from pathlib import Path
import re
import sys


ASSIGNMENT = re.compile(r"^(CONFIG_[A-Za-z0-9_]+)=(.*)$")
DISABLED = re.compile(r"^# (CONFIG_[A-Za-z0-9_]+) is not set$")


def read_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        line = line.strip()
        match = ASSIGNMENT.fullmatch(line)
        disabled = DISABLED.fullmatch(line)
        if match:
            symbol, value = match.groups()
        elif disabled:
            symbol, value = disabled.group(1), "n"
        else:
            if line and not line.startswith("#"):
                raise ValueError(f"{path}:{number}: invalid config line: {line}")
            continue
        if symbol in values:
            raise ValueError(f"{path}:{number}: duplicate setting: {symbol}")
        values[symbol] = value
    return values


def compare_config(actual: dict[str, str], requested: dict[str, str]) -> list[str]:
    return [
        f"{symbol}: expected {value}, got {actual.get(symbol, '<missing>')}"
        for symbol, value in requested.items()
        if actual.get(symbol) != value
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("fragment", type=Path)
    args = parser.parse_args()
    try:
        actual = read_config(args.config)
        requested = read_config(args.fragment)
        if not requested:
            raise ValueError(f"{args.fragment}: no requested config settings")
        errors = compare_config(actual, requested)
    except (OSError, ValueError) as error:
        print(f"Config check failed: {error}", file=sys.stderr)
        return 1
    if errors:
        print("Skorion config settings did not survive Kconfig normalization:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(f"Verified {len(requested)} Skorion config settings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
