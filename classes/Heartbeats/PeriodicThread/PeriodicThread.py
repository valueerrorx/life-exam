import logging
import threading


class PeriodicThread(object):
    """ Python periodic Thread using Timer """
    # original by https://gist.github.com/cypreess/5481681

    def __init__(self, callback=None, period=1, name=None, *args, **kwargs):
        """
        :param callback: Callback function
        :param period: delay in seconds
        """
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.period = period
        self.stop = False
        self.pause_ = False
        self.current_timer = None
        self.schedule_lock = threading.Lock()

    def start(self):
        """ Thread standard start method """
        self.schedule_timer()

    def run(self):
        """ By default run callback """
        if self.callback is not None:
            self.callback(*self.args, **self.kwargs)

    def _run(self):
        """ Run desired callback and then reschedule Timer (if thread is not stopped) """
        try:
            if self.pause_ is False:
                self.run()
        except Exception as ex:
            logging.exception("Exception in running periodic thread")
            logging.exception(ex)
        finally:
            with self.schedule_lock:
                if not self.stop:
                    self.schedule_timer()

    def schedule_timer(self):
        """ Schedules next Timer run """
        self.current_timer = threading.Timer(self.period, self._run, *self.args, **self.kwargs)
        if self.name:
            self.current_timer.name = self.name
        self.current_timer.start()

    def cancel(self):
        """ Timer standard cancel method """
        with self.schedule_lock:
            self.stop = True
            if self.current_timer is not None:
                self.current_timer.cancel()

    def join(self):
        """ Thread standard join method """
        self.current_timer.join()

    def pause(self):
        """ Pause executing Callback Function """
        self.pause_ = True

    def resume(self):
        """ executing Callback Function again """
        self.pause_ = False
