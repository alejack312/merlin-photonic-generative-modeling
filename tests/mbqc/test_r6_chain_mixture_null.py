"""R6 richer causal-chain fixture; empirical symmetries are not a theorem."""
from __future__ import annotations

import numpy as np
import pytest

from merlin_iqp.mbqc import compile_m1, iqp_distribution_exact
from test_r6_mixture_null import _bits, _bits_to_index, _validate_policy_dependencies

G = np.array([[1, 0, 0], [1, 1, 0], [1, 1, 1]], dtype=np.uint8)
BASE = np.array([0.13, 0.27, 0.41])
TOLERANCE = 1e-9


def angles(rule: str, s: np.ndarray, constant: bool = False) -> np.ndarray:
    theta = BASE.copy()
    if not constant:
        if s[0]:
            theta[1] = -BASE[1] if rule == "sign" else BASE[1] + (
                np.pi if rule == "pi" else np.pi / 2
            )
        theta[2] += 0.19 * int(s[0]) - 0.23 * int(s[1])
    return theta


def table(g: np.ndarray, theta: np.ndarray) -> np.ndarray:
    return iqp_distribution_exact(compile_m1(g, theta))


def joint(rule: str, constant: bool = False) -> np.ndarray:
    """Independent graph-state projection, with causal bases selected per branch."""
    bits = _bits(3)
    result = np.zeros((8, 8))
    for si, s in enumerate(bits):
        theta = angles(rule, s, constant)
        bra = np.array([(np.cos(t), -1j * np.sin(t)) if outcome == 0
                        else (np.sin(t), 1j * np.cos(t))
                        for t, outcome in zip(theta, s, strict=True)])
        for yi, y in enumerate(bits):
            amplitude = 0j
            for a in bits:
                factor = np.prod(bra[np.arange(3), a])
                for z in bits:
                    parity = int((a @ ((G @ z) % 2) + z @ y) % 2)
                    amplitude += 2 ** (-4.5) * factor * (-1) ** parity
            result[si, yi] = abs(amplitude) ** 2
    return result


def corrected(prob: np.ndarray, xor: np.ndarray) -> np.ndarray:
    result = np.zeros(8)
    for si, s in enumerate(_bits(3)):
        for yi, y in enumerate(_bits(3)):
            result[_bits_to_index(y ^ ((xor @ s) % 2))] += prob[si, yi]
    return result


@pytest.mark.parametrize("rule", ["sign", "pi", "half_pi"])
def test_chain_branch_identity_mixture_uniform_mass(rule: str) -> None:
    _validate_policy_dependencies([(), (0,), (0, 1)])
    prob = joint(rule)
    tables = np.array([table(G, angles(rule, s)) for s in _bits(3)])
    predicted = np.array([[tables[si, _bits_to_index(y ^ ((G.T @ s) % 2))] / 8
                           for y in _bits(3)] for si, s in enumerate(_bits(3))])
    gaps = {"joint": float(np.max(abs(prob - predicted))),
            "mixture": float(np.max(abs(corrected(prob, G.T) - tables.mean(axis=0)))),
            "weights": float(np.max(abs(prob.sum(axis=1) - 1 / 8))),
            "mass": float(abs(prob.sum() - 1))}
    print(rule, gaps)
    np.testing.assert_allclose(prob, predicted, atol=TOLERANCE, rtol=0)
    np.testing.assert_allclose(corrected(prob, G.T), tables.mean(axis=0), atol=TOLERANCE, rtol=0)
    np.testing.assert_allclose(prob.sum(axis=1), np.full(8, 1 / 8), atol=TOLERANCE, rtol=0)
    assert gaps["mass"] <= TOLERANCE
    mixture = corrected(prob, G.T)
    distances = np.max(abs(tables - mixture), axis=1)
    print(rule, "mixture-to-each-branch gaps", distances.tolist())
    assert np.min(distances) > 1e-3


def test_chain_equal_angles_collapse() -> None:
    actual, expected = corrected(joint("sign", True), G.T), table(G, BASE)
    print("equal-angle collapse gap", float(np.max(abs(actual - expected))))
    np.testing.assert_allclose(actual, expected, atol=TOLERANCE, rtol=0)


@pytest.mark.parametrize("rule,identical", [("sign", True), ("pi", True), ("half_pi", False)],
                         ids=["sign_identical_vacuous", "pi_identical_vacuous", "half_pi_distinct"])
def test_second_angle_rule_non_vacuity(rule: str, identical: bool) -> None:
    theta = BASE.copy()
    theta[1] = angles(rule, np.array([1, 0, 0], dtype=np.uint8))[1]
    a, b = table(G, BASE), table(G, theta)
    gap = float(np.max(abs(a - b)))
    print(rule, "isolated second-generator table gap", gap)
    assert (gap <= TOLERANCE) if identical else (gap > 1e-3)


@pytest.mark.parametrize("corruption", ["drop_xor", "reverse_bits", "wrong_weights"])
def test_chain_adversarial_controls(corruption: str) -> None:
    prob = joint("half_pi")
    tables = np.array([table(G, angles("half_pi", s)) for s in _bits(3)])
    expected = tables.mean(axis=0)
    if corruption == "wrong_weights":
        weights = np.array([0.15] * 4 + [0.10] * 4)
        actual = weights @ tables
    else:
        actual = corrected(prob, np.zeros_like(G.T) if corruption == "drop_xor" else G.T[::-1])
    print(corruption, "gap", float(np.max(abs(actual - expected))))
    with pytest.raises(AssertionError):
        np.testing.assert_allclose(actual, expected, atol=TOLERANCE, rtol=0)


@pytest.mark.parametrize("dependencies", [[(), (1,), (0, 1)], [(), (2,), (0, 1)], [(), (0,), (2,)]])
def test_chain_rejects_self_or_future(dependencies: list[tuple[int, ...]]) -> None:
    with pytest.raises(ValueError):
        _validate_policy_dependencies(dependencies)


def test_empirical_random_angle_symmetries_report_only() -> None:
    rng = np.random.default_rng(20260930)
    maxima = {"sign": 0.0, "pi": 0.0}
    for _ in range(100):
        while True:
            g = rng.integers(0, 2, size=(3, 3), dtype=np.uint8)
            if np.all(g.sum(axis=1) > 0) and not np.array_equal(g, g.T):
                break
        theta = rng.uniform(-np.pi, np.pi, 3)
        j = int(rng.integers(3))
        original = table(g, theta)
        for rule in maxima:
            changed = theta.copy()
            changed[j] = -theta[j] if rule == "sign" else theta[j] + np.pi
            maxima[rule] = max(maxima[rule], float(np.max(abs(original - table(g, changed)))))
    print("empirical, random sample of N=100 cases", maxima)
