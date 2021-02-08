'''
Small Class to measure execution time
Usage:
with timeit():
    # your code, e.g.,
    print(sum(range(int(1e7))))
'''
from _datetime import datetime


class time_it():

    def __enter__(self):
        self.tic = datetime.now()

    def __exit__(self, *args, **kwargs):
        print('runtime: {}'.format(datetime.now() - self.tic))
