from importlib import import_module
import subprocess
import traceback

def install_plugin(plugin_repository):
    repo_link = 'git+' + plugin_repository
    try:
        exit_status = subprocess.check_call(['pip',
                                             'install',
                                             '--upgrade',
                                             repo_link])
    except Exception:
        return False
    return exit_status == 0


def get_plugin(plugin_module):
    try:
        plugin = import_module(plugin_module)
        plugin = plugin.REFRESHER_PLUGIN
    except ImportError as e:
        traceback.print_exc()
        raise Exception("Plugin {} is not installed".format(plugin_module))
    return plugin()


def get_action_from_plugin(plugin_module, action):
    plugin = get_plugin(plugin_module)
    return plugin.ACTIONS.get(action)
