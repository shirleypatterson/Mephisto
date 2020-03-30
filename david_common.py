import sys
import os
import time
import shlex
from datetime import datetime
import pytz

from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator

def init_david(NO_SANDBOX=0):
    db = LocalMephistoDB()
    #db.new_requester("NoahTurkProject.1024@gmail.com_sandbox", "mturk_sandbox")
    #db.new_requester("NoahTurkProject.1024@gmail.com", "mock")
    #db.new_requester("NoahTurkProject.1024@gmail.com", "mturk")
    operator = Operator(db)
    provider_type = ("mturk" if NO_SANDBOX else "mturk_sandbox")
    requester = db.find_requesters(provider_type=provider_type)[-1]
    requester.register()
    return  operator, requester

def load_possible_classes():
    with open('./classes.csv') as f:
        classes = [ln.lower().strip() for ln in f.readlines()]
    return classes

def make_object_class_data_file(hits_per_object, data_root='./data/launches/'):
    now = datetime.now(tz=pytz.timezone('US/Pacific'))
    stamp = now.strftime('%y-%m-%d_%H-%M-%S')
    data_file = os.path.join(data_root, stamp + '.csv')
    print(f'Exporting data file: {data_file}')
    with open(data_file, 'w') as f:
        f.write('object_class\n')
        for obclass, n_hits in hits_per_object.items():
            for _ in range(n_hits):
                ln = f'{obclass}\n'
                f.write(ln)
    # with open(data_file) as f:
    #     for line in f.readlines():
    #         print(line.strip())
    return data_file
    
    