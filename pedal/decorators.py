from _thread import allocate_lock as Lock

LOCK = Lock()

# defining a decorator
def threadsafe(func):
    global LOCK
    def wrap(*args, **kwargs):
        LOCK.acquire()
        result = func(*args, **kwargs)
        LOCK.release()
        return result

    return wrap