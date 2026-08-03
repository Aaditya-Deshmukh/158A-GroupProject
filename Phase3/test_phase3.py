from dns_resolver import (
    CACHE,
    CLASS_IN,
    DNSHeader,
    DNSPacket,
    DNSQuestion,
    DNSRecord,
    DNSResponseError,
    TYPE_A,
    TYPE_CNAME,
    validate_response,
)


def empty_packet(header):
    return DNSPacket(
        header=header,
        questions=[],
        answers=[],
        authorities=[],
        additionals=[],
    )


def test_transaction_id():
    packet = empty_packet(DNSHeader(id=222, flags=0))

    try:
        validate_response(packet, 111)
    except DNSResponseError as error:
        print("PASS transaction ID:", error)
    else:
        raise AssertionError("Transaction ID mismatch was not detected")


def test_nxdomain():
    # RCODE 3 means NXDOMAIN.
    packet = empty_packet(DNSHeader(id=111, flags=3))

    try:
        validate_response(packet, 111)
    except DNSResponseError as error:
        print("PASS NXDOMAIN:", error)
    else:
        raise AssertionError("NXDOMAIN was not detected")


def test_cname_cache():
    CACHE.entries.clear()

    cname = DNSRecord(
        name=b"www.test.example",
        type_=TYPE_CNAME,
        class_=CLASS_IN,
        ttl=60,
        data="test.example",
    )
    address = DNSRecord(
        name=b"test.example",
        type_=TYPE_A,
        class_=CLASS_IN,
        ttl=60,
        data="1.2.3.4",
    )

    CACHE.put(cname)
    CACHE.put(address)

    cname_result = CACHE.get("www.test.example", TYPE_CNAME)
    address_result = CACHE.get("test.example", TYPE_A)

    assert cname_result[0].data == "test.example"
    assert address_result[0].data == "1.2.3.4"
    print("PASS CNAME records are cached")


if __name__ == "__main__":
    test_transaction_id()
    test_nxdomain()
    test_cname_cache()
    print("All local Phase 3 tests passed")
