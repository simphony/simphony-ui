from ..ui import Application, logging


def main():
    """Instantiate and start the application"""
    logging.basicConfig()
    ui = Application()
    ui.configure_traits()
