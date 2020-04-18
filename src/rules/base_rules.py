from abc import ABC, abstractmethod

class BaseRules(ABC):
    @abstractmethod
    def get_error_fields(self):
        pass

    def verify_rules(self, nodes, containers):
        pass