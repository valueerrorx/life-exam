'''
Small Class to measure execution time
Usage:
with timeit():
    # your code, e.g.,
    print(sum(range(int(1e7))))
'''


class time_it():
    from datetime import datetime

    def __enter__(self):
        self.tic = self.datetime.now()

    def __exit__(self, *args, **kwargs):
        print('runtime: {}'.format(self.datetime.now() - self.tic))
