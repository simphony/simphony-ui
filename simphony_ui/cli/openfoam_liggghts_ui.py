import logging
from ..ui import Application


def main():
    """Instantiate and start the application"""
    logging.basicConfig()
    ui = Application()
    ui.configure_traits()
