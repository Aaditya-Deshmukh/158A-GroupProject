import sys

from part1 import TYPE_A
from part3 import resolve


def main():
    if len(sys.argv) != 2:
        print("Usage: python resolve.py <domain>")
        return 1

    domain_name = sys.argv[1]
    address = resolve(domain_name, TYPE_A)

    print(address)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())