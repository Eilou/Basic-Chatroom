class CustomExitException(Exception):
    def __init__(self, message="Key Empty") -> None:
        super(CustomExitException, self).__init__(message)
