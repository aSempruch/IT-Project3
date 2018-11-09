DNS Project - Phase 2
---

Project was tested with Python 3.7

Python files are distributed among directories to allow for importing custom modules and reuse of code

TSCOM.py and TSEDU.py are simply importing the same ts.py module 
and executing it with different parameters

Execution from project root
---
TSCOM server:
`python server/TSCOM.py PROJ2-DNSCOM.txt`

TSEDU server:
`python server/TSEDU.py PROJ2-DNSEDU.txt`

RS server:
`python server/RS.py <TSCOM-hostname> <TSEDU-hostname> PROJ2-DNSRS.txt`

Client:
`python client/CLIENT.py <RS-hostname> PROJ2-HNS.txt`