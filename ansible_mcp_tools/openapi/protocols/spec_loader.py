from typing import Dict
from typing import Protocol, runtime_checkable


@runtime_checkable
class SpecLoader(Protocol):

    def fetch(self) -> str: ...

    def load(self) -> Dict: ...
