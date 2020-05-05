class NoTokenError(Exception):
    
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)


class GetContentError(Exception):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
