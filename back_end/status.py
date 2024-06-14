# back_end/status.py

import time
from functools import wraps

class APIStatus:
    _is_running = True

    @property
    def is_running(self):
        return self._is_running

    def set(self, status: bool):
        self._is_running = status


api_status = APIStatus()


# decorator timer
def timer(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        str_timer = time.time()
        resp = func(*args, **kwargs)
        end_timer = time.time()

        spend_timer = '%.2fs' % (end_timer - str_timer)
        print(f'func: {func.__name__}(), spend time: {spend_timer}')
        return resp
    return wrap