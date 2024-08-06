class MalformedCommandException(Exception):
    def __init__(self, message="Malformed command, arguments are separated using a forward slash (/)") -> None:
        super(MalformedCommandException, self).__init__(message)
        self.message = "Malformed command, arguments are separated using a forward slash (/)"
