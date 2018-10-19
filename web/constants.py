from enum import Enum
class Status(Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    SUCCESS="success"
    FAILED="failed"
    RETRYING = "retrying"
    NOTEXIST = "not exist"


MAX_RETRY = 2