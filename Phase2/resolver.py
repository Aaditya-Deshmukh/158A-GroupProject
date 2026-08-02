import sys

from dns_resolver import TYPE_A, resolve


def main():
    if len(sys.argv) < 2:
        print("Usage: python resolver.py <domain> [domain ...]")
        return 1

    exit_code = 0

    # PHASE 2 MODIFICATION:
    # Resolve every domain provided on the command line while sharing
    # the same DNS cache.
    for domain_name in sys.argv[1:]:
        print(f"\nResolving {domain_name}")

        try:
            address = resolve(domain_name, TYPE_A)
        except (OSError, RuntimeError, ValueError) as error:
            print(f"DNS lookup failed: {error}", file=sys.stderr)
            exit_code = 1
            continue

        print(address)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())