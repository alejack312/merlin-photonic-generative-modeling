"""Phase-tagged study scripts: sweep runners, analysis CLIs, and de-risking
probes for the merlin_iqp v1.0/v2.x/v3.0 milestones.

Not a reusable library surface -- these are one-off, provenance-documented
experiment scripts that import from the installed ``merlin_iqp`` package.
Run individually from the repository root, e.g. ``python
scripts/natural_order_train.py``. This ``__init__.py`` exists only so tests
can import script internals as ``scripts.<name>`` for direct unit testing.
"""
