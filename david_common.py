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
    # db.new_requester("NoahTurkProject.1024@gmail.com_sandbox", "mturk_sandbox")
    #db.new_requester("NoahTurkProject.1024@gmail.com", "mock")
    # db.new_requester("NoahTurkProject.1024@gmail.com", "mturk")
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

def print_assignment(self):
    requester = self.get_requester()
    fields_to_print = {
        'n_units': len(self.get_units()),
        'data_dir': self.get_data_dir(),
        'status': self.get_status(),
        'requester': f'{requester.requester_name}@{requester.provider_type}',
    }
    str_ = [f"Assignment id={self.db_id}"]
    for k, v in fields_to_print.items():
        str_.append(f" {k} = {str(v)}")
    str_ = ";".join(str_)
    print(str_)

def print_worker(self):
    fields_to_print = {
        'name': self.worker_name,
        'provider': self.provider_type,
    }
    str_ = [f"Worker id={self.db_id}"]
    for k, v in fields_to_print.items():
        str_.append(f" {k} = {str(v)}")
    str_ = ";".join(str_)
    print(str_)

def print_unit(self):
    fields_to_print = {
        'sandbox': self.sandbox,
        'assignment': self.get_assignment().db_id,
        'status': self.get_status(),
        'reward': self.get_pay_amount(),
    }
    str_ = [f"Unit id={self.db_id}"]
    for k, v in fields_to_print.items():
        str_.append(f" {k} = {str(v)}")
    str_ = ";".join(str_)
    print(str_)
