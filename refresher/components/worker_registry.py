from utils.work_distributer.requester import RefreshRequester

def get_plugins(*args, **kwargs):
    r = RefreshRequester('worker_registry')
    return r.block_request({"action": "get_plugins"})


def delete_plugin(plugin_name, *args, **kwargs):
    r = RefreshRequester('worker_registry')
    return r.block_request({
        "action": "delete_plugin",
        "plugin_name": plugin_name
    })

ACTIONS = {
    "get_plugins": get_plugins,
    "delete_plugin": delete_plugin
}
