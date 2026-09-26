"""Small NumPy MLP for a complete CPU imitation-learning exercise.

This is a language-conditioned visual-feature baseline, not SmolVLA and not
an end-to-end pixel VLA. No reward, policy gradients or RL library is used.
"""
import json
from pathlib import Path
import numpy as np
from .core import MAX_DELTA, bounded


class TinyPolicy:
    def __init__(self, seed=0):
        rng = np.random.default_rng(seed)
        self.params = [rng.normal(0, .25, (14, 64)), np.zeros(64),
                       rng.normal(0, .15, (64, 64)), np.zeros(64),
                       rng.normal(0, .10, (64, 2)), np.zeros(2)]

    def forward(self, x):
        w1,b1,w2,b2,w3,b3 = self.params
        h1 = np.tanh(x @ w1 + b1)
        h2 = np.tanh(h1 @ w2 + b2)
        y = h2 @ w3 + b3
        return y, h1, h2

    def action(self, x):
        return bounded(self.forward(x)[0] * MAX_DELTA)

    def save(self, path):
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, **{f"p{i}": v for i,v in enumerate(self.params)})

    @classmethod
    def load(cls, path):
        m = cls()
        with np.load(path, allow_pickle=False) as data:
            m.params = [data[f"p{i}"] for i in range(6)]
        return m


def train(dataset, output, epochs=200, seed=0):
    from integration.data import validate
    validate(dataset)
    with np.load(Path(dataset)/"samples.npz", allow_pickle=False) as data:
        x, y, split = data["x"], data["y"] / MAX_DELTA, data["split"]
    xt, yt = x[split == "train"], y[split == "train"]
    xv, yv = x[split == "val"], y[split == "val"]
    if not len(xt) or not len(xv):
        raise ValueError("Need nonempty training and validation episodes")
    model = TinyPolicy(seed); rng = np.random.default_rng(seed)
    moments = [np.zeros_like(p) for p in model.params]
    variances = [np.zeros_like(p) for p in model.params]
    history=[]; best=float("inf"); step=0
    output=Path(output); output.mkdir(parents=True, exist_ok=False)
    for epoch in range(epochs):
        order=rng.permutation(len(xt))
        for start in range(0,len(order),128):
            ix=order[start:start+128]; xb,yb=xt[ix],yt[ix]
            pred,h1,h2=model.forward(xb)
            dy=(pred-yb)/len(ix)  # derivative of mean over B*2 components
            w1,b1,w2,b2,w3,b3=model.params
            dh2=(dy @ w3.T)*(1-h2*h2)
            dh1=(dh2 @ w2.T)*(1-h1*h1)
            grads=[xb.T@dh1, dh1.sum(0), h1.T@dh2, dh2.sum(0), h2.T@dy, dy.sum(0)]
            step+=1
            for p,g,m,v in zip(model.params,grads,moments,variances):
                m *= .9; m += .1*g
                v *= .999; v += .001*g*g
                p -= .002*(m/(1-.9**step))/(np.sqrt(v/(1-.999**step))+1e-8)
        tr=float(np.mean((model.forward(xt)[0]-yt)**2))
        va=float(np.mean((model.forward(xv)[0]-yv)**2))
        history.append({"epoch":epoch+1,"train_mse_normalised":tr,"val_mse_normalised":va})
        if va<best:
            best=va; model.save(output/"policy.npz")
    (output/"history.json").write_text(json.dumps(history,indent=2))
    (output/"config.json").write_text(json.dumps({"model":"Tiny visual-feature MLP", "seed":seed,
        "epochs":epochs,"action_scale_m":MAX_DELTA,"dataset":str(Path(dataset).resolve()),
        "selection":"validation action MSE; closed-loop evaluation is separate"},indent=2))
    return {"training_steps":step,"best_validation_mse_normalised":best}
