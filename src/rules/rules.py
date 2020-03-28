import networkx as nx
from pathlib import Path

def verify_rules(nodes, containers, source=None):
    """Validate configuration of nodes.

    :type graph: nx.DiGraph
    :returns: True if configuration is correct, otherwise dict representing the error and rule.
    """
    errors = []

    if source == 'Alteryx':
        for n in nodes.items():
            if n[1].get('settings') is not None:
                path = Path(n[1].get('Macro', ''))
                if path.is_absolute():
                    errors.append({
                            'rule':'All macros need to have a relative file path.',
                            'location': f'#{n[0]}',
                            'message': f'Macro path is: {path}',
                            'error_level': 'ERROR'})


        for n in nodes.items():
            if n[1].get('container') is None:

                is_in_text_box = False
                for (id, container_node) in containers.items():
                    container_left = container_node.get('position').get('x')
                    container_top = container_node.get('position').get('y')
                    container_right = container_left + container_node.get('size').get('width')
                    container_bottom = container_top + container_node.get('size').get('height')
                    x = n[1].get('position').get('x')
                    y = n[1].get('position').get('y')
                    if x >= container_left and (x+60) <= container_right and (y+60) <= container_bottom and y >= container_top:
                        is_in_text_box = True

                if is_in_text_box is False:
                    errors.append({
                        'rule': 'All tools need to be in a container.',
                        'location': f'#{n[0]}',
                        'message': '',
                        'error_level': 'ERROR'})

    elif source == 'Knime':
        for n in nodes.items():
            if n[1].get('is_metanode'):
                if n[1].get('settings') is not None:
                    if n[1].get('settings').get('workflow_template_information') is None:
                        errors.append({
                            'rule': 'Metanodes must be saved as templates.',
                            'location': f'#{n[0]} - {n[1]["type"]}',
                            'message': 'No template information in metanode.',
                            'error_level': 'ERROR'
                        })

    else:
        raise Exception('Source software unknown.')

    if len(errors) == 0:
        return True
    else:
        return errors

