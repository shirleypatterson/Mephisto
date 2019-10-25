#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod, abstractproperty
from mephisto.providers.mock.provider_type import PROVIDER_TYPE
from mephisto.data_model.agent_state import AgentState
from mephisto.core.utils import get_crowd_provider_from_type, get_task_runner_from_type
from mephisto.data_model.assignment import Unit
from mephisto.data_model.requester import Requester
from mephisto.data_model.worker import Worker
from mephisto.data_model.agent import Agent

from typing import List, Optional, Tuple, Dict, Any, ClassVar, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB
    from mephisto.data_model.task import TaskRun


class CrowdProvider(ABC):
    """
    Base class that defines the required functionality for
    the mephisto system to be able to interface with an
    external crowdsourcing vendor.

    Implementing the methods within, as well as supplying
    wrapped Unit, Requester, Worker, and Agent classes
    should ensure support for a vendor.
    """

    UnitClass: ClassVar[Type[Unit]] = Unit

    RequesterClass: ClassVar[Type[Requester]] = Requester

    WorkerClass: ClassVar[Type[Worker]] = Worker

    AgentClass: ClassVar[Type[Agent]] = Agent

    SUPPORTED_TASK_TYPES: ClassVar[List[str]]

    def __init__(self, db: "MephistoDB"):
        """
        Crowd provider classes should keep as much of their state
        as possible in their non-python datastore. This way
        the system can work even after shutdowns, and the
        state of the system can be managed or observed from
        other processes.

        In order to set up a datastore, init should check to see
        if one is already set (using get_datastore_for_provider)
        and use that one if available, otherwise make a new one
        and register it with the database.
        """
        existing_datastore = db.get_datastore_for_provider(PROVIDER_TYPE)
        if existing_datastore is not None:
            self.datastore = existing_datastore
        else:
            self.datastore_root = db.get_db_path_for_provider(PROVIDER_TYPE)
            self.datastore = self.initialize_provider_datastore(self.datastore_root)
            db.set_datastore_for_provider(PROVIDER_TYPE, self.datastore)

    @abstractmethod
    def get_default_db_location(self) -> str:
        """
        Return the folder root we expect the datastore for this
        crowdprovider to be set up in.
        """
        raise NotImplementedError()

    @abstractmethod
    def initialize_provider_datastore(self, storage_path: Optional[str] = None) -> Any:
        """
        Do whatever is required to initialize this provider insofar
        as setting up local or external state is required to ensure
        that this vendor is usable.

        Local data storage should be put into the given root path.

        This method should return the local data storage component that
        is required to do any object initialization, as it will be available
        from the MephistoDB in a db.get_provider_datastore(PROVIDER_TYPE).
        """
        raise NotImplementedError()

    @abstractmethod
    def setup_resources_for_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        """
        Setup any required resources for managing any additional resources
        surrounding a specific task run.
        """
        raise NotImplementedError()

    @abstractmethod
    def cleanup_resources_from_task_run(
        self, task_run: "TaskRun", server_url: str
    ) -> None:
        """
        Destroy any resources set up specifically for this task run
        """
        raise NotImplementedError()
