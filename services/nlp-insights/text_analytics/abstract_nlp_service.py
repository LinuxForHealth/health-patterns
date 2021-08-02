from abc import ABC, abstractmethod


class NLPService(ABC):

    @abstractmethod
    def process(self, text):
        return None

    @staticmethod
    @abstractmethod
    def concept_to_dict(concept):
        return None

    @staticmethod
    @abstractmethod
    def symptom_to_dict(symptom):
        return None
