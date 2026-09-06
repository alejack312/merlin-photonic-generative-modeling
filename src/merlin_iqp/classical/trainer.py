"""Deterministic exact classical trainer with portable resume."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

import numpy as np

from .checkpoint import checkpoint_generator, load_checkpoint, save_checkpoint
from .contracts import Checkpoint, KernelSpec
from .model import IQPModel
from .objectives import objective_and_gradient_exact
from ._validation import hash_json


class Trainer:
    def __init__(self, model: IQPModel, target: object, kernel: KernelSpec | str = "hamming_gaussian", *, sigma: float = 1.0, optimizer: str = "adam", lr: float = 0.05, seed: int = 0, source_commit: str | None = None) -> None:
        if not isinstance(model, IQPModel):
            raise TypeError("model must be an IQPModel")
        self.model = model
        self.target = target
        self.kernel = kernel if isinstance(kernel, KernelSpec) else KernelSpec(kind="hamming_gaussian" if kernel in {"gaussian", "hamming_gaussian"} else "spatial_gaussian", sigma=sigma, centers=np.zeros((2**model.n, 1)) if kernel == "spatial_gaussian" else None)
        self.optimizer = optimizer.lower()
        if self.optimizer not in {"sgd", "adam"}:
            raise ValueError("optimizer must be 'sgd' or 'adam'")
        if not np.isfinite(lr) or lr <= 0:
            raise ValueError("lr must be positive and finite")
        self.lr = float(lr)
        self.seed = int(seed)
        self.source_commit = source_commit
        self.step = 0
        self.loss_history: list[float] = []
        self._m = np.zeros_like(model.theta)
        self._v = np.zeros_like(model.theta)
        self._adam_t = 0
        self._rng = np.random.default_rng(self.seed)

    @property
    def spec_hash(self) -> str:
        return hash_json({"G": self.model.G.tolist(), "convention": self.model.provenance.get("convention_id", "iqp_z_msb_v1")})

    @property
    def dataset_hash(self) -> str:
        return str(getattr(self.target, "hash", hash_json(np.asarray(self.target).tolist())))

    def run(self, steps: int, *, checkpoint_path: str | Path | None = None) -> dict[str, Any]:
        if steps < 0:
            raise ValueError("steps must be non-negative")
        if not self.loss_history:
            initial, _ = objective_and_gradient_exact(self.model.theta, self.model.G, self.target, self.kernel)
            self.loss_history.append(float(initial))
        for _ in range(steps):
            loss, gradient = objective_and_gradient_exact(self.model.theta, self.model.G, self.target, self.kernel)
            self._apply(gradient)
            self.step += 1
            next_loss, _ = objective_and_gradient_exact(self.model.theta, self.model.G, self.target, self.kernel)
            self.loss_history.append(float(next_loss))
        if checkpoint_path is not None:
            save_checkpoint(self.checkpoint(), checkpoint_path, generator=self.model.G)
        return {"step": self.step, "theta": self.model.theta.copy(), "loss_history": tuple(self.loss_history), "final_loss": self.loss_history[-1]}

    fit = run

    def _apply(self, gradient: np.ndarray) -> None:
        if self.optimizer == "sgd":
            self.model.theta -= self.lr * gradient
            return
        self._adam_t += 1
        self._m = 0.9 * self._m + 0.1 * gradient
        self._v = 0.999 * self._v + 0.001 * gradient**2
        m_hat = self._m / (1 - 0.9**self._adam_t)
        v_hat = self._v / (1 - 0.999**self._adam_t)
        self.model.theta -= self.lr * m_hat / (np.sqrt(v_hat) + 1e-8)

    def checkpoint(self) -> Checkpoint:
        return Checkpoint(
            spec_hash=self.spec_hash,
            dataset_hash=self.dataset_hash,
            kernel_hash=self.kernel.hash,
            theta=self.model.theta.copy(),
            step=self.step,
            optimizer=self.optimizer,
            optimizer_state={"m": self._m.tolist(), "v": self._v.tolist(), "adam_t": self._adam_t, "lr": self.lr},
            rng_state=self._rng.bit_generator.state,
            dtype=str(self.model.theta.dtype),
            library_versions={"python": platform.python_version(), "numpy": np.__version__},
            source_commit=self.source_commit,
            loss_history=tuple(self.loss_history),
            checkpoint_selection_rule="fixed_last_step",
            metadata={"seed": self.seed},
        )

    def resume(self, path: str | Path) -> None:
        checkpoint = load_checkpoint(path, expected_spec_hash=self.spec_hash, expected_dataset_hash=self.dataset_hash, expected_kernel_hash=self.kernel.hash)
        if checkpoint.optimizer != self.optimizer or len(checkpoint.theta) != self.model.m:
            raise ValueError("checkpoint optimizer or theta shape is incompatible")
        saved_lr = checkpoint.optimizer_state.get("lr")
        if saved_lr is None or not np.isfinite(saved_lr) or saved_lr <= 0:
            raise ValueError("checkpoint is missing a valid optimizer learning rate")
        if not np.isclose(float(saved_lr), self.lr, rtol=0.0, atol=0.0):
            raise ValueError(
                "checkpoint learning rate mismatch: "
                f"checkpoint={float(saved_lr):.17g}, trainer={self.lr:.17g}"
            )
        self.model.theta = checkpoint.theta.copy()
        self.step = checkpoint.step
        self.loss_history = list(checkpoint.loss_history)
        state = checkpoint.optimizer_state
        self._m = np.asarray(state.get("m", np.zeros(self.model.m)), dtype=np.float64)
        self._v = np.asarray(state.get("v", np.zeros(self.model.m)), dtype=np.float64)
        self._adam_t = int(state.get("adam_t", 0))
        self._rng = np.random.default_rng()
        if checkpoint.rng_state:
            self._rng.bit_generator.state = checkpoint.rng_state

    @classmethod
    def from_checkpoint(cls, path: str | Path, target: object, kernel: KernelSpec | str = "hamming_gaussian", **kwargs: Any) -> "Trainer":
        checkpoint = load_checkpoint(path)
        model = IQPModel(checkpoint_generator(path), checkpoint.theta)
        requested_lr = kwargs.pop("lr", None)
        saved_lr = checkpoint.optimizer_state.get("lr")
        if saved_lr is None:
            if requested_lr is None:
                raise ValueError("checkpoint is missing a valid optimizer learning rate")
            initial_lr = float(requested_lr)
        else:
            initial_lr = float(saved_lr)
            if requested_lr is not None and not np.isclose(float(requested_lr), initial_lr, rtol=0.0, atol=0.0):
                raise ValueError(
                    "checkpoint learning rate mismatch: "
                    f"checkpoint={initial_lr:.17g}, trainer={float(requested_lr):.17g}"
                )
        trainer = cls(model, target, kernel, optimizer=checkpoint.optimizer, lr=initial_lr, **kwargs)
        trainer.resume(path)
        return trainer
