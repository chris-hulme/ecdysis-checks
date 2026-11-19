"""Independent check of ext:829df225aeb1af24 (Balduzzi and Tononi 2008, claim (ii)).

phi as defined in the registered test: effective information (ei) of the
transition x0 -> x1 is computed against the product of the parts' repertoires
for the total partition and every bipartition; inputs from outside a part are
averaged at maximum entropy; the minimum information partition (MIP) minimises
ei / N_P, with N_P = H_max(X0) for the total partition and
(k - 1) * min_k H_max(M0^k) otherwise; phi = ei across the MIP.
Pure Python (stdlib only). No randomness is needed; ECDYSIS_SEED is read as a
string and hashed only so that the run records which seed it ran under.
"""
import hashlib, itertools, json, math, os, sys

SEED = os.environ.get("ECDYSIS_SEED", "0")
SEED_INT = int(hashlib.sha256(SEED.encode()).hexdigest()[:8], 16)  # unused: deterministic
TOL = 1e-12


def states(n):
    return list(itertools.product((0, 1), repeat=n))


def part_cond(mechs, n, part, m0_idx_state, mu1):
    """p(mu1 | m0) for part, outside inputs averaged at maximum entropy.
    mechs[i](x) -> probability that element i is ON at t given full state x at t-1."""
    outside = [i for i in range(n) if i not in part]
    tot = 0.0
    for o in itertools.product((0, 1), repeat=len(outside)):
        x = [0] * n
        for i, v in zip(part, m0_idx_state):
            x[i] = v
        for i, v in zip(outside, o):
            x[i] = v
        p = 1.0
        for i, v in zip(part, mu1):
            q = mechs[i](tuple(x))
            p *= q if v else 1.0 - q
        tot += p
    return tot / (2 ** len(outside))


def repertoire(mechs, n, part, mu1):
    """a posteriori repertoire over the part's past states (uniform a priori)."""
    sts = states(len(part))
    w = [part_cond(mechs, n, part, s, mu1) for s in sts]
    z = sum(w)
    if z <= 0:
        return None
    return {s: wi / z for s, wi in zip(sts, w)}


def ei_partition(mechs, n, x1, parts):
    actual = repertoire(mechs, n, list(range(n)), x1)
    if actual is None:
        return None
    if len(parts) == 1:
        # total partition: ei of the whole, against the maximum entropy repertoire
        reps = [{x0: 2.0 ** -n for x0 in actual}]
    else:
        reps = [repertoire(mechs, n, p, tuple(x1[i] for i in p)) for p in parts]
    ei = 0.0
    for x0, pa in actual.items():
        if pa <= TOL:
            continue
        q = 1.0
        for p, r in zip(parts, reps):
            q *= r[tuple(x0[i] for i in p)]
        ei += pa * math.log2(pa / q)
    return max(ei, 0.0)


def bipartitions(n):
    els = list(range(n))
    out = []
    for r in range(1, n // 2 + 1):
        for a in itertools.combinations(els, r):
            b = tuple(i for i in els if i not in a)
            if r == n - r and a > b:
                continue
            out.append([list(a), list(b)])
    return out


def phi(mechs, n, x1):
    """Returns (phi with ties broken towards bipartitions, phi with ties towards total)."""
    cands = [([list(range(n))], float(n))]
    cands += [(p, float(min(len(q) for q in p))) for p in bipartitions(n)]
    vals = []
    for p, norm in cands:
        e = ei_partition(mechs, n, x1, p)
        if e is None:
            return None
        vals.append((e / norm, len(p), e))
    best = min(v[0] for v in vals)
    tied = [v for v in vals if abs(v[0] - best) < 1e-9]
    bi = [v[2] for v in tied if v[1] == 2]
    tot = [v[2] for v in tied if v[1] == 1]
    phi_bi = min(bi) if bi else tot[0]
    phi_tot = tot[0] if tot else min(bi)
    return phi_bi, phi_tot


def reachable(mechs, n):
    out = set()
    for x in states(n):
        out.add(tuple(1 if mechs[i](x) > 0.5 else 0 for i in range(n)))
    return sorted(out)


# Binary counter (Figure 11): bit i flips when all lower bits are on.
def counter_mech(i):
    return lambda x: float(x[i] ^ all(x[j] for j in range(i)))

COUNTER = [counter_mech(i) for i in range(4)]
# Replay: four non-interacting elements driven from outside the system (a tape);
# within the system each element has no inputs, so it is ON with p = 0.5 whatever X0.
REPLAY = [lambda x: 0.5] * 4
# Replay variant: each element connected only to itself (no interaction).
REPLAY_SELF = [lambda x, i=i: float(x[i]) for i in range(4)]
# AND-gates (Figure 1): each of three elements is an AND of the other two.
# Copies (Figure 6): element 3+i copies AND-gate i.
AND3 = [lambda x: float(x[1] and x[2]), lambda x: float(x[0] and x[2]), lambda x: float(x[0] and x[1])]
COPY6 = AND3 + [lambda x, i=i: float(x[i]) for i in range(3)]


def main():
    res = {}
    c = [phi(COUNTER, 4, s) for s in states(4)]
    cb = [v[0] for v in c]
    ct = [v[1] for v in c]
    res["counter_phi_min"] = min(cb)
    res["counter_phi_max"] = max(cb)
    res["counter_states_phi_zero"] = sum(1 for v in cb if v <= 1e-9)
    res["counter_states_phi_near_019"] = sum(1 for v in cb if abs(v - 0.19) <= 0.01)
    res["counter_phi_closest_to_019"] = min(cb, key=lambda v: abs(v - 0.19))
    res["counter_states_tie_total"] = sum(1 for a, b in c if abs(a - b) > 1e-9)
    res["counter_phi_max_ties_total"] = max(ct)
    r1 = [phi(REPLAY, 4, s) for s in states(4)]
    r2 = [phi(REPLAY_SELF, 4, s) for s in states(4)]
    res["replay_phi_max"] = max(max(v) for v in r1)
    res["replay_self_phi_max"] = max(max(v) for v in r2)
    reach = reachable(COPY6, 6)
    p6 = [phi(COPY6, 6, s) for s in reach]
    res["copies_reachable_states"] = len(reach)
    res["copies_phi_max"] = max(max(v) for v in p6)
    a3 = [phi(AND3, 3, s) for s in reachable(AND3, 3)]
    res["and3_phi_max"] = max(v[0] for v in a3)
    ok = (res["counter_states_phi_zero"] == 0 and res["counter_states_phi_near_019"] >= 1
          and res["replay_phi_max"] <= 1e-9 and res["replay_self_phi_max"] <= 1e-9
          and res["copies_phi_max"] <= 1e-9)
    res["test_passed"] = 1 if ok else 0
    res = {k: (round(v, 6) if isinstance(v, float) else v) for k, v in res.items()}
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "outputs"), exist_ok=True)
    with open(os.path.join(here, "outputs", "results.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(res, indent=2, sort_keys=True))
    print("per-state counter phi:", [round(v, 4) for v in cb], file=sys.stderr)


if __name__ == "__main__":
    main()
