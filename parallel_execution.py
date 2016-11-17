"""
Run various simulations in parallel.
"""
import multiprocessing
import subprocess
import sys


def run_moran(N):
    subprocess.call(["python", "moran.py", str(N)])
    return True


def main(max_N):
    """
    Create a pool of moran processes and run them in parallel
    """
    cores = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cores)
    return p.map(run_moran, range(2, max_N + 1))

if __name__ == '__main__':
    try:
        max_N = int(sys.argv[1])
    except IndexError:
        max_N = 12
    print(main(max_N))
