from datetime import datetime

def str2datetime(x):
    if x is None:
        return None
    return datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')