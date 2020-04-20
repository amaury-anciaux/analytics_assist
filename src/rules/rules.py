import networkx as nx
from src.rules.alteryx import Rules as AlteryxRules
from src.rules.knime import Rules as KnimeRules
from src.configuration import read_configuration


config = read_configuration()

if config.get('source') == 'Alteryx':
    rules = AlteryxRules()
elif config.get('source') == 'Knime':
    rules = KnimeRules()
else:
    raise Exception('Source software unknown.')


def get_error_fields():
    return rules.get_error_fields()

def verify_rules(nodes, containers):
    """Validate configuration of nodes.

    :type graph: nx.DiGraph
    :returns: True if configuration is correct, otherwise dict representing the error and rule.
    """

    return rules.verify_rules(nodes, containers)
