import os

class Settings:
    def __init__(self):
        self.BASE_DIR = os.getenv("CHECKTOOL_BASE_DIR", "/workspace")

settings = Settings()
