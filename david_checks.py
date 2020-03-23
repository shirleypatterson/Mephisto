import sys
import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator

USE_LOCAL = 0
NO_SANDBOX = 1
os.environ["SKIP_LOCALE_REQUIREMENT"]="TRUE"

db = LocalMephistoDB()

# db.new_requester("NoahTurkProject.1024@gmail.com_sandbox", "mturk_sandbox")
#db.new_requester("NoahTurkProject.1024@gmail.com", "mock")
# db.new_requester("NoahTurkProject.1024@gmail.com", "mturk")
#Mock never completes properly - you can't test seeing worker id

operator = Operator(db)
provider_type = "mock" if USE_LOCAL else ("mturk" if NO_SANDBOX else "mturk_sandbox")
requester = db.find_requesters(provider_type=provider_type)[-1]
requester.register()
requester_name = requester.requester_name
architect_type = "local" if USE_LOCAL else "heroku"
assert USE_LOCAL or NO_SANDBOX or requester_name.endswith('_sandbox'), "Should use a sandbox for testing"
hit_title = "Fruit video task (best done on mobile phone)"

# data stored to:
# /private/home/dnovotny/mephisto/data/data/runs/NO_PROJECT/4/2/2
all_hits = requester.get_all_hits()
all_hits = [h for h in all_hits if hit_title in h['Title']]
print(f'There are {len(all_hits)} HITs on the MTurk site:')
for hit in all_hits:
    stat_str = (
        f"{hit['Title']}: "
        + f" status={hit['HITStatus']};"
        + f" avail={hit['NumberOfAssignmentsAvailable']}"
        + f" completed={hit['NumberOfAssignmentsCompleted']}"
        + f" pending={hit['NumberOfAssignmentsPending']}"
        + f" expires={hit['Expiration']}"
    )
    print(stat_str)

operator.shutdown()