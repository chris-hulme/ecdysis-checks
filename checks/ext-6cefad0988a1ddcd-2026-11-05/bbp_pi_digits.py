"""Independent check of Bailey, Borwein and Plouffe (1997): hexadecimal digits of pi
by digit extraction in ordinary double precision, with operation counts.

Ecdysis claim ext:6cefad0988a1ddcd. No external data: pi is computed independently
with mpmath (GMP backend). Randomness (the sampled digit positions) comes only from
ECDYSIS_SEED, read as a string and hashed.
"""
import hashlib
import json
import math
import os
import random
import time

import mpmath

N_HEX = 8            # hex digits taken from each double-precision extraction
D_MAX = 1_000_000    # largest position tested
N_RANDOM = 8         # random positions drawn under the seed
FIXED = [1, 1_000, 10_000, 100_000, 1_000_000]
OPS_SIZES = [100, 1_000, 10_000, 100_000]


def modpow_counted(b, e, m):
    """Left-to-right binary exponentiation; returns (b**e mod m, multiplications)."""
    if m == 1:
        return 0, 0
    r, ops = 1, 0
    for bit in bin(e)[2:]:
        r = (r * r) % m
        ops += 1
        if bit == "1":
            r = (r * b) % m
            ops += 1
    return r, ops


def series(j, d, counted=False):
    """Fractional part of sum_k 16^(d-k)/(8k+j), in double precision."""
    s, ops = 0.0, 0
    for k in range(d + 1):
        den = 8 * k + j
        if counted:
            t, n = modpow_counted(16, d - k, den)
            ops += n
        else:
            t = pow(16, d - k, den)
        s = (s + t / den) % 1.0
        ops += 2  # one division, one addition
    k = d + 1
    while True:
        term = 16.0 ** (d - k) / (8 * k + j)
        if term < 1e-17:
            break
        s += term
        ops += 2
        k += 1
    return s % 1.0, ops


def bbp_hex(pos, counted=False):
    """N_HEX hex digits of pi starting at fractional position pos (1-based)."""
    d = pos - 1
    total = 0
    parts = []
    for j in (1, 4, 5, 6):
        s, ops = series(j, d, counted)
        parts.append(s)
        total += ops
    x = (4 * parts[0] - 2 * parts[1] - parts[2] - parts[3]) % 1.0
    out = ""
    for _ in range(N_HEX):
        x *= 16
        dig = int(x)
        out += "0123456789ABCDEF"[dig]
        x -= dig
    return out, total


def reference_hex(n_digits):
    """First n_digits fractional hex digits of pi, computed independently with mpmath."""
    mpmath.mp.prec = 4 * n_digits + 128
    v = int(mpmath.floor(mpmath.ldexp(mpmath.pi, 4 * n_digits)))
    h = format(v, "X")
    assert h[0] == "3"
    return h[1:]


def main():
    seed = os.environ.get("ECDYSIS_SEED", "0")
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    positions = sorted(set(FIXED + [rng.randrange(2, D_MAX) for _ in range(N_RANDOM)]))

    t0 = time.time()
    ref = reference_hex(D_MAX + N_HEX + 8)
    print(f"reference computed in {time.time() - t0:.1f} s")

    correct_digits = 0
    positions_all_correct = 0
    first_digit_correct = 0
    for p in positions:
        got, _ = bbp_hex(p)
        want = ref[p - 1:p - 1 + N_HEX]
        n_ok = 0
        for a, b in zip(got, want):
            if a != b:
                break
            n_ok += 1
        correct_digits += n_ok
        positions_all_correct += int(n_ok == N_HEX)
        first_digit_correct += int(n_ok >= 1)
        print(f"pos {p:>8}: bbp {got} ref {want} leading digits correct {n_ok}")

    # operation counts, with a check that the counted exponentiation agrees with pow()
    ops = {}
    for d in OPS_SIZES:
        got_c, n = bbp_hex(d, counted=True)
        got_p, _ = bbp_hex(d)
        assert got_c == got_p
        ops[d] = n
        print(f"d {d:>7}: operations {n}, per d*log2(d) {n / (d * math.log2(d)):.4f}")
    ratios = [ops[d] / (d * math.log2(d)) for d in OPS_SIZES]
    xs = [math.log(d) for d in OPS_SIZES]
    ys = [math.log(ops[d]) for d in OPS_SIZES]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)

    pass_digits = first_digit_correct == len(positions)
    pass_ops = ratios[-1] <= ratios[0] * 1.05
    res = {
        "n_positions": len(positions),
        "max_position": max(positions),
        "first_digit_correct_positions": first_digit_correct,
        "all8_correct_positions": positions_all_correct,
        "mean_leading_hex_digits_correct": round(correct_digits / len(positions), 4),
        "ops_d1e2": ops[100],
        "ops_d1e3": ops[1_000],
        "ops_d1e4": ops[10_000],
        "ops_d1e5": ops[100_000],
        "ops_per_dlog2d_1e2": round(ratios[0], 4),
        "ops_per_dlog2d_1e5": round(ratios[-1], 4),
        "loglog_slope_ops_vs_d": round(slope, 4),
        "test_passed": int(pass_digits and pass_ops),
    }
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs"), exist_ok=True)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "results.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
