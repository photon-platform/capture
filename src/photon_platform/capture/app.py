"""
run the main app
"""
from .capture import Capture


def run() -> None:
    reply = Capture().run()
    print(reply)
