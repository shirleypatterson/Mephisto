import sys
import os
import time
import shlex
from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.operator import Operator

def init_david(NO_SANDBOX=0):
    db = LocalMephistoDB()
    # db.new_requester("NoahTurkProject.1024@gmail.com_sandbox", "mturk_sandbox")
    #db.new_requester("NoahTurkProject.1024@gmail.com", "mock")
    #db.new_requester("NoahTurkProject.1024@gmail.com", "mturk")
    operator = Operator(db)
    provider_type = ("mturk" if NO_SANDBOX else "mturk_sandbox")
    requester = db.find_requesters(provider_type=provider_type)[-1]
    requester.register()
    return  operator, requester