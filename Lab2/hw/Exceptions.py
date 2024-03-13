class StatusCodeException(Exception):
    def __init__(self, message, response, code):
        super().__init__(message)
        self.response = response
        self.code = code
