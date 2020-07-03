class GitHubApiError(Exception):
    def __init__(self, message="", status=0):
        super().__init__(message)
        self.status = status
