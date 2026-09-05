import sys, json, tempfile, csv
from pathlib import Path
from types import SimpleNamespace
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from merlin_iqp.trainability.sweep import pooled_gradients_for_cell
from scripts.v3_hardness import loss_sweep
from scripts.v3_trainability import gradient_variance_sweep as train_sweep
from merlin_iqp.hardness import sweep

one, count = pooled_gradients_for_cell(3, 'weight1', 'data_dependent', 0, 1)
two, _ = pooled_gradients_for_cell(3, 'weight1', 'data_dependent', 0, 2)
print('deterministic_init', json.dumps({'gradient':one.tolist(), 'pooled_var':float(np.var(one)), 'per_coordinate_var':np.var(two.reshape(2,count),axis=0).tolist()}))
with tempfile.TemporaryDirectory() as temp:
    out = str(Path(temp)/'loss.csv')
    args = SimpleNamespace(n_values=[2], eta_grid=[.9], out=out, backend='polarization',scope='weight1',n_draws=3)
    width = len(sweep._quantities_for_scope('weight1'))
    for start, vals in [(0,[0.1,0.9]),(1,[0.9,0.2])]:
        np.save(loss_sweep._chunk_path(out,'polarization','weight1',2,.9,start,2), np.repeat(np.array(vals)[:,None],width,axis=1))
    with open(out,'w',newline='') as f:
        rows = loss_sweep.combine_chunks(args,csv.DictWriter(f,fieldnames=loss_sweep.FIELDNAMES),f)
    print('overlapping_loss_chunks',json.dumps({'reported_draws':rows[0]['n_draws'],'reported_mean':rows[0]['tvd_to_lossless_mean'],'unique_draws':3,'correct_unique_mean':float(np.mean([.1,.9,.2]))}))
    out = str(Path(temp)/'train.csv')
    args = SimpleNamespace(n_values=[2],init_schemes=['uniform'],out=out,scope='weight1',sigma=.1,max_tracked_params=2,scale_factor=1.0)
    for start, vals in [(0,[.1,.1,.9,.9]),(1,[.9,.9,.2,.2])]:
        np.save(train_sweep._chunk_path(out,'weight1',2,'uniform',.1,start,2),np.array(vals))
    class Capture:
        def writerow(self,row): self.row=row
    writer=Capture()
    with open(out,'w') as f: train_sweep.combine_chunks(args,writer,f)
    print('overlapping_train_chunks',json.dumps(writer.row))
