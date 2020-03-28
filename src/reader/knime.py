import xml.etree.cElementTree as ET
from pathlib import Path
from src.reader.common import elementtree_to_dict
xmlns = "{http://www.knime.org/2008/09/XMLConfig}"

class Reader:
    def __init__(self):
        pass

    @staticmethod
    def read_nodes(document_xml):
        return document_xml.find(xmlns + "config[@key='nodes']").findall(xmlns + "config")

    #
    # def read_child_nodes(node_xml):
    #     try:
    #         return node_xml.find('ChildNodes').findall('Node')
    #     except AttributeError:
    #         return None
    from src.reader.common import elementtree_to_dict

    @staticmethod
    def read_node_id(node_xml):
        return node_xml.find(xmlns + "entry[@key='id']").get('value')

    @staticmethod
    def read_node_type(node_xml):
        if Reader.is_metanode(node_xml):
            node_type = node_xml.find(xmlns + "entry[@key='node_type']").get('value')
            if node_type == "MetaNode":
                raise Exception(f'Unknown metanode type: #{Reader.read_node_id(node_xml)}')
            elif node_type == "SubNode":
                return node_xml.find(xmlns + "entry[@key='name']").get('value')
            elif node_type == "TempNode":
                raise Exception(f'Unknown metanode type: #{Reader.read_node_id(node_xml)}')
            else:
                raise Exception(f'Unknown metanode type: #{Reader.read_node_id(node_xml)}')
        else:
            return node_xml.find(xmlns + "entry[@key='node-name']").get('value')

    @staticmethod
    def load_node_extra_settings(node_xml, workflow_path):
        # Extend node XML with settings.xml
        node_settings_file = node_xml.find(xmlns + "entry[@key='node_settings_file']").get('value')
        file_path = Path(workflow_path) / Path(node_settings_file)
        tree = ET.ElementTree(file=file_path)
        settings_root = tree.getroot()
        settings_root.extend(node_xml)
        if Reader.is_metanode(node_xml):
            node_type = node_xml.find(xmlns + "entry[@key='node_type']").get('value')
            if node_type == "MetaNode":
                raise Exception(f'Unknown metanode type: #{Reader.read_node_id(node_xml)}')
            elif node_type == "SubNode":
                # Extend node XML with workflow.knime of metanode
                workflow_path = file_path.parent
                workflow_xml_path = Path(workflow_path) / Path('workflow.knime')
                tree = ET.ElementTree(file=workflow_xml_path)
                root = tree.getroot()
                settings_root.extend(root)
            elif node_type == "TempNode":
                raise Exception(f'Unknown metanode type: #{Reader.read_node_id(node_xml)}')
            else:
                raise Exception(f'Unknown metanode type: #{Reader.read_node_id(node_xml)}')
        return settings_root

    @staticmethod
    def read_node_position(node_xml):
        return {'x': float(node_xml.find(xmlns + "config[@key='ui_settings']").find(xmlns + "config[@key='extrainfo.node.bounds']").find(xmlns + "entry[@key='0']").get('value')),
                'y': float(node_xml.find(xmlns + "config[@key='ui_settings']").find(xmlns + "config[@key='extrainfo.node.bounds']").find(xmlns + "entry[@key='1']").get('value')),
                }

    @staticmethod
    def read_node_size(node_xml):
        w = node_xml.find(xmlns + "config[@key='ui_settings']").find(xmlns + "config[@key='extrainfo.node.bounds']").find(xmlns + "entry[@key='2']").get('value')
        h = node_xml.find(xmlns + "config[@key='ui_settings']").find(xmlns + "config[@key='extrainfo.node.bounds']").find(xmlns + "entry[@key='3']").get('value')
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
        return elementtree_to_dict(node_xml.find(xmlns + "config[@key='model']"))

    # def is_node_documentation(node_xml):
    #     return node_xml.find('GuiSettings').get('Plugin') == 'AlteryxGuiToolkit.TextBox.TextBox'
    #
    @staticmethod
    def ignore_node(node_xml):
        return False

    @staticmethod
    def is_metanode(node_xml):
        return node_xml.find(xmlns + "entry[@key='node_is_meta']").get('value') == 'true'

    @staticmethod
    def read_node_settings(node_xml):
        """
        Return a dictionary structure of settings items
        :param node_xml:
        :return:
        """
        workflow_template_information = node_xml.find(xmlns + "config[@key='workflow_template_information']")
        if workflow_template_information is not None:
            workflow_template_information = elementtree_to_dict(workflow_template_information)
        return { 'workflow_template_information': workflow_template_information}


    #
    # def read_connections(document_xml):
    #     return document_xml.find('Connections').findall('Connection')
    #
    #
    # def read_connection(connection_xml):
    #     return {
    #         'from_node': connection_xml.find('Origin').get('ToolID'),
    #         'to_node': connection_xml.find('Destination').get('ToolID'),
    #         'from_port': connection_xml.find('Origin').get('Connection'),
    #         'to_port': connection_xml.find('Destination').get('Connection'),
    #     }
    #
    #
    @staticmethod
    def read_node_annotation(node_xml):
        annotation_xml = node_xml.find(xmlns + "entry[@key='nodeAnnotation']")
        if annotation_xml is not None:
            return annotation_xml.get('value')
        else:
            return ''
