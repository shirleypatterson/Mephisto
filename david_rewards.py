import sys
import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator
from datetime import datetime
import pytz
from termcolor import colored
# from botocore import errorfactory 
# from botocore.errorfactory import RequestError
# from botocore.exceptions import RequestError

from david_common import get_all_hits, init_david, \
    load_data_check_info, print_assignment, print_unit, print_agent, \
    get_boto_client, pay_qr_bonus

operator, requester = init_david(NO_SANDBOX=1)
db = operator.db
client = get_boto_client(requester)
do_not_check_qr = True # override automated qr code check
bonus_amount = 0.3

# task_run_id = '20'
task_run_id = '29'
data_check_root = '/checkpoint/dnovotny/object_videos_amt/mephisto_runs/NO_PROJECT/'
dry_run = False

REJECT_ASSIGN_IDS = [364,355]

assignments = db.find_assignments(
    task_run_id=task_run_id,
)


for asgn in assignments:
    print_assignment(asgn)
    if asgn.get_status()=='completed':
        units = asgn.get_units()
        for unit in units:
            print_unit(unit)
            agent = unit.get_assigned_agent()
            print_agent(agent)

            if agent.get_status()=='completed':
                data_check_info, video_file = load_data_check_info(
                    agent, data_check_root=data_check_root)
                
                # for now, accept all that pass is_video check
                
                # is video?
                if not data_check_info['is_video']:
                    print(colored(f'not a video: {video_file}', 'red'))
                    print('-> REJECT')
                    if not dry_run:
                        try:
                            agent.reject_work(
                                'Unfortunately, the uploaded file is not a video.' 
                                'Hence, we are rejecting the HIT, sorry.'
                            )
                        except client.exceptions.RequestError as e:
                            print('Cant reject the agent '
                                    '(probably already rejected before):')
                            print(e)
                    continue

                # check manually rejected assign ids
                if int(asgn.db_id) in REJECT_ASSIGN_IDS:
                    print(colored(f'manual reject: {video_file}', 'red'))
                    print('-> REJECT')
                    if not dry_run:
                        try:
                            agent.reject_work(
                                'Unfortunately, we cant accept your video, sorry.'
                            )
                        except client.exceptions.RequestError as e:
                            print('Cant reject the agent '
                                    '(probably already rejected before):')
                            print(e)
                    continue

                # if everything above passes -> approve
                print(colored(f'good: {video_file}', 'green'))
                print('-> APPROVE')
                already_approved = False
                if not dry_run:
                    try:
                        agent.approve_work()
                    except client.exceptions.RequestError as e:
                        print('Cant reward the agent '
                            '(probably already rewarded):')
                        print(e)
                        already_approved = True

                # pay bonus for QR
                if data_check_info['marked_with_qr']:
                    if not already_approved:  # make sure we do not pay twice!
                        if data_check_info['has_qr']:
                            print('-> PAYING BONUS')
                            if not dry_run:
                                pay_qr_bonus(agent, bonus_amount)        
                        else:
                            print(colored(
                                'No QR present (despite indicated)', 'red'))
                            if do_not_check_qr:
                                print('-> PAYING BONUS ANYWAY')
                                if not dry_run:
                                    pay_qr_bonus(agent, bonus_amount)
                            continue
                    else:
                         print('-> BONUS ALREADY PAYED')
                    

    print('---')

operator.shutdown()