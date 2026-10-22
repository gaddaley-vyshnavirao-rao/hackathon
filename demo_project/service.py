from core import run
import subprocess

def process(value):
    return subprocess.run(value, shell=True)
