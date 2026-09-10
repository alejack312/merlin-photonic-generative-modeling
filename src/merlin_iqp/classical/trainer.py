"""Deterministic exact classical trainer with portable resume."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

import numpy as np

from .checkpoint import checkpoint_generator, load_checkpoint, save_checkpoint
from .contracts import Checkpoint, KernelSpec
from .model import IQPModel
from .objectives import objective_and_gradient_exact, objective_exact
from ._validation import hash_json


class Trainer:
    def __init__(self, model: IQPModel, target: object, kernel: KernelSpec | str = "hamming_gaussian", *, sigma: float = 1.0, centers: np.ndarray | None = None, optimizer: str = "adam", lr: float = 0.05, seed: int = 0, source_commit: str | None = None) -> None:
        if not isinstance(model, IQPModel):
            raise TypeError("model must be an IQPModel")
        self.model = model
        self.target = target
        if isinstance(kernel, KernelSpec):
            if centers is not None:
                raise ValueError("centers must be supplied by the KernelSpec when kernel is a KernelSpec")
            self.kernel = kernel
        elif kernel in {"gaussian", "hamming_gaussian"}:
            if centers is not None:
                raise ValueError("centers are only valid for the spatial_gaussian kernel")
            self.kernel = KernelSpec(kind="hamming_gaussian", sigma=sigma)
        elif kernel == "spatial_gaussian":
            self.kernel = KernelSpec(kind="spatial_gaussian", sigma=sigma, centers=centers)
        else:
            raise ValueError(f"unsupported kernel {kernel!r}")
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
            if not np.isfinite(initial):
                raise FloatingPointError("initial objective is not finite")
            self.loss_history.append(float(initial))
        for _ in range(steps):
            loss, gradient = objective_and_gradient_exact(self.model.theta, self.model.G, self.target, self.kernel)
            if not np.isfinite(loss) or not np.all(np.isfinite(gradient)):
                raise FloatingPointError("training objective or gradient is not finite")
            self._apply(gradient)
            self.step += 1
            next_loss = objective_exact(self.model.theta, self.model.G, self.target, self.kernel)
            if not np.isfinite(next_loss) or not np.all(np.isfinite(self.model.theta)):
                raise FloatingPointError("training trajectory is not finite")
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
        if checkpoint.step > 0 and not checkpoint.loss_history:
            raise ValueError("checkpoint with positive step must include complete loss history")
        if len(checkpoint.loss_history) not in {0, checkpoint.step + 1}:
            raise ValueError("checkpoint loss history length is inconsistent with checkpoint step")
        saved_lr = checkpoint.optimizer_state.get("lr")
        try:
            saved_lr_value = float(saved_lr)
        except (TypeError, ValueError):
            saved_lr_value = float("nan")
        if saved_lr is None or not np.isfinite(saved_lr_value) or saved_lr_value <= 0:
            raise ValueError("checkpoint is missing a valid optimizer learning rate")
        if not np.isclose(saved_lr_value, self.lr, rtol=0.0, atol=0.0):
            raise ValueError(
                "checkpoint learning rate mismatch: "
                f"checkpoint={saved_lr_value:.17g}, trainer={self.lr:.17g}"
            )
        state = checkpoint.optimizer_state
        if self.optimizer == "adam":
            missing = [key for key in ("m", "v", "adam_t") if key not in state]
            if missing:
                raise ValueError(f"checkpoint is missing Adam optimizer state: {', '.join(missing)}")
            new_m = np.asarray(state["m"], dtype=np.float64)
            new_v = np.asarray(state["v"], dtype=np.float64)
            if new_m.shape != (self.model.m,) or new_v.shape != (self.model.m,):
                raise ValueError("checkpoint Adam moments have incompatible shape")
            if not np.all(np.isfinite(new_m)) or not np.all(np.isfinite(new_v)) or np.any(new_v < 0):
                raise ValueError("checkpoint Adam moments must be finite and second moments non-negative")
            try:
                raw_adam_t = float(state["adam_t"])
            except (TypeError, ValueError) as error:
                raise ValueError("checkpoint Adam step is invalid") from error
            if not np.isfinite(raw_adam_t) or int(raw_adam_t) != raw_adam_t:
                raise ValueError("checkpoint Adam step must be an integer")
            new_adam_t = int(raw_adam_t)
            if new_adam_t != checkpoint.step or new_adam_t < 0:
                raise ValueError("checkpoint Adam step does not match checkpoint step")
        else:
            new_m = np.zeros(self.model.m, dtype=np.float64)
            new_v = np.zeros(self.model.m, dtype=np.float64)
            new_adam_t = 0
        new_rng = np.random.default_rng()
        if checkpoint.rng_state:
            try:
                new_rng.bit_generator.state = checkpoint.rng_state
            except (TypeError, ValueError) as error:
                raise ValueError("checkpoint RNG state is invalid") from error

        # Commit only after every checkpoint field has passed validation.
        self.model.theta = checkpoint.theta.copy()
        self.step = checkpoint.step
        self.loss_history = list(checkpoint.loss_history)
        self._m = new_m
        self._v = new_v
        self._adam_t = new_adam_t
        self._rng = new_rng

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
