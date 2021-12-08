import enum

from tkinterTest import openGUI


class CustStatus(enum.Enum):
    IN_QUEUE = 0
    BEING_SERVCED = 1
    DONE = 2


openGUI(simTime=0, numCustomers=0, numServers=0, status=CustStatus.IN_QUEUE)
