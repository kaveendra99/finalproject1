class FileReadError(Exception):
    def __init__(self, message="INVALID MEDIA TYPE") -> None:
        self.message = message
        super().__init__(self.message)


class DetectionInitializationError(Exception):
    def __init__(self, message="DETECTION MODEL INITIALIZATION ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class DatabaseReadError(Exception):
    def __init__(self, message="DATABASE READ ERROR") -> None:
        self.message = message
        super().__init__(self.message)


class DetectionError(Exception):
    def __init__(self, message="DETECTION ERROR") -> None:
        self.message = message
        super().__init__(self.message)
