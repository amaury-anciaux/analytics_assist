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

        for n in nodes.items():
            if n[1].get('settings') is not None:
                if n[1].get('settings').get('Macro') is not None:
                    path = Path(n[1].get('settings').get('Macro'))
                    if path.is_absolute():
                        errors.append({
                                'location': f'#{n[0]} - {n[1]["type"]}',
                                'message': f'Macro path should be relative and is absolute: {path}',
                                })


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
                        'location': f'#{n[0]} - {n[1]["type"]}',
                        'message': 'Tool is outside of a container or text box.',
                        })


        return errors
