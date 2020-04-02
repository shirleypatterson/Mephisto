import sys
import os
import time
import shlex
import json
from datetime import datetime
import pytz
import random

from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator

#########################
# Task setup
#########################

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

def make_obj_class_selection_ul(cls_sel):
    """
    Given a list of classes cls_sel (e.g. [banana, apple, orange]),
    creates a html string in the following format:
        <li>ob_class_1
        <li>ob_class_2
        <li>ob_class_3
        ...
        <li>ob_class_N
    This is used as input data to the AMT object video collection heroku server.
    """
    ob_str=''
    for cls_ in cls_sel:
        ob_str+=f'<li>{cls_}'
    # assert ',' not in ob_str, 'commas not allowed in the string'
    return ob_str

def multichoice_hits(hits_per_object, multichoice, seed=0):
    """
    Generate a list of strings corresponding to the object class lists
    used for defining the subset of object classes to capture in each HIT.
    """
    objs_for_hit = []
    remaining_hits_per_object_ = hits_per_object.copy()
    strs = []
    random.seed(seed)  # set seed for reproducibility ...
    while sum(remaining_hits_per_object_.values()) > 0:
        # select "multichoice" unique random classes from the remaining ones
        unq_classes = list(set(remaining_hits_per_object_.keys()))
        multichoice_ = min(multichoice, len(unq_classes))
        cls_sel = sorted(random.sample(unq_classes, multichoice_))
        # erase the selected classes from remaining_hits_per_object_
        for cls_ in cls_sel:
            remaining_hits_per_object_[cls_]-=1
            if remaining_hits_per_object_[cls_]==0:
                del remaining_hits_per_object_[cls_]
        # create the <ul>...<\ul> string
        ob_str = make_obj_class_selection_ul(cls_sel)
        strs.append(ob_str)
    return strs

def make_object_class_data_file(
    hits_per_object: dict, html: str, 
    data_root='./data/launches/', 
    multichoice: int=1
):
    
    now = datetime.now(tz=pytz.timezone('US/Pacific'))
    stamp = now.strftime('%y-%m-%d_%H-%M-%S')
    data_file = os.path.join(data_root, stamp + '.csv')
    print(f'Exporting data file: {data_file}')
    
    if multichoice > 1:
        # make a list of <ul>...<\ul> strings for the HIT inputs
        object_class_tokens = multichoice_hits(hits_per_object, multichoice)
        with open(data_file, 'w') as f:
            f.write('object_class\n')
            for obclass_token in object_class_tokens:
                ln = f'{obclass_token}\n'
                f.write(ln)
        # the preview ul has all the available classes
        possible_classes_str = ', '.join(list(set(hits_per_object.keys())))
        possible_classes_str = (
            f'[Up to {multichoice} categories from '
            f'<it>{{{possible_classes_str}}}</it> '
            '- the actual list of possibilities will be specified '
            'after accepting the HIT]'
        )
        obclass_token = make_obj_class_selection_ul([possible_classes_str])
        # obclass_token = make_obj_class_selection_ul(
        #     list(set(hits_per_object.keys())))
        with open(html, 'r') as f:
            html_data = f.read()
        # replace the token
        html_data_rep = html_data.replace('${object_class}', obclass_token)
        assert html_data_rep!=html_data, '${object_class} token not found!'

    else:
        with open(data_file, 'w') as f:
            f.write('object_class\n')
            for obclass, n_hits in hits_per_object.items():
                for _ in range(n_hits):
                    ln = f'{obclass}\n'
                    f.write(ln)
        # make the preview page by replacing the ${object_class} token
        possible_classes_str = ', '.join(list(set(hits_per_object.keys())))
        possible_classes_str = f'[One of ({possible_classes_str}) - the actual object will be specified after accepting the HIT]'
        with open(html, 'r') as f:
            html_data = f.read()
        # replace the token
        html_data_rep = html_data.replace('${object_class}', possible_classes_str)
        assert html_data_rep!=html_data, '${object_class} token not found!'
    
    preview_html_file = os.path.join(data_root, stamp + '_preview.html')
    print(f'Exporting preview file: {preview_html_file}')
    with open(preview_html_file, 'w') as f:
        f.write(html_data_rep)
        
    # print('===== preview html =====')
    # with open(preview_html_file) as f:
    #     for line in f.readlines():
    #         print(line.strip())
    print('===== data .csv file =====')
    with open(data_file) as f:
        for line in f.readlines():
            print(line.strip())
    return data_file, preview_html_file


#########################
# data checks
#########################

def load_data_check_info(agent, data_check_root=None):
    data_dir = agent.get_data_dir()
    video_file = [f for f in os.listdir(data_dir) if f!='agent_data.json'][0]
    video_file = os.path.join(data_dir, video_file)
    check_dir = os.path.join(data_check_root, *data_dir.split(os.sep)[-3:])
    check_json = os.path.join(check_dir, 'data_check_flags.json')
    with open(check_json, 'r') as f:
        check_data = json.load(f)
    return check_data, video_file

#########################
# HIT manipulation
#########################

def pay_qr_bonus(agent, bonus_amount, max_allowed_bonus=1.):
    """
    Pays the worker of the agent bonus for the QR codes.
    """
    # client = get_boto_client(agent.get_assignment().get_requester())
    assert bonus_amount <= max_allowed_bonus, \
        f'Are you sure you want to pay a bonus of {bonus_amount}?'
    reason = "Thanks for the QR codes!"
    worker = agent.get_worker()
    unit = agent.get_unit()
    worker.bonus_worker(bonus_amount, reason, unit)

def get_boto_client(requester):
    return requester._get_client(requester._requester_name)

def get_all_hits(client):
    """ Get all HITs on the MTurk server """
    print('Getting all HITs (might take some time) ...')
    hits = []
    hits = client.get_paginator(
        'list_hits').paginate(
            PaginationConfig={'PageSize': 100}).build_full_result()
    return hits['HITs']

def delete_hit(client, hit_id, hit_status, approve_all=False):
    """ Delete, and optionally approve (approve_all=True), a HIT """
    if hit_status=='Assignable':
        response = client.update_expiration_for_hit(
            HITId=hit_id,
            ExpireAt=datetime(2015, 1, 1) # some time in history
        )
    elif hit_status=='Reviewable' and approve_all:
        approve_assignments_for_hit(
            client, hit_id, override_rejection=True
        )
        
    # Delete the HIT
    try:
        client.delete_hit(HITId=hit_id)
    except Exception as e:
        print(f'{hit_id} not deleted:')
        print(e)
    else:
        print(f'{hit_id} deleted')

#########################
# Printing
#########################

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

def print_agent(self):
    fields_to_print = {
        'status': self.get_status(),
        'data_dir': self.get_data_dir(),
    }
    str_ = [f"Agent id={self.db_id}"]
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

