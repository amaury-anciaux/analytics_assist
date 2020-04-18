from src.rules.base_rules import BaseRules
from pathlib import Path

class Rules(BaseRules):
    def get_error_fields(self):
        return [
            ('location', 'Location'),
            ('message', 'Message'),
                ]

    def verify_rules(self, nodes, containers):
        """Validate configuration of nodes.

        :type graph: nx.DiGraph
        :returns: True if configuration is correct, otherwise dict representing the error and rule.
        """
        errors = []

        # Macro paths should all be relative
        for (id, node) in nodes.items():
            if node.get('settings') is not None:
                if node.get('settings').get('Macro') is not None:
                    path = Path(node.get('settings').get('Macro'))
                    if path.is_absolute():
                        errors.append({
                                'location': f'#{id} - {node["type"]}',
                                'message': f'Macro path should be relative and is absolute: {path}',
                                })

        # All nodes should be either inside a container tool or located in a text box
        for (id, node) in nodes.items():
            if node.get('container') is None:
                is_in_text_box = False
                for (container_id, container_node) in containers.items():
                    container_left = container_node.get('position').get('x')
                    container_top = container_node.get('position').get('y')
                    container_right = container_left + container_node.get('size').get('width')
                    container_bottom = container_top + container_node.get('size').get('height')
                    x = node.get('position').get('x')
                    y = node.get('position').get('y')
                    if x >= container_left and (x+60) <= container_right and (y+60) <= container_bottom and y >= container_top:
                        is_in_text_box = True

                if is_in_text_box is False:
                    errors.append({
                        'location': f'#{id} - {node["type"]}',
                        'message': 'Tool is outside of a container or text box.',
                        })

        # Joins cannot use "by record position"
        for (id, node) in nodes.items():
            if node.get('configuration').get('joinByRecordPos') == 'True':
                errors.append({
                    'location': f'#{id} - {node["type"]}',
                    'message': 'Join uses "By Record Position" option which is unsafe.',
                })

        # There should be no nodes with an unknown type
        for (id, node) in nodes.items():
            if node.get('type') == 'Unknown':
                errors.append({
                    'location': f'#{id} - {node["type"]}',
                    'message': 'Node type is unknown, probably a macro that is not found.',
                })

        # All files used for input should have a relative path
        for (id, node) in nodes.items():
            if node.get('type') == 'DbFileInput':
                file_path = Path(node.get('configuration').get('File').get('text'))
                if file_path.is_absolute():
                    errors.append({
                        'location': f'#{id} - {node["type"]}',
                        'message': f'File path should be relative but is absolute: {file_path}',
                    })

        # All containers should be enabled
        for (id, node) in containers.items():
            if node.get('type') == 'ToolContainer':
                if node.get('configuration').get('Disabled').get('value') == 'True':
                    errors.append({
                        'location': f'#{id} - {node["type"]}',
                        'message': f'Container is disabled.',
                    })

        return errors
