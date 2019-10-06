from utils.work_distributer.requester import RefreshRequester

def get_plugins(*args, **kwargs):
    r = RefreshRequester('worker_registry')
    return r.block_request({"action": "get_plugins"})

ACTIONS = {
    "get_plugins": get_plugins
}