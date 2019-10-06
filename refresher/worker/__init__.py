import traceback
import json
import random
from redis import Redis
from threading import Thread
from refresher import components
from refresher.worker.handler import Handler
from utils.services import plugin_service
from utils.work_distributer.requester import RefreshRequester

class RefreshWorker(object):
    ''' Responsible for using a Academic Parser
        to fetch information from the portal
        and communicate to API.
     '''

    def __init__(self):
        self.refresh_queue = RefreshQueue()
        self.registry_requester = RefreshRequester('worker_registry')
        self.check_install_plugins()

    def check_install_plugins(self):
        plugins = self.registry_requester.block_request({"action": "get_plugins"})
        plugins = plugins.get('data')
        for p in plugins:
            try:
                plugin_service.get_refresher_plugin(p.get('plugin_name'))
            except:
                try:
                    plugin_service.install_plugin(p.get('plugin_repo'))
                except:
                    traceback.print_exc()

    def run(self):
        while True:
            try:
                data = self.refresh_queue.get_new_payload()
                action = data.get('action')
                if action == 'install_plugin':
                    plugin_repo = data.get('plugin_repo')
                    plugin_service.install_plugin(plugin_repo)
                    self.registry_requester.block_request(data)
                    self.refresh_queue.respond({"status": "success"})
                else:
                    plugin = data.get('plugin')
                    if plugin in components.COMPONENTS:
                        action = components.get_action_from_component(plugin, action)
                    else:
                        action = plugin_service.get_refresher_action_from_plugin(plugin, action)
                    print plugin, data.get('action')
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
