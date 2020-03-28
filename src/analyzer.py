from src.reader.reader import WorkflowGraph
from src.rules.rules import verify_rules
from src.configuration import read_configuration
import logging
from win10toast import ToastNotifier

toaster = ToastNotifier()
logger = logging.getLogger(__name__)

def analyze_workflow(workflow_path):
    source = read_configuration().get('analyzer').get('source')
    logger.info(f'Analyzing workflow: {workflow_path}')
    graph = WorkflowGraph(workflow_path, '', source)
    graph.build()
    errors = verify_rules(graph.nodes, graph.containers, source)
    if errors != True:
        toaster.show_toast(errors[0]['rule'], errors[0]['message'], threaded=True)
    logger.info(f'Errors generated: {errors}')
    return errors