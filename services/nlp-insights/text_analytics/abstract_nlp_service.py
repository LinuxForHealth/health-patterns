from abc import ABC, abstractmethod


class NLPService(ABC):

    @abstractmethod
    def process(self, text):
        return None

