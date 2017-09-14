# Basic Exception to handle not found companies
class CompanySnapshotNotFoundException(Exception):
    pass


# Basic Exception to raise when SAFER is down
class SAFERUnreachableException(Exception):
    pass
