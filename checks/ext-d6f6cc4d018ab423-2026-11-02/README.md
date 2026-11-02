# Check of ext:d6f6cc4d018ab423 (2 November 2026)

**Claim.** Hoel, Albantakis and Tononi (2013), *Quantifying causal emergence shows that macro can beat micro*, PNAS 110(49), 19790-19795 (doi:10.1073/pnas.1314922110): "Although in the example systems the macro mechanisms are completely specified by their underlying micro mechanisms, EI can nevertheless peak at a macro spatiotemporal scale."

**Test on the record.** Refuted if, in either spatial example (Fig. 2: A and B each an AND of C and D, C and D each an AND of A and B, on for certain when both inputs are on and with probability 0.3 otherwise; Fig. 4: six deterministic AND gates in three pairs, each gate taking the previous pair's outputs, in a cycle), EI under uniform perturbation at the macro level (each pair one element, on only when both are on) does not exceed EI at the micro level, or the four EI values differ from the printed 1.15, 1.55, 2.43 and 3 bits at two decimals.

**Method.** An independent implementation (a replication, not the authors' code). Each system's state-by-state transition probability matrix is built from its element mechanisms, with elements conditionally independent given the current state. EI is the mean, over all states set with equal probability, of the Kullback-Leibler divergence (bits) of each state's effect distribution from the average effect distribution. The macro matrices are derived from the macro mechanisms; for Fig. 2 the script also confirms that the macro matrix equals the micro matrix coarse-grained under uniform perturbation within each macro state (maximum deviation reported).

**Data sources.** None: every system is defined by construction in the paper's text (Fig. 2's noise level of 0.3 as Hoel et al. 2016 give it for the same system).

**Run.** `pip install -r requirements.txt && python checks/ext-d6f6cc4d018ab423-2026-11-02/ei_macro_micro.py`. The computation is deterministic; `ECDYSIS_SEED` (default 0) is read and recorded only.

**Result (seed 0).** Fig. 2: micro EI 1.149 bits, macro EI 1.552 bits. Fig. 4: micro EI 2.434 bits, macro EI 3.000 bits. All four values match the printed 1.15, 1.55, 2.43 and 3 bits at two decimals, and in both examples EI is higher at the macro level. The test is passed: the claim is confirmed for the spatial examples.

**Limits.** Only the spatial examples (Figs. 2 and 4) are checked, as the registered test specifies; the temporal and spatiotemporal examples (Figs. 5 and 6) are not. The check confirms the arithmetic of the construction; it does not address whether EI is an appropriate measure of causal power, which is a matter for argument. Fig. 2's noise parameter is taken from a later paper by the same group.
