import subprocess
import shutil


def test():
    subprocess.call('pytest -v', shell=True)
    shutil.rmtree('.pytest_cache', ignore_errors=True)


def dist():
    subprocess.call('python setup.py sdist upload', shell=True)
    shutil.rmtree('dist', ignore_errors=True)
