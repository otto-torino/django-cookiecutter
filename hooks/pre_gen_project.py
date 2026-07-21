#!/usr/bin/env python3

import re
import socket
import sys
from collections import OrderedDict  # noqa: F401 - used by rendered context repr


context = {{cookiecutter}}

LANGUAGE_CODE_PATTERN = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]+)*$")


LOCAL_PORTS = {
    1025: "MailHog SMTP",
    5434: "PostgreSQL",
    5678: "debugpy",
    8000: "Django",
    8001: "Django with pdb",
    8025: "MailHog web UI",
}


def validate_languages():
    """Validate the comma-separated language codes used by Django."""
    if context["use_translations"] != "y":
        return

    languages = [
        language.strip() for language in context["languages"].split(",")
        if language.strip()
    ]
    default_language = context["default_language"].strip()
    errors = []

    if len(languages) < 2:
        errors.append("choose at least two comma-separated language codes")
    if len(languages) != len(set(languages)):
        errors.append("language codes must not be repeated")

    invalid_languages = [
        language for language in languages
        if not LANGUAGE_CODE_PATTERN.fullmatch(language)
    ]
    if invalid_languages:
        errors.append(
            "invalid language code(s): " + ", ".join(invalid_languages)
        )
    if default_language not in languages:
        errors.append(
            f"default_language '{default_language}' must be included in languages"
        )

    if not errors:
        return

    print("\nInvalid multilingual configuration:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    print(
        "\nUse lowercase Django language codes, for example: it,en or "
        "it,en,fr.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def unavailable_ports():
    """Return local TCP ports that cannot be bound on the loopback address."""
    unavailable = []
    for port, service in LOCAL_PORTS.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind(("127.0.0.1", port))
            except OSError as error:
                unavailable.append((port, service, error))
    return unavailable


def main():
    validate_languages()
    unavailable = unavailable_ports()
    if not unavailable:
        return

    print(
        "\nCannot create the project because these local ports are unavailable:",
        file=sys.stderr,
    )
    for port, service, error in unavailable:
        print(f"  - {port}: {service} ({error.strerror})", file=sys.stderr)
    print(
        "\nStop the processes or containers using these ports, then run "
        "Cookiecutter again.",
        file=sys.stderr,
    )
    raise SystemExit(1)


if __name__ == "__main__":
    main()
