"""Ecdysis check of ext:42826af46a5f52c7 (Ganguli et al. 2022, arXiv:2209.07858).

Claim: RLHF models become harder to red team as they scale; the other model
types show a flat trend. Metric (the paper's Figure 1, middle): the average
over attacks of the minimum harmlessness preference-model score in each
transcript, per model type and size. Higher means harder to red team.

Registered test: RLHF average rises 2.7B -> 13B and 13B -> 52B, and for each
of plain LM, prompted LM (context distillation in the data) and rejection
sampling, |mean(52B) - mean(2.7B)| < 0.5 * (RLHF mean(52B) - RLHF mean(2.7B)).
"""
import gzip, hashlib, json, os, random, sys, urllib.request
from pathlib import Path

URL = ("https://raw.githubusercontent.com/anthropics/hh-rlhf/"
       "c72f5cee8eb7b4d2ea5617657f4430d5e333af07/red-team-attempts/"
       "red_team_attempts.jsonl.gz")
SHA256 = "4c7b0069991460f0064f279fd400b51f3f0095697d14d7793c49b0925f80814f"
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
CACHE = HERE / "data" / "red_team_attempts.jsonl.gz"
TYPES = {"plain lm": "plain", "context distillation": "prompted",
         "rejection sampling": "rs", "rlhf": "rlhf"}
SIZES = {"2.7B": "2p7b", "13B": "13b", "52B": "52b"}
N_BOOT = 2000


def fetch():
    if not CACHE.exists():
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, CACHE)
    h = hashlib.sha256(CACHE.read_bytes()).hexdigest()
    if h != SHA256:
        sys.exit(f"sha256 mismatch: {h}")
    return json.loads(gzip.decompress(CACHE.read_bytes()).decode("utf-8"))


def mean(xs):
    return sum(xs) / len(xs)


def verdict(m):
    rise = m[("rlhf", "52b")] - m[("rlhf", "2p7b")]
    ok = (m[("rlhf", "13b")] > m[("rlhf", "2p7b")]
          and m[("rlhf", "52b")] > m[("rlhf", "13b")])
    ratios = {}
    for t in ("plain", "prompted", "rs"):
        ratios[t] = abs(m[(t, "52b")] - m[(t, "2p7b")]) / rise if rise > 0 else float("inf")
        ok = ok and ratios[t] < 0.5
    return ok, rise, ratios


def main():
    seed_str = os.environ.get("ECDYSIS_SEED", "0")
    seed = int.from_bytes(hashlib.sha256(seed_str.encode()).digest()[:8], "big")
    rng = random.Random(seed)
    rows = fetch()
    groups = {}
    for r in rows:
        k = (TYPES[r["model_type"]], SIZES[r["num_params"]])
        groups.setdefault(k, []).append(float(r["min_harmlessness_score_transcript"]))
    m = {k: mean(v) for k, v in groups.items()}
    ok, rise, ratios = verdict(m)
    # Bootstrap over attacks within each cell: share of resamples passing the test.
    passes = 0
    for _ in range(N_BOOT):
        mb = {k: mean([v[rng.randrange(len(v))] for _ in range(len(v))])
              for k, v in groups.items()}
        passes += verdict(mb)[0]
    out = {f"mean_{t}_{s}": round(m[(t, s)], 6)
           for t in TYPES.values() for s in SIZES.values()}
    out["rlhf_rise_2p7b_to_52b"] = round(rise, 6)
    for t, v in ratios.items():
        out[f"ratio_{t}_change_to_rlhf_rise"] = round(v, 6)
    out["n_attacks"] = len(rows)
    out["test_passed"] = int(ok)
    out["bootstrap_pass_fraction"] = round(passes / N_BOOT, 4)
    OUT.mkdir(exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
