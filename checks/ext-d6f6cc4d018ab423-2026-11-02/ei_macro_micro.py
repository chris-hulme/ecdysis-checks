"""Check of ext:d6f6cc4d018ab423 (Hoel, Albantakis and Tononi 2013, PNAS 110:19790).

Effective information (EI) under uniform perturbation, micro versus macro,
for the paper's two spatial examples (Figs. 2 and 4). No external data.
"""
import itertools, json, os, sys
import numpy as np

SEED = os.environ.get("ECDYSIS_SEED", "0")  # the computation is deterministic; the seed (the archive issues 64 hex) is recorded only


def ei(tpm):
    """EI = mean over uniformly perturbed states of KL(row || mean row), in bits."""
    tpm = np.asarray(tpm, dtype=float)
    assert np.allclose(tpm.sum(axis=1), 1.0)
    avg = tpm.mean(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(tpm > 0, tpm * np.log2(tpm / avg), 0.0)
    return float(terms.sum(axis=1).mean())


def tpm_from_onprob(n, onprob):
    """Build a state-by-state TPM for n binary elements that update independently;
    onprob(state) returns the per-element probability of being on at t+1."""
    states = list(itertools.product((0, 1), repeat=n))
    idx = {s: i for i, s in enumerate(states)}
    T = np.zeros((len(states), len(states)))
    for s in states:
        p = onprob(s)
        for s2 in states:
            T[idx[s], idx[s2]] = np.prod([p[k] if s2[k] else 1 - p[k] for k in range(n)])
    return T


# Fig. 2: A, B each an AND of C and D; C, D each an AND of A and B;
# on for certain when both inputs are on, on with probability 0.3 otherwise.
NOISE = 0.3
def fig2_micro(s):
    A, B, C, D = s
    cd = 1.0 if (C and D) else NOISE
    ab = 1.0 if (A and B) else NOISE
    return [cd, cd, ab, ab]

def fig2_macro(s):
    # alpha = {A,B} on iff both on; beta = {C,D} on iff both on.
    alpha, beta = s
    # alpha' on iff A' and B' both on; A', B' independent given C,D.
    pa = 1.0 if beta else NOISE ** 2
    pb = 1.0 if alpha else NOISE ** 2
    return [pa, pb]

# Fig. 4: six deterministic AND gates in three pairs; each gate of pair k is
# the AND of the two outputs of pair k-1 (cyclically).
def fig4_micro(s):
    out = []
    for k in range(3):
        prev = s[2 * ((k - 1) % 3): 2 * ((k - 1) % 3) + 2]
        v = 1.0 if (prev[0] and prev[1]) else 0.0
        out += [v, v]
    return out

def fig4_macro(s):
    # each macro element (a pair, on iff both gates on) copies the previous one.
    return [float(s[(k - 1) % 3]) for k in range(3)]


def macro_consistency_fig2():
    """Check the macro TPM equals the micro TPM coarse-grained under uniform
    perturbation within each macro state (supervenience)."""
    Tm = tpm_from_onprob(4, fig2_micro)
    states = list(itertools.product((0, 1), repeat=4))
    grp = lambda s: (int(s[0] and s[1]), int(s[2] and s[3]))
    M = np.zeros((4, 4)); cnt = np.zeros(4)
    mstates = list(itertools.product((0, 1), repeat=2))
    mi = {s: i for i, s in enumerate(mstates)}
    for i, s in enumerate(states):
        r = np.zeros(4)
        for j, s2 in enumerate(states):
            r[mi[grp(s2)]] += Tm[i, j]
        M[mi[grp(s)]] += r; cnt[mi[grp(s)]] += 1
    M /= cnt[:, None]
    return float(np.abs(M - tpm_from_onprob(2, fig2_macro)).max())


def main(outdir):
    r = {
        "ei_fig2_micro": ei(tpm_from_onprob(4, fig2_micro)),
        "ei_fig2_macro": ei(tpm_from_onprob(2, fig2_macro)),
        "ei_fig4_micro": ei(tpm_from_onprob(6, fig4_micro)),
        "ei_fig4_macro": ei(tpm_from_onprob(3, fig4_macro)),
    }
    r["gain_fig2"] = r["ei_fig2_macro"] - r["ei_fig2_micro"]
    r["gain_fig4"] = r["ei_fig4_macro"] - r["ei_fig4_micro"]
    r["fig2_macro_supervenience_maxdev"] = macro_consistency_fig2()
    printed = {"ei_fig2_micro": 1.15, "ei_fig2_macro": 1.55, "ei_fig4_micro": 2.43, "ei_fig4_macro": 3.0}
    ok_print = all(abs(round(r[k], 2) - v) < 1e-9 or abs(np.floor(r[k] * 100) / 100 - v) < 1e-9
                   for k, v in printed.items())
    r["matches_printed_two_decimals"] = 1 if ok_print else 0
    r["macro_beats_micro_both"] = 1 if (r["gain_fig2"] > 0 and r["gain_fig4"] > 0) else 0
    r["seed"] = SEED
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "results.json"), "w") as f:
        json.dump(r, f, indent=2)
    print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs"))
