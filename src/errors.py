import os.path


class Error:
    def __init__(self, logger):
        self.logger = logger

    def lockfile_error(self, path):
        if os.path.exists(path):
            return False
        else:
            self.logger.error("Lockfile does not exist, VALORANT is not open")
