from threading import Thread

class Worker(Thread):

    def __init__(self, function, requester, data, callback):
        self.function = function
        self.requester = requester
        self.data = data
        self.callback = callback
        Thread.__init__(self)

    def run(self):
        self.function(self.requester, self.data, self.callback)