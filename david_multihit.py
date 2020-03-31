import sys
import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from david_common import init_david, load_possible_classes, \
    make_object_class_data_file, print_worker, print_assignment, print_unit

from datetime import datetime
import pytz

operator, requester = init_david(NO_SANDBOX=1)
db = operator.db

if requester.is_sandbox():
    os.environ["SKIP_LOCALE_REQUIREMENT"]="TRUE"
else:
    os.environ["PRODUCTION_AMT_RUN"]="TRUE"
    print('Warning: Production AMT run!')

# data stored to:
# /private/home/dnovotny/mephisto/data/data/runs/NO_PROJECT/4/2/2

object_classes = load_possible_classes()

hits_per_class = {
    'apple': 10,
    'banana': 10,
    'orange': 10,
}

assert all(k in object_classes for k in hits_per_class)

n_hits_total = sum(hits_per_class.values())
print(f'Submitting {n_hits_total} HITs:')
for clas, n_hits in hits_per_class.items():
    print(f'{clas:20s}: {n_hits} hits')

html_source = "merged.out.html"
data_file, preview_html = make_object_class_data_file(hits_per_class, html_source)

#frame height greater than 650
#task timeout 18000=5 hours
#The argument string goes through shlex.split twice, hence the quoting.
ARG_STRING = (
    "--blueprint-type static "
    f"--architect-type {'heroku'} "
    f"--requester-name {requester.requester_name} "
    '--task-title "\\"Fruit video task v4\\"" '
    '--task-description "\\"Take a video of a piece of fruit from all sides.\\"" '
    "--task-reward 1.2 "
    "--task-tags static,task,testing "
    f'--data-csv "{data_file}" '
    '--assignment-duration-seconds 1200 ' # max time for a worker to complete.
    f'--task-source "{html_source}" '
    f'--preview-source "{preview_html}" '
    #'--allow-mobile required '
    '--extra-source-dir payload '
    #'--html-source "task.html" '
    f"--units-per-assignment 1"
)

print(ARG_STRING)

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
                print_assignment(asgn)
                # print('=> Units <=')
                # for unit in asgn_units:
                #     print_unit(unit)
                    # agent = unit.get_assigned_agent()
                    # if agent is not None:
                    #     print(str(agent))
            print('---')

        time.sleep(10)
    
            

except Exception as e:
    import traceback
    traceback.print_exc()
except (KeyboardInterrupt, SystemExit) as e:
    pass
finally:
    operator.shutdown()
