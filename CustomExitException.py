class CustomExitException(Exception):
    def __init__(self, message="Intentional exit") -> None:
        super(CustomExitException, self).__init__(message)
        
