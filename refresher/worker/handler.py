import traceback
from threading import Thread
from time import time

class Handler(Thread):

    def __init__(self, action, data, queue):
        self.action = action
        self.queue = queue
        self.data = data
        Thread.__init__(self)
    
    def run(self):
        current_milli_time = lambda: int(round(time() * 1000))
        initial_time = current_milli_time()
        try:
            fetched_data = self.action(**self.data)
            if not fetched_data.get('status'):
                fetched_data['status'] = 'success'
            self.queue.respond(fetched_data)
        except:
            traceback.print_exc()
            self.queue.respond({"status": "internal_error"})
        final_time = current_milli_time()
        print 'Total time: {}'.format(final_time - initial_time)