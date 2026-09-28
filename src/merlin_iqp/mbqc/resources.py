"""Logical-only M1 graph resource accounting."""

from __future__ import annotations

from typing import Any

from .pattern import M1Pattern


def resource_report(pattern: M1Pattern) -> dict[str, Any]:
    """Report graph size and fixed-basis logical resource fields."""

    return {
        "logical_qubits": pattern.n,
        "ancilla_qubits": pattern.m,
        "graph_qubits": pattern.n + pattern.m,
        "edges": pattern.edge_count,
        "fixed_bases": {
            "data": "X",
            "ancilla": [f"b(theta_{j})" for j in range(pattern.m)],
        },
        "ideal_feed_forward_rounds": 0,
        "status": "logical-only",
        "physical_graph_preparation_validated": False,
    }
