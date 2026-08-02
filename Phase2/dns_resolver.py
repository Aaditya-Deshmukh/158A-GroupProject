import dataclasses
import random
import socket
import struct
import time
from dataclasses import dataclass
from io import BytesIO
from typing import List


TYPE_A = 1
TYPE_NS = 2
TYPE_TXT = 16
CLASS_IN = 1
ROOT_SERVER = "198.41.0.4"


@dataclass
class DNSHeader:
    id: int
    flags: int
    num_questions: int = 0
    num_answers: int = 0
    num_authorities: int = 0
    num_additionals: int = 0


@dataclass
class DNSQuestion:
    name: bytes
    type_: int
    class_: int


def header_to_bytes(header):
    fields = dataclasses.astuple(header)
    return struct.pack("!HHHHHH", *fields)


def question_to_bytes(question):
    return question.name + struct.pack("!HH", question.type_, question.class_)


def encode_dns_name(domain_name):
    encoded = b""
    for part in domain_name.encode("ascii").split(b"."):
        encoded += bytes([len(part)]) + part
    return encoded + b"\x00"


def build_query(domain_name, record_type):
    name = encode_dns_name(domain_name)
    query_id = random.randint(0, 65535)
    header = DNSHeader(
        id=query_id,
        num_questions=1,
        flags=0,
    )
    question = DNSQuestion(
        name=name,
        type_=record_type,
        class_=CLASS_IN,
    )
    return header_to_bytes(header) + question_to_bytes(question)


@dataclass
class DNSRecord:
    name: bytes
    type_: int
    class_: int
    ttl: int
    data: object


@dataclass
class DNSPacket:
    header: DNSHeader
    questions: List[DNSQuestion]
    answers: List[DNSRecord]
    authorities: List[DNSRecord]
    additionals: List[DNSRecord]

@dataclass
class CacheEntry:
    record: DNSRecord
    expires_at: float


# PHASE 2 MODIFICATION:
# DNS records are cached by the pair (normalized name, record type).
class DNSCache:
    def __init__(self):
        self.entries = {}

    def make_key(self, name, record_type):
        if isinstance(name, bytes):
            name = name.decode("ascii")

        normalized_name = name.rstrip(".").lower()
        return normalized_name, record_type

    def put(self, record):
        # Records with TTL 0 must not be reused.
        if record.ttl <= 0:
            return

        key = self.make_key(record.name, record.type_)
        entry = CacheEntry(
            record=record,
            expires_at=time.time() + record.ttl,
        )

        self.entries.setdefault(key, []).append(entry)

    def put_packet(self, packet):
        # Cache answers as well as intermediate NS and glue records.
        records = (
            packet.answers
            + packet.authorities
            + packet.additionals
        )

        for record in records:
            self.put(record)

    def get(self, name, record_type):
        key = self.make_key(name, record_type)
        current_time = time.time()

        valid_entries = [
            entry
            for entry in self.entries.get(key, [])
            if entry.expires_at > current_time
        ]

        if not valid_entries:
            self.entries.pop(key, None)
            return []

        self.entries[key] = valid_entries
        return [entry.record for entry in valid_entries]


# PHASE 2 MODIFICATION:
# The cache remains alive for the duration of one program execution.
CACHE = DNSCache()

# Used to demonstrate whether a lookup actually sent a DNS packet.
NETWORK_QUERY_COUNT = 0


def parse_header(reader):
    items = struct.unpack("!HHHHHH", reader.read(12))
    return DNSHeader(*items)


def parse_question(reader):
    name = decode_name(reader)
    data = reader.read(4)
    type_, class_ = struct.unpack("!HH", data)
    return DNSQuestion(name, type_, class_)


def decode_name(reader):
    parts = []

    while True:
        length_data = reader.read(1)
        if not length_data:
            raise ValueError("Unexpected end of DNS message while decoding name")

        length = length_data[0]
        if length == 0:
            break

        if length & 0xC0:
            parts.append(decode_compressed_name(length, reader))
            break

        parts.append(reader.read(length))

    return b".".join(parts)


def decode_compressed_name(length, reader):
    pointer_bytes = bytes([length & 0x3F]) + reader.read(1)
    pointer = struct.unpack("!H", pointer_bytes)[0]

    current_pos = reader.tell()
    reader.seek(pointer)
    result = decode_name(reader)
    reader.seek(current_pos)

    return result


def ip_to_string(ip):
    return ".".join(str(byte) for byte in ip)


def parse_record(reader):
    name = decode_name(reader)
    data = reader.read(10)
    type_, class_, ttl, data_len = struct.unpack("!HHIH", data)
    if type_ == TYPE_NS:
        record_data = decode_name(reader).decode("ascii")
    elif type_ == TYPE_A:
        record_data = ip_to_string(reader.read(data_len))
    else:
        record_data = reader.read(data_len)

    return DNSRecord(name, type_, class_, ttl, record_data)


def parse_dns_packet(data):
    reader = BytesIO(data)
    header = parse_header(reader)
    questions = [parse_question(reader) for _ in range(header.num_questions)]
    answers = [parse_record(reader) for _ in range(header.num_answers)]
    authorities = [parse_record(reader) for _ in range(header.num_authorities)]
    additionals = [parse_record(reader) for _ in range(header.num_additionals)]

    return DNSPacket(
        header=header,
        questions=questions,
        answers=answers,
        authorities=authorities,
        additionals=additionals,
    )


def send_query(ip_address, domain_name, record_type):
    global NETWORK_QUERY_COUNT

    query = build_query(domain_name, record_type)

    NETWORK_QUERY_COUNT += 1
    print(
        f"[NETWORK QUERY #{NETWORK_QUERY_COUNT}] "
        f"{ip_address} for {domain_name}"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)
        sock.sendto(query, (ip_address, 53))
        data, _ = sock.recvfrom(4096)

    response = parse_dns_packet(data)

    # PHASE 2 MODIFICATION:
    # Cache all records learned from the response, including NS and glue.
    CACHE.put_packet(response)

    return response

# PHASE 2 MODIFICATION:
# Normalize names so Example.COM, example.com, and example.com. use
# the same cache key.
def normalize_name(name):
    if isinstance(name, bytes):
        name = name.decode("ascii")

    return name.rstrip(".").lower()

def get_answer(packet):
    for record in packet.answers:
        if record.type_ == TYPE_A:
            return record.data
    return None


def get_nameserver_ip(packet):
    for record in packet.additionals:
        if record.type_ == TYPE_A:
            return record.data
    return None


def get_nameserver(packet):
    for record in packet.authorities:
        if record.type_ == TYPE_NS:
            return record.data
    return None


def parent_domains(domain_name):
    labels = normalize_name(domain_name).split(".")

    for index in range(len(labels)):
        yield ".".join(labels[index:])


# PHASE 2 MODIFICATION:
# Reuse a cached NS record and its cached glue A record.
def find_cached_nameserver(domain_name):
    for zone_name in parent_domains(domain_name):
        ns_records = CACHE.get(zone_name, TYPE_NS)

        for ns_record in ns_records:
            ns_domain = normalize_name(ns_record.data)
            glue_records = CACHE.get(ns_domain, TYPE_A)

            if glue_records:
                nameserver_ip = glue_records[0].data

                print(
                    f"[CACHE REFERRAL] zone={zone_name}, "
                    f"server={ns_domain}, ip={nameserver_ip}"
                )

                return nameserver_ip

    return None

def resolve(domain_name, record_type=TYPE_A):
    domain_name = normalize_name(domain_name)

    # PHASE 2 MODIFICATION:
    # Check for a valid cached final answer before sending network queries.
    cached_answers = CACHE.get(domain_name, record_type)

    if cached_answers:
        print(f"[CACHE HIT] {domain_name} type={record_type}")
        return cached_answers[0].data

    print(f"[CACHE MISS] {domain_name} type={record_type}")

    nameserver = find_cached_nameserver(domain_name) or ROOT_SERVER

    while True:
        print(f"Querying {nameserver} for {domain_name}")
        response = send_query(nameserver, domain_name, record_type)

        answer_ip = get_answer(response)
        if answer_ip:
            return answer_ip

        nameserver_ip = get_nameserver_ip(response)
        if nameserver_ip:
            nameserver = nameserver_ip
            continue

        nameserver_domain = get_nameserver(response)
        if nameserver_domain:
            nameserver = resolve(nameserver_domain, TYPE_A)
            continue

        raise RuntimeError(
            f"No A answer or usable nameserver referral for {domain_name}"
        )
