import time
import dns_resolver

from dns_resolver import CACHE, CLASS_IN, DNSRecord, TYPE_A, resolve


record = DNSRecord(
    name=b"ttl-test.example",
    type_=TYPE_A,
    class_=CLASS_IN,
    ttl=2,
    data="1.2.3.4",
)

print("Adding record with TTL = 2 seconds")
CACHE.put(record)

print("Before expiration:")
result = CACHE.get("ttl-test.example", TYPE_A)
print("CACHE HIT" if result else "CACHE MISS")

print("Waiting 3 seconds...")
time.sleep(3)

print("After expiration:")
result = CACHE.get("ttl-test.example", TYPE_A)
print("CACHE HIT" if result else "CACHE MISS")

print("\nRe-fetch test:")

CACHE.entries.clear()
dns_resolver.NETWORK_QUERY_COUNT = 0

resolve("example.com", TYPE_A)
first_count = dns_resolver.NETWORK_QUERY_COUNT

key = CACHE.make_key("example.com", TYPE_A)

for entry in CACHE.entries[key]:
    entry.expires_at = 0

print("\nSecond lookup after expiration:")
resolve("example.com", TYPE_A)
second_count = dns_resolver.NETWORK_QUERY_COUNT

print("Network queries after first lookup:", first_count)
print("Network queries after expired lookup:", second_count)