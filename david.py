import sys
import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from david_common import init_david

operator, requester = init_david(NO_SANDBOX=0)

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
    '--task-title "\\"Fruit video task (Do not accept this hit please)\\"" '
    '--task-description "\\"Take a video of an orange from all sides.\\"" '
    "--task-reward 1.2 "
    "--task-tags static,task,testing "
    '--data-csv "data.csv" '
    '--assignment-duration-seconds 18000 ' # max time for a worker to complete.
    '--task-source "merged.out.html" '
    #'--allow-mobile required '
    '--extra-source-dir payload '
    #'--html-source "task.html" '
    f"--units-per-assignment 10 "    
)

try:
    operator.parse_and_launch_run(shlex.split(ARG_STRING))
    print(operator.get_running_task_runs())
    while len(operator.get_running_task_runs()) > 0:
        # operator.ping_architect()
        print(f'Operator running {operator.get_running_task_runs()}')
        time.sleep(10)
except Exception as e:
    import traceback
    traceback.print_exc()
except (KeyboardInterrupt, SystemExit) as e:
    pass
finally:
    operator.shutdown()
