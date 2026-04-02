from __future__ import annotations
from abc import ABC, abstractmethod
from main_files.convert  import Invoice

class InvoiceParser(ABC):
    name: str

    @abstractmethod
    def can_parse(self, text: str) -> bool: ...

    @abstractmethod
    def parse(self, text: str, source_file: str) -> Invoice: ...
