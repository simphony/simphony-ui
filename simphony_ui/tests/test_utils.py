from contextlib import contextmanager
import shutil
import logging


@contextmanager
def cleanup_garbage(tmpdir):
    try:
        yield
    except:
        try:
            print "Things went bad. Cleaning up ", tmpdir
            shutil.rmtree(tmpdir)
        except OSError:
            logging.exception("could not delete the tmp directory")
        raise
