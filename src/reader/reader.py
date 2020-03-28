import xml.etree.cElementTree as ET
import logging
import networkx as nx
import os


logger = logging.getLogger(__name__)
from src.reader.alteryx import Reader as AlteryxReader
from src.reader.knime import Reader as KnimeReader


class WorkflowGraph(object):
    def __init__(self, workflow_path, macro_root, source=None):
        self.logger = logging.getLogger(__name__)
        self.source=source
        self.workflow_path = workflow_path
        if macro_root is None:
            self.macro_root = []
        else:
            self.macro_root = macro_root
        self.containers = {}
        self.nodes = {}
        self.containers ={}
        self.connections = []
        if self.source == 'Alteryx':
            self.reader = AlteryxReader()
        elif self.source == 'Knime':
            self.reader = KnimeReader()

    def build(self):

        self.logger.info(f'Reading file {self.workflow_path}')
        # We need this loop because Watchdog is firing the event as soon as the file's
        # modification is detected, and it may not have been fully written when we get
        # here.

        tree=None
        while tree is None:
            try:
                if self.source == 'Knime':
                    tree = ET.ElementTree(file=os.path.join(self.workflow_path, 'workflow.knime'))
                else:
                    tree = ET.ElementTree(file=self.workflow_path)
            except ET.ParseError:
                continue
        self.logger.debug(f'File reading finished: {self.workflow_path}')
        root = tree.getroot()
        if self.source == 'Knime':
            self.xmlns = "{http://www.knime.org/2008/09/XMLConfig}"

            self.nodes, self.containers = self.build_knime_nodes(self.reader.read_nodes(root))

        else:
            self.nodes, self.containers = self.build_nodes(self.reader.read_nodes(root))
            self.connections = self.build_connections(root, self.nodes)
            self.graph = self.build_graph(self.nodes, self.connections)

        #knime_connections = self.build_knime_connections(root, knime_nodes)
        #graph = self.build_graph(knime_nodes, knime_connections)
        #flow_vars = self.get_global_vars()
        flow_vars = {}

        # self.logger.info("## BUILD - END - " + self.knime_workflow_path + " ##")
        #return graph, flow_vars


    def build_knime_nodes(self, xml_nodes):
        nodes = {}
        containers = {}
        for xml_node in xml_nodes:
            id = self.reader.read_node_id(xml_node)
            settings_root = self.reader.load_node_extra_settings(xml_node, self.workflow_path)

            nodes[id] = self.build_node(settings_root)
        return nodes, containers



    def build_nodes(self, xml_nodes, flatten=True):
        nodes = {}
        containers = {}
        for n in xml_nodes:
            # For now, text nodes are stored in the containers dict. In reality they can also be
            # just text annotations.
            if not self.reader.ignore_node(n):
                node_id = self.reader.read_node_id(n)
                if self.reader.is_node_documentation(n):
                    containers[node_id] = self.build_node(n)
                else:
                    child_nodes = self.reader.read_child_nodes(n)
                    if child_nodes is not None:
                        nodes_dict, containers_dict = self.build_nodes(child_nodes)
                        if flatten:
                            # Flatten the container nodes: child nodes are added to the dict of nodes, and reference
                            # their container which is added to its own dict.
                            for node in nodes_dict.items():
                                node[1]['container'] = node_id
                            nodes.update(nodes_dict)
                            containers[node_id] = self.build_node(n)
                        else:
                            # Do not flatten: node dict contains another dict with child nodes.
                            nodes[node_id] = self.build_node(n)
                            nodes[node_id]['child_nodes'] = nodes_dict
                    else:
                        nodes[node_id] = self.build_node(n)
        return nodes, containers

    def build_node(self, node_xml):
        return {
            'type': self.reader.read_node_type(node_xml),
            'position': self.reader.read_node_position(node_xml),
            'size': self.reader.read_node_size(node_xml),
            'annotation': self.reader.read_node_annotation(node_xml),
            'configuration': self.reader.read_node_configuration(node_xml),
            'settings': self.reader.read_node_settings(node_xml),
            'is_metanode': self.reader.is_metanode(node_xml),
        }

    def build_connections(self, connection_xml, nodes):
        xml_connections = self.reader.read_connections(connection_xml)
        connections = []
        for n in xml_connections:
            c = self.reader.read_connection(n)
            if c['from_node'] not in nodes:
                logger.error(f'Error: connection references non-existing node: {c["from_node"]}')
                raise Exception
            if c['to_node'] not in nodes:
                logger.error(f'Error: connection references non-existing node: {c["to_node"]}')
                raise Exception

            connections.append(self.reader.read_connection(n))
        return connections

    def build_graph(self, nodes, connections):
        graph = nx.DiGraph()

        for (node_id, node) in nodes.items():
            graph.add_node(node_id, **node)
    #        if node.get(['child_nodes']):
    #            node['graph'] = build_graph(['child_nodes'],)

        for c in connections:
            # Note: ports are ignored for now
            graph.add_edge(c['from_node'], c['to_node'])
        return graph
