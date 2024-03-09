from enum import Enum, auto


class ConnectionType(Enum):
    """
    Different handling procedures on how to communicate with our Database.
    """

    """
    The database relies on a local "drinks.db" file. If one does not exist, it will create one.
    """
    LOCAL_FILE = auto()

    """
    The database will be destroyed after the process stops.
    """
    LOCAL_MEMORY = auto()

    """
    The database relies on a remote url specified by the REMOTE_* config variables.
    """
    REMOTE_SERVER = auto()
