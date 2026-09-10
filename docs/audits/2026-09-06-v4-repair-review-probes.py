"""Independent follow-up probes. Reproduced=True means a defect remains.

Only temporary fixtures are written; production/sibling artifacts are read-only.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts/v4_tcdp' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    results = {}
    from merlin_iqp.classical import IQPModel, Trainer, ExactProbabilities
    from merlin_iqp.classical._validation import hash_array
    trainer = Trainer(IQPModel(np.eye(2, dtype=np.uint8), np.array([.2, .3])), ExactProbabilities(np.array([0., 0., 0., 1.])), kernel='spatial_gaussian')
    run = trainer.run(1)
    results['spatial_geometry'] = {'reproduced': bool(abs(run['final_loss']) < 1e-15), 'loss': run['final_loss'], 'TVD': float(1-trainer.model.probability_vector_exact()[-1])}

    cache = ROOT / '.pytest_cache'
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as temporary:
        directory = Path(temporary)
        compare = load_script('compare_backends')
        source = ROOT / 'results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke'
        fixture = directory / 'comparison'
        fixture.mkdir()
        for name in ('run.npz', 'dataset.npz', 'manifest.json'):
            shutil.copy2(source/name, fixture/name)
        with np.load(fixture/'run.npz') as archive:
            arrays = {key: archive[key].copy() for key in archive.files}
        arrays['final_theta'][0] += .02
        np.savez(fixture/'run.npz', **arrays)
        comparison = compare.build_comparison(fixture)
        recorded = comparison.common_manifest['theta_hash']
        actual = hash_array(arrays['final_theta'])
        results['stale_artifact'] = {'reproduced': recorded != actual, 'recorded_theta_hash': recorded, 'actual_theta_hash': actual}

        from merlin_iqp.experiments.rings import resolve_config, train_rings, write_run_artifacts
        ring_root = directory/'rings'
        parity = train_rings(resolve_config('rings_hamming', n=4, seed=0, steps=0))
        first_paths = write_run_artifacts(parity, ring_root)
        before = first_paths['run'].read_bytes()
        ablation = train_rings(resolve_config('rings_hamming', n=4, seed=0, steps=0, initialization='uniform'))
        second_paths = write_run_artifacts(ablation, ring_root)
        results['ablation_overwrite'] = {'reproduced': first_paths['run']==second_paths['run'] and before!=second_paths['run'].read_bytes(), 'same_destination': first_paths['run']==second_paths['run']}

        validate = load_script('validate_deploy')
        from merlin_iqp.deploy.maps import reconstruct_cp_map
        from merlin_iqp.deploy.fock import FullFockResult
        analytic_gate = reconstruct_cp_map(.7, use_perceval=False)
        analytic_gate.metadata['perceval'] = {'status':'PASS'}
        analytic_gate.metadata['perceval_probe'] = {'status':'PASS'}
        with patch.object(validate, 'reconstruct_cp_map', return_value=analytic_gate), patch.object(validate, 'full_fock_cp_reference', return_value=FullFockResult('INCONCLUSIVE', diagnostics={'reason':'injected missing physical evidence'})):
            validation = validate.run(with_perceval=True)
        results['physical_aggregate'] = {'reproduced':validation['status']=='PASS' and validation['full_fock']['status']=='INCONCLUSIVE', 'overall':validation['status'], 'fock':validation['full_fock']['status']}

        retrain = load_script('retrain_sibling')
        sibling = directory / 'fake_sibling'
        historical = sibling / 'results/training_smoke'
        historical.mkdir(parents=True)
        (historical/'results.jsonl').write_text(json.dumps({'n':6, 'trajectory_path':'results/training_smoke/trajectory.jsonl'})+'\n')
        (historical/'trajectory.jsonl').write_text(json.dumps({'step':0, 'theta':[.1,.2], 'loss':.5})+'\n')
        requested = directory/'different-config.yaml'
        requested.write_text('experiment:\n  name: intentionally_different\ntraining:\n  num_steps: 999\n')
        observed = {}
        fake_module = types.ModuleType('iqp_bp.experiments.run_training')
        def fake_run(config):
            observed.update({'experiment': config['experiment']['name'], 'steps': config['training']['num_steps']})
            destination = Path(config['experiment']['output_dir'])
            destination.mkdir(parents=True)
            trajectory = destination/'trajectory.jsonl'
            trajectory.write_text(json.dumps({'step':0, 'theta':[float('nan'),float('nan')], 'loss':float('nan')})+'\n')
            return [{'trajectory_path':str(trajectory)}]
        fake_module.run = fake_run
        with patch.dict(sys.modules, {'iqp_bp.experiments.run_training':fake_module}):
            report = retrain.run_retraining(requested, sibling, directory/'rerun')
        results['ignored_config'] = {'reproduced': observed['experiment'] != 'intentionally_different', 'executed':observed, 'reported_config':report['source_config']}
        results['nan_false_pass'] = {'reproduced':report['status']=='PASS', 'status':report['status'], 'theta_error':report['max_theta_abs_error'], 'loss_error':report['max_loss_abs_error']}
        results['unverified_source'] = {'reproduced':report['sibling_unchanged_by_adapter'] is True, 'fake_root_has_git':(sibling/'.git').exists()}
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
