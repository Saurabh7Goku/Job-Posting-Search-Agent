import logging
from threading import Lock
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

jobs_lock = Lock()
jobs: Dict[str, "Job"] = {}


@dataclass
class Event:
    timestamp: datetime
    data: str


@dataclass
class Job:
    status: str
    events: List[Event]
    result: str


def append_event(job_id: str, event_data: str):
    with jobs_lock:
        if job_id not in jobs:
            logging.info("Job %s started", job_id)
            jobs[job_id] = Job(
                status='STARTED',
                events=[],
                result='')
        else:
            logging.info("Appending event for job %s: %s", job_id, event_data)
        jobs[job_id].events.append(
            Event(timestamp=datetime.now(), data=event_data))