# OWNER FINAL, 2026-09-28

| Rung                                   | Label                                                              |
| -------------------------------------- | ------------------------------------------------------------------ |
| 1: all 2^n moments, exact              | Exact reference and oracle diagnostic                              |
| 2: order <= L, exact                   | Approximation                                                      |
| 3: random subset, same count as rung 2 | Approximation (control for rung 2: does choosing by order matter?) |
| 4: tensor-network estimate             | Approximation                                                      |
| 5: Pauli-propagation estimate          | Approximation                                                      |

Owner reasoning: if rung 2 beats rung 3, the model's learned information lives in
low-order moments (equivalently, low-order marginals, as in the sibling project).
