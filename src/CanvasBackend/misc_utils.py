from datetime import datetime as dt

def str2datetime(x):
    if x is None:
        return None
    return dt.strptime(x, '%Y-%m-%dT%H:%M:%SZ')