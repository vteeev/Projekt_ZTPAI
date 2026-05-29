#!/usr/bin/env python
"""Narzedzie wiersza polecen Django."""
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Nie mozna zaimportowac Django. Czy jest zainstalowane i czy "
            "srodowisko wirtualne jest aktywne?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
