import sys
import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from david_common import init_david

from datetime import datetime
import pytz

operator, requester = init_david(NO_SANDBOX=0)
db = operator.db

if requester.is_sandbox():
    os.environ["SKIP_LOCALE_REQUIREMENT"]="TRUE"

# data stored to:
# /private/home/dnovotny/mephisto/data/data/runs/NO_PROJECT/4/2/2

#frame height greater than 650
#task timeout 18000=5 hours
#The argument string goes through shlex.split twice, hence the quoting.
ARG_STRING = (
    "--blueprint-type static "
    f"--architect-type {'heroku'} "
    f"--requester-name {requester.requester_name} "
    '--task-title "\\"Fruit video task - 1unit\\"" '
    '--task-description "\\"Take a video of an orange from all sides.\\"" '
    "--task-reward 1.2 "
    "--task-tags static,task,testing "
    '--data-csv "data.csv" '
    '--assignment-duration-seconds 60 ' # max time for a worker to complete.
    '--task-source "merged.out.html" '
    #'--allow-mobile required '
    '--extra-source-dir payload '
    #'--html-source "task.html" '
    f"--units-per-assignment 1"
)

try:
    operator.parse_and_launch_run(shlex.split(ARG_STRING))
    print(operator.get_running_task_runs())
    while len(operator.get_running_task_runs()) > 0:
        # operator.ping_architect()
        task_runs = operator.get_running_task_runs()
        print(datetime.now(tz=pytz.timezone('US/Pacific')))
        print(f'Operator running {len(task_runs)} task runs:') 
        for task_run_id in task_runs:
            print(f'=> Task run {task_run_id} <=')
            task_run_asgn = db.find_assignments(task_run_id=task_run_id)
            print(f'=> Assignments #={len(task_run_asgn)} <=')
            for asgn in task_run_asgn:
                asgn_units = asgn.get_units()
                print(str(asgn))
                # print('=> Units <=')
                # for unit in asgn_units:
                #     print(str(unit))
                #     agent = unit.get_assigned_agent()
                #     if agent is not None:
                #         print(str(agent))

            print('---')

        time.sleep(5)
    
            

except Exception as e:
    import traceback
    traceback.print_exc()
except (KeyboardInterrupt, SystemExit) as e:
    pass
finally:
    operator.shutdown()
