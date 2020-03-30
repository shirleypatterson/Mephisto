import sys
import os
import time
import shlex
from david_common import init_david

operator, requester = init_david(NO_SANDBOX=0)

HIT_TITLE = "Fruit video task (best done on mobile phone)"

all_hits = requester.get_all_hits()
all_hits = [h for h in all_hits if HIT_TITLE in h['Title']]
print(f'There are {len(all_hits)} HITs on the MTurk site:')
print('Destroying all!')

for hit in all_hits:
    hit_id = hit['HITId']
    hit_title = hit['Title']
    print(f'Destroying hit title={hit_title}; id={hit_id}')
    status = hit['HITStatus']
    requester.delete_hit(hit_id, status, approve_all=True)