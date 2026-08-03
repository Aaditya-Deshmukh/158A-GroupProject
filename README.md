# CS 158A DNS Resolver Project

## Group Information

**Group Number:** [ADD GROUP NUMBER]

**Group Members:**
- [MEMBER NAME]
- [MEMBER NAME]

## Project Overview

This project implements a DNS resolver in three phases:

- **Phase 1:** Build a baseline iterative DNS resolver.
- **Phase 2:** Add a TTL-based DNS cache.
- **Phase 3:** Add CNAME resolution, DNS error handling, and transaction ID validation.

The resolver is written in Python 3 and performs DNS lookups without using `getaddrinfo`, `dnspython`, or the operating system resolver.

## Repository Structure

```text
158A-GroupProject/
├── Phase1/
│   ├── part1.py
│   ├── part2.py
│   ├── part3.py
│   ├── resolver.py
│   └── README.md
├── Phase2/
│   ├── dns_resolver.py
│   ├── resolver.py
│   ├── test_ttl.py
│   ├── README.md
│   └── screenshots
├── Phase3/
│   ├── dns_resolver.py
│   ├── resolver.py
│   ├── test_phase3.py
│   ├── README.md
│   └── screenshots
└── README.md
```

## Requirements

- Python 3
- Internet access
- No external Python packages are required

## How to Run

Clone the repository:

```bash
git clone https://github.com/Aaditya-Deshmukh/158A-GroupProject.git
cd 158A-GroupProject
```

Each phase is run from its own folder.

---

## Phase 1

### Overview

Phase 1 implements the baseline iterative DNS resolver by following the structure from *Implement DNS in a Weekend*.

The resolver:

- Builds DNS query packets.
- Encodes domain names.
- Sends UDP DNS requests.
- Parses DNS headers, questions, and resource records.
- Handles DNS name compression.
- Starts at a root server.
- Follows referrals to TLD and authoritative name servers.
- Returns an IPv4 address from an A record.

### How to Run

```bash
cd Phase1
python resolver.py example.com
```

Example:

```text
Querying 198.41.0.4 for example.com
Querying 192.41.162.30 for example.com
Querying 108.162.192.162 for example.com
104.20.23.154
```

The exact IP address may differ because some domains return multiple valid A records.

### Test Cases

#### Test Case 1 - Different Domains

Commands:

```bash
python resolver.py example.com
python resolver.py python.org
```

Results:

- `example.com` resolved successfully.
- `python.org` resolved successfully.
- Results were compared with `nslookup`.

#### Test Case 2 - Domain With Multiple A Records

Command:

```bash
python resolver.py google.com
```

Verification:

```bash
nslookup -type=A google.com
```

The returned address may differ because Google uses multiple valid A records and DNS-based load balancing.

#### Test Case 3 - Subdomain

Command:

```bash
python resolver.py www.example.com
```

The resolver successfully returned a valid IPv4 address for the subdomain.

#### Test Case 4 - Nonexistent Domain

Command:

```bash
python resolver.py nonexistent-test.invalid
```

Phase 1 did not return an IP address and ended with a generic error. This limitation is improved in Phase 3.

See [`Phase1/README.md`](Phase1/README.md) for complete outputs and verification details.

---

## Phase 2

### Overview

Phase 2 extends the baseline resolver with an in-memory DNS cache.

The cache:

- Uses `(normalized name, record type)` as the key.
- Stores final A records.
- Stores intermediate NS records.
- Stores glue A records.
- Honors record TTL values.
- Removes expired entries.
- Checks the cache before sending a network query.
- Reuses cached referrals to skip unnecessary root queries.
- Logs cache hits, misses, referrals, and network query counts.

### How to Run

```bash
cd Phase2
python resolver.py example.com
```

The cache lasts for one program execution. To test multiple lookups with the same cache, provide multiple domains in one command.

### Test Cases

#### Test Case 1 - Repeated Lookup

Command:

```bash
python resolver.py example.com example.com
```

Expected behavior:

- First lookup: `[CACHE MISS]`
- Network queries are sent.
- Second lookup: `[CACHE HIT]`
- No new network query is sent for the second lookup.

#### Test Case 2 - TTL Expiration

Command:

```bash
python test_ttl.py
```

Expected behavior:

- Record is available before expiration.
- Record becomes a cache miss after its TTL passes.
- The resolver sends another network query to re-fetch the expired answer.

#### Test Case 3 - Reuse Cached NS and Glue Records

Command:

```bash
python resolver.py example.com google.com
```

Expected behavior:

- The first lookup starts at the root server.
- The second lookup uses a cached `.com` referral.
- The second lookup skips the root server.

See [`Phase2/README.md`](Phase2/README.md) for complete outputs, screenshots, and implementation details.

---

## Phase 3

### Overview

Phase 3 adds two extensions based on gaps between the Phase 2 resolver and the DNS RFCs:

1. **CNAME resolution**
2. **Improved DNS error handling and transaction ID validation**

### Extension 1 - CNAME Resolution

The Phase 2 resolver only looked for direct A records. Some valid domains return a CNAME alias instead.

The Phase 3 resolver now:

- Supports DNS record type 5 (`TYPE_CNAME`).
- Parses CNAME targets as DNS names.
- Follows each alias until an A record is found.
- Caches CNAME records.
- Detects repeated names in a CNAME chain.
- Limits the chain to 10 CNAME records.

This extension follows **RFC 1034 Section 3.6.2**.

### Extension 2 - DNS Errors and Transaction IDs

The Phase 2 resolver did not inspect the DNS RCODE field and did not verify that the response transaction ID matched the original query.

The Phase 3 resolver now recognizes:

- FORMERR
- SERVFAIL
- NXDOMAIN
- NOTIMP
- REFUSED

It also rejects responses whose transaction ID does not match the original query.

This extension follows **RFC 1035 Section 4.1.1**.

### How to Run

```bash
cd Phase3
python resolver.py www.microsoft.com
```

Run more than one lookup with the same in-memory cache:

```bash
python resolver.py example.com www.microsoft.com
```

Run local Phase 3 tests:

```bash
python test_phase3.py
```

### Test Cases

#### Test Case 1 - CNAME Resolution

Command:

```bash
python resolver.py www.microsoft.com
```

Relevant output from testing:

```text
[CNAME] www.microsoft.com -> www.microsoft.com-c-3.edgekey.net
[CNAME] www.microsoft.com-c-3.edgekey.net -> e13678.dscb.akamaiedge.net
23.37.18.39
```

The exact final address may differ because Microsoft and Akamai use DNS load balancing.

Verification:

```powershell
Resolve-DnsName www.microsoft.com
```

The system command showed the same CNAME chain during testing.

#### Test Case 2 - NXDOMAIN Handling

Command:

```bash
python resolver.py nonexistent-example-test-5.com
```

Relevant output:

```text
DNS error: NXDOMAIN: the domain name does not exist
```

This is more specific than the generic error produced by Phase 1.

#### Test Case 3 - Transaction ID and Local Tests

Command:

```bash
python test_phase3.py
```

Expected output:

```text
PASS transaction ID: Transaction ID mismatch: expected 111, received 222
PASS NXDOMAIN: NXDOMAIN: the domain name does not exist
PASS CNAME records are cached
All local Phase 3 tests passed
```

See [`Phase3/README.md`](Phase3/README.md) for complete outputs, screenshots, before-and-after comparisons, and implementation details.

---

## References

- *Implement DNS in a Weekend*: https://implement-dns.wizardzines.com/
- RFC 1034 Section 3.6.2 - Aliases and canonical names
- RFC 1035 Section 3.2.1 - Resource record TTL
- RFC 1035 Section 4.1.1 - DNS header, transaction ID, and RCODE
- RFC 1035 Section 4.1.3 - Resource record format
