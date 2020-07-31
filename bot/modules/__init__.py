import glob
from os.path import basename, dirname, isfile


def get_modules():
    path = glob.glob(dirname(__file__) + "/*.py")

    modules = [
        basename(f)[:-3]
        for f in path
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]

    return modules


__all__ = get_modules()
ALL_MODULES = get_modules()
