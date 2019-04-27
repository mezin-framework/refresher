import traceback
import json
from redis import Redis
from refresher.worker.handler import Handler
from refresher.services import plugin_service

class RefreshWorker(object):
    ''' Responsible for using a Academic Parser
        to fetch information from the portal
        and communicate to API.
     '''

    def __init__(self):
        self.refresh_queue = RefreshQueue()

    def run(self):
        while True:
            try:
                data = self.refresh_queue.get_new_payload()
                self.working = True
                action = data.get('action')
                if action == 'install_plugin':
                    plugin_service.install_plugin(data.get('plugin_repo'))
                    self.refresh_queue.respond({'status': 'success'})
                else:
                    plugin = data.get('plugin')
                    action = plugin_service.get_action_from_plugin(plugin, action)
                    queue = RefreshQueue(work_id=self.refresh_queue.work_id)
                    self.refresh_queue.clear()
                    Handler(action, data, queue).start()
            except:
                traceback.print_exc()
                self.refresh_queue.respond({"status": "internal_error"})
                continue

class RefreshQueue(object):
    ''' Responsible for encapsulating Queue behaviour,
        such as getting a new payload.
    '''

    QUEUE = 'refresher_queue'

    def __init__(self, work_id=''):
        self.redis = Redis(host='redis')
        self.work_id = work_id

    def get_new_payload(self):
        key, value = self.redis.brpop(self.QUEUE)
        data = json.loads(value.decode())
        self.work_id = data.get('work_id')
        self.redis.lpush(self.work_id, json.dumps({"status": "processing"}))
        return data

    def respond(self, data):
        if self.work_id:
            self.redis.lpush(self.work_id, json.dumps(data))
            self.clear()

    def clear(self):
        self.work_id = ''
