from abc import ABC, abstractmethod

class ModelObserverAbstract(ABC):
    @abstractmethod
    def update(self):
        pass

