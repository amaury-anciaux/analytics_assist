import logging
from src.reader.reader import WorkflowGraph
from src.rules.rules import verify_rules
from src.configuration import read_configuration


logger = logging.getLogger(__name__)

def analyze_workflow(workflow_path):
    source = read_configuration().get('source')
    logger.info(f'Analyzing workflow: {workflow_path}')
    graph = WorkflowGraph(workflow_path, '', source)
    graph.build()
    errors = verify_rules(graph.nodes, graph.containers)
    logger.info(f'Errors generated: {errors}')
    return errors