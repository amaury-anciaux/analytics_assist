from src.rules.base_rules import BaseRules

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
            if n[1].get('is_metanode'):
                if n[1].get('settings') is not None:
                    if n[1].get('settings').get('workflow_template_information') is None:
                        errors.append({
                            'rule': 'Metanodes must be saved as templates.',
                            'location': f'#{n[0]} - {n[1]["type"]}',
                            'message': 'No template information in metanode.',
                            'error_level': 'ERROR'
                        })

        return errors