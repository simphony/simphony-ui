from ..ui import Application
import logging


def main():
    """Instantiate and start the application"""
    logging.basicConfig()
    ui = Application()
    ui.configure_traits()
