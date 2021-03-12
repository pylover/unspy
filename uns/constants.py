import os
import re


IGMP_ADDRESS = '224.0.0.70'
IGMP_PORT = 5333
UDP_READSIZE = 128
VERB_DISCOVER = 1
VERB_ANSWER = 2
VERBS = {
    VERB_DISCOVER: 'discover',
    VERB_ANSWER: 'answer'
}
DEFAULT_DBFILE = os.path.join(os.environ['HOME'], '.cache', 'uns')
DEFAULT_TIMEOUT = 5
BINARY_CONTENTTYPES = [
    re.compile('^image/.*'),
    re.compile('^application/octet-stream'),
]
