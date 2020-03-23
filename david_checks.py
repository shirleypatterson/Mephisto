import sys
import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator

from datetime import datetime
import pytz


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

try:
    # this has to be hidden in the requester code
    client = requester._get_client(requester._requester_name)

    # get all hits
    all_hits = requester.get_all_hits()
    all_hits = [h for h in all_hits if hit_title in h['Title']]
    print(f'There are {len(all_hits)} HITs on the MTurk site:')
    for hit in all_hits:
        stat_str = (
            f"{hit['Title']}: \n"
            + f" status={hit['HITStatus']}\n"
            + f" avail={hit['NumberOfAssignmentsAvailable']}\n"
            + f" completed={hit['NumberOfAssignmentsCompleted']}\n"
            + f" pending={hit['NumberOfAssignmentsPending']}\n"
            + f" created={hit['CreationTime']}\n"
            + f" expires={hit['Expiration']}\n"
        )

        now = datetime.now(tz=pytz.timezone('US/Pacific'))
        expires = hit['Expiration']
        if now > expires:
            stat_str += f" -> expired!\n"
        
        # http response
        asgn_response = client.list_assignments_for_hit(
            HITId=hit['HITId'],
            MaxResults=100,
            # AssignmentStatuses=[
            #     'Submitted'
            # ]
        )
        num_asgn = asgn_response['NumResults']
        stat_str += f" num_asgn={num_asgn}\n"
        if num_asgn > 0:
            for asgn in asgn_response['Assignments']:
                stat_str += f"   AssignmentId={asgn['AssignmentId']}\n"
                stat_str += f"   AssignmentStatus={asgn['AssignmentStatus']}\n"
                # if asgn['AssignmentStatus']=='Submitted':
                #     print('\n\n   => Approving! <=\n\n')
                #     approve_response = client.approve_assignment(
                #             AssignmentId=asgn['AssignmentId'],
                #         )
                
        # if hit['NumberOfAssignmentsCompleted'] > 0:
        #     import pdb; pdb.set_trace()

        print(stat_str)
   

except Exception as e:
    import traceback
    traceback.print_exc()

except (KeyboardInterrupt, SystemExit) as e:
    pass

finally:
    operator.shutdown()
