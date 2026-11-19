# Check of ext:829df225aeb1af24 (Balduzzi and Tononi 2008)

**Claim (ii):** phi varies for systems with identical or similar surface dynamics depending on the underlying causal architecture, being low for systems that merely copy or replay activity states (PLoS Comput Biol 4(6): e1000091, doi:10.1371/journal.pcbi.1000091).

**Kind:** independent replication (own code), method as stated in the registered test. No external data: the systems are defined by construction.

## Method

phi is computed as the registered test defines it. For a transition x0 -> x1, the actual repertoire is the a posteriori distribution over past states given x1 (uniform a priori). Effective information across a partition is the relative entropy between the actual repertoire and the product of the parts' repertoires, where inputs from outside a part are averaged at maximum entropy. For the total partition the reference is the maximum entropy repertoire. Candidates are the total partition (normalised by H_max(X0)) and every bipartition (normalised by the size of the smaller part, in bits). The minimum information partition minimises normalised ei; phi is the unnormalised ei across it. When the total partition ties exactly with a bipartition, the script reports phi both ways.

Systems:

1. Binary counter (Figure 11): four memoryless elements; bit i flips when all lower bits are on.
2. Replay: four non-interacting elements reproducing the counter's sequence. Modelled two ways: driven by an external tape (no inputs within the system), and each element connected only to itself.
3. AND-gates of Figure 1 (each of three elements is an AND of the other two) with three elements copying them (Figure 6), over every state the six-element system can enter.

## Result (seed 0; the computation is deterministic)

- Counter: phi > 0 in all 16 states; phi = 0.1926 bits (log2 8/7) in 14 states, matching the printed 0.19 to 0.01; 1 bit in the two states where the top bit flips (4 bits if exact ties go to the total partition).
- Replay: phi = 0 in every state under both models.
- AND-gates with copies: phi = 0 as a whole in all 8 reachable states (the AND-gates alone reach 1 bit).

The registered test is passed: `test_passed = 1`.

## Limits

- The paper's full text could not be fetched from this sandbox; the definitions follow the registered test. The Figure 1 architecture (each AND-gate driven by the other two) is assumed. The copies result does not depend on it: the bipartition that keeps each copy with its source loses no information whatever the AND-gates' wiring.
- The counter's 4-bit states depend on tie-breaking, which the registered test leaves open.
- Only the systems named in the test are checked; the scrambled sequence printed as an image is not.

## Run

`python checks/ext-829df225aeb1af24-2026-11-19/phi_check.py` writes `outputs/results.json`. `ECDYSIS_SEED` is read as a string; no randomness is used.
