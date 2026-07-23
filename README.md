\# Phase 1 - Baseline Resolver



\# Running result

\# Several different domains resolving correctly

\# For "example.com"



C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>python resolver.py example.com

Querying 198.41.0.4 for example.com

Querying 192.41.162.30 for example.com

Querying 108.162.192.162 for example.com

104.20.23.154



\# Verification



C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>nslookup example.com

Server:  ns1.sonic.net

Address:  50.0.1.1



Non-authoritative answer:

Name:    example.com

Addresses:  2606:4700:10::6814:179a

&#x20;         2606:4700:10::ac42:93f3

&#x20;         104.20.23.154

&#x20;         172.66.147.243



\-It shows the address are 104.20.23.154





\# For "python.org"



C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>python resolver.py python.org

Querying 198.41.0.4 for python.org

Querying 199.249.112.1 for python.org

Querying 205.251.196.110 for python.org

151.101.192.223



\# Verification

C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>nslookup -type=A python.org

Server:  ns1.sonic.net

Address:  50.0.1.1



Non-authoritative answer:

Name:    python.org

Addresses:  151.101.0.223

&#x20;         151.101.64.223

&#x20;         151.101.192.223

&#x20;         151.101.128.223



\-It shows the address are 151.101.192.223





\# A domain that returns multiple A records.

\# For "google.com"



C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>python resolver.py google.com

Querying 198.41.0.4 for google.com

Querying 192.41.162.30 for google.com

Querying 216.239.34.10 for google.com

142.251.218.110



\# Verification



\# First time

C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>nslookup -type=A google.com

Server:  ns1.sonic.net

Address:  50.0.1.1



Non-authoritative answer:

Name:    google.com

Address:  142.251.218.14



\# Second time

C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>nslookup -type=A google.com

Server:  ns1.sonic.net

Address:  50.0.1.1



Non-authoritative answer:

Name:    google.com

Address:  142.251.215.206



\# Third time

C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>nslookup -type=A google.com

Server:  ns1.sonic.net

Address:  50.0.1.1



Non-authoritative answer:

Name:    google.com

Address:  142.251.210.142



\-The IP returned by my resolver may differ from the IP returned by nslookup because google.com has multiple valid A records and uses DNS-based load balancing. Both results are valid.



\# A subdomain



\# For "www.example.com"



C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>python resolver.py www.example.com

Querying 198.41.0.4 for www.example.com

Querying 192.41.162.30 for www.example.com

Querying 108.162.192.162 for www.example.com

104.20.23.154



\# Verification



C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>nslookup -type=A www.example.com

Server:  ns1.sonic.net

Address:  50.0.1.1



Non-authoritative answer:

Name:    www.example.com

Addresses:  172.66.147.243

&#x20;         104.20.23.154



\-It shows the address are 104.20.23.154, which are same as "example.com" too.





\# An error case



\# For "nonexistent-test.invalid"



C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>python resolver.py nonexistent-test.invalid

Querying 198.41.0.4 for nonexistent-test.invalid

Traceback (most recent call last):

&#x20; File "C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject\\resolver.py", line 21, in <module>

&#x20;   raise SystemExit(main())

&#x20;                    ^^^^^^

&#x20; File "C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject\\resolver.py", line 13, in main

&#x20;   address = resolve(domain\_name, TYPE\_A)

&#x20;             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

&#x20; File "C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject\\part3.py", line 102, in resolve

&#x20;   raise Exception('something went wrong')

Exception: something went wrong



\# Verification



C:\\Users\\kofan\\OneDrive\\Documents\\GitHub\\158A-GroupProject>nslookup -type=A nonexistent-test.invalid

Server:  ns1.sonic.net

Address:  50.0.1.1



\*\*\* ns1.sonic.net can't find nonexistent-test.invalid: Non-existent domain



\-The verification command confirmed that the domain does not exist. My resolver did not return an IP address and terminated with an exception. This shows that the resolver detected an unsuccessful DNS lookup, but the current error handling is not user-friendly because it prints a traceback and a generic error message.











