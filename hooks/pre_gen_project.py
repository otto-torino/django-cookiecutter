#!/usr/bin/env python3

import socket
import sys


LOCAL_PORTS = {
    1025: "MailHog SMTP",
    5434: "PostgreSQL",
    5678: "debugpy",
    8000: "Django",
    8001: "Django with pdb",
    8025: "MailHog web UI",
}


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
