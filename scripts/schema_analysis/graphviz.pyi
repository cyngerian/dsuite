from typing import Any, Optional

class Digraph:
    def __init__(
        self,
        name: Optional[str] = None,
        comment: Optional[str] = None,
        filename: Optional[str] = None,
        directory: Optional[str] = None,
        format: Optional[str] = None,
        engine: Optional[str] = None,
        encoding: Optional[str] = None,
        graph_attr: Optional[dict[str, str]] = None,
        node_attr: Optional[dict[str, str]] = None,
        edge_attr: Optional[dict[str, str]] = None,
        body: Optional[list[str]] = None,
        strict: Optional[bool] = None,
    ) -> None: ...
    def attr(self, kw: Optional[str] = None, **attrs: Any) -> None: ...
    def node(self, name: str, label: Optional[str] = None, **attrs: Any) -> None: ...
    def edge(self, tail_name: str, head_name: str, **attrs: Any) -> None: ...
    def render(
        self,
        filename: Optional[str] = None,
        directory: Optional[str] = None,
        view: bool = False,
        cleanup: bool = False,
        format: Optional[str] = None,
    ) -> str: ...
