from refresher.components import worker_registry

COMPONENTS = ['worker_registry', 'refresher', 'worker', 'api']


def get_action_from_component(component, action):
    return worker_registry.ACTIONS.get(action) # TODO: be compatible with other components
