# Phase 2 - DNS Resolver with TTL Cache

## Overview

Phase 2 extends the baseline iterative DNS resolver from Phase 1 by adding an in-memory DNS record cache.

The resolver now:

- Stores DNS records using `(name, record type)` as the cache key.
- Stores final A records and intermediate NS/glue records.
- Honors the TTL of each cached record.
- Removes expired records instead of serving stale data.
- Checks the cache before sending a network query.
- Reuses cached NS and glue records to skip unnecessary hierarchy lookups.
- Logs cache hits, cache misses, cached referrals, and network query counts.

The cache remains available during one execution of the program. Therefore, multiple domains can be supplied in one command so they share the same cache.

## Files

```text
Phase2/
├── dns_resolver.py
├── resolver.py
├── test_ttl.py
├── README.md
├── repeated_lookup.png
├── different_name.png
└── ttl_test.png
```

## How to Run

Clone the repository:

git clone https://github.com/Aaditya-Deshmukh/158A-GroupProject.git

cd 158A-GroupProject

cd Phase2

### Resolve one domain

python resolver.py example.com

### Resolve multiple domains in the same process

python resolver.py example.com google.com

### Run the TTL test

python test_ttl.py

## Phase 2 Implementation

### Cache key

DNS records are cached using:

(normalized domain name, record type)

Domain names are normalized by converting the name to lowercase, removing a trailing period, and converting byte strings to regular Python strings when necessary.

### Cached records

The resolver caches records from the Answer, Authority, and Additional sections. This allows the cache to store final A records, NS records learned during referrals, and glue A records for nameservers.

### TTL handling

Each cache entry stores the DNS resource record and the time when the record expires. The expiration time is calculated as:

current time + record TTL

Before returning a cached entry, the resolver checks whether its expiration time has passed. Expired entries are removed and are not served. Records with TTL 0 are not reused.

### Cache logging

[CACHE MISS] means no valid cached answer was found.

[CACHE HIT] means the answer was returned from cache without sending a new network query.

[CACHE REFERRAL] means the resolver reused cached NS and glue records.

[NETWORK QUERY #N] shows that an actual DNS packet was sent.

## Test Cases

### Test Case 1 - Repeated Lookup Uses the Cache

Command:

python resolver.py example.com example.com

Relevant output:

Resolving example.com
[CACHE MISS] example.com type=1
Querying 198.41.0.4 for example.com
[NETWORK QUERY #1] 198.41.0.4 for example.com
Querying 192.41.162.30 for example.com
[NETWORK QUERY #2] 192.41.162.30 for example.com
Querying 108.162.192.162 for example.com
[NETWORK QUERY #3] 108.162.192.162 for example.com
104.20.23.154

Resolving example.com
[CACHE HIT] example.com type=1
104.20.23.154

Verification:

The first lookup was a cache miss and required three network queries. The second lookup displayed [CACHE HIT] and did not send another network query. The network query count remained at three.

Screenshot:

repeated_lookup.png

### Test Case 2 - TTL Expiration and Re-fetching

Command:

python test_ttl.py

Relevant output:

Adding record with TTL = 2 seconds
Before expiration:
CACHE HIT
Waiting 3 seconds...
After expiration:
CACHE MISS

Re-fetch test:
[CACHE MISS] example.com type=1
Querying 198.41.0.4 for example.com
[NETWORK QUERY #1] 198.41.0.4 for example.com
Querying 192.41.162.30 for example.com
[NETWORK QUERY #2] 192.41.162.30 for example.com
Querying 108.162.192.162 for example.com
[NETWORK QUERY #3] 108.162.192.162 for example.com

Second lookup after expiration:
[CACHE MISS] example.com type=1
[CACHE REFERRAL] zone=example.com, server=hera.ns.cloudflare.com, ip=108.162.192.162
Querying 108.162.192.162 for example.com
[NETWORK QUERY #4] 108.162.192.162 for example.com
Network queries after first lookup: 3
Network queries after expired lookup: 4

Verification:

The synthetic test record had a TTL of two seconds. It produced a cache hit before expiration and a cache miss after waiting three seconds. In the real-domain test, the network query count increased from three to four after the final cached A record was expired. This shows that the resolver re-fetched the answer instead of serving the expired record.

Screenshot:

ttl_test.png

### Test Case 3 - Reusing Cached NS and Glue Records

Command:

python resolver.py example.com google.com

Relevant output:

Resolving example.com
[CACHE MISS] example.com type=1
Querying 198.41.0.4 for example.com
[NETWORK QUERY #1] 198.41.0.4 for example.com
Querying 192.41.162.30 for example.com
[NETWORK QUERY #2] 192.41.162.30 for example.com
Querying 108.162.192.162 for example.com
[NETWORK QUERY #3] 108.162.192.162 for example.com
104.20.23.154

Resolving google.com
[CACHE MISS] google.com type=1
[CACHE REFERRAL] zone=com, server=l.gtld-servers.net, ip=192.41.162.30
Querying 192.41.162.30 for google.com
[NETWORK QUERY #4] 192.41.162.30 for google.com
Querying 216.239.34.10 for google.com
[NETWORK QUERY #5] 216.239.34.10 for google.com
142.251.214.46

Verification:

The first lookup began at the root server and cached the .com NS and glue records. The second lookup displayed [CACHE REFERRAL] zone=com and began directly at the cached .com TLD server. It did not query root server 198.41.0.4 again for google.com.

Screenshot:

different_name.png

## Test Summary

- Repeated lookup is served from cache: Passed
- Cache hit sends no new network query: Passed
- Cached entry expires after TTL: Passed
- Expired entry is not served: Passed
- Expired answer is re-fetched: Passed
- Intermediate NS/glue records are reused: Passed
- Different domain under the same TLD skips root: Passed

## Known Behavior

The cache is stored in memory and is cleared when the Python program exits. To test cache reuse, multiple domains must be supplied in the same command.

The resolver currently returns one A record even when a DNS response contains multiple A records. The exact returned IP address may change between runs because some domains use multiple valid A records or DNS-based load balancing.