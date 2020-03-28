
class Reader:
    def __init__(self):
        pass

    @staticmethod
    def read_nodes(document_xml):
        return document_xml.find('Nodes').findall('Node')

    @staticmethod
    def read_child_nodes(node_xml):
        try:
            return node_xml.find('ChildNodes').findall('Node')
        except AttributeError:
            return None

    @staticmethod
    def read_node_id(node_xml):
        return node_xml.get('ToolID')

    @staticmethod
    def read_node_type(node_xml):
        return node_xml.find('GuiSettings').get('Plugin')

    @staticmethod
    def read_node_position(node_xml):
        return {'x': float(node_xml.find('GuiSettings/Position').get('x')), 'y': float(node_xml.find('GuiSettings/Position').get('y'))}

    @staticmethod
    def read_node_size(node_xml):
        w = node_xml.find('GuiSettings/Position').get('width')
        h = node_xml.find('GuiSettings/Position').get('height')
        if w is not None:
            w = float(w)
        if h is not None:
            h = float(h)

        return {'width': w, 'height': h}

    @staticmethod
    def read_node_configuration(node_xml):
        """
        Return a dictionary structure of configuration items
        :param node_xml:
        :return:
        """
        configuration = {}
        for i in node_xml.find('Properties/Configuration'):
            configuration[i.tag] = i.attrib
            configuration[i.tag]['text'] = i.text
        return configuration

    @staticmethod
    def is_node_documentation(node_xml):
        return node_xml.find('GuiSettings').get('Plugin') == 'AlteryxGuiToolkit.TextBox.TextBox'

    @staticmethod
    def ignore_node(node_xml):
        return node_xml.find('GuiSettings').get('Plugin') in \
               ['AlteryxGuiToolkit.Questions.Tab.Tab']

    @staticmethod
    def read_node_settings(node_xml):
        """
        Return a dictionary structure of settings items
        :param node_xml:
        :return:
        """
        try:
            return node_xml.find('EngineSettings').attrib
        except AttributeError:
            return None

    @staticmethod
    def is_metanode(node_xml):
        engine =  node_xml.find('EngineSettings')
        if engine is not None:
            return engine.get('Macro')
        else:
            return False

    @staticmethod
    def read_connections(document_xml):
        return document_xml.find('Connections').findall('Connection')

    @staticmethod
    def read_connection(connection_xml):
        return {
            'from_node': connection_xml.find('Origin').get('ToolID'),
            'to_node': connection_xml.find('Destination').get('ToolID'),
            'from_port': connection_xml.find('Origin').get('Connection'),
            'to_port': connection_xml.find('Destination').get('Connection'),
        }

    @staticmethod
    def read_node_annotation(node_xml):
        return node_xml.findtext('Properties/Annotation/AnnotationText', default=node_xml.findtext('Properties/Annotation/DefaultAnnotationText', default=''))
