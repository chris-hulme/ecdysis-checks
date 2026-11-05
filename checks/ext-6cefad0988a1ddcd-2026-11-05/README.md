# Check of ext:6cefad0988a1ddcd (Bailey, Borwein and Plouffe 1997)

## Claim
"These algorithms can be easily implemented (multiple precision arithmetic is not needed), require virtually no memory, and feature run times that scale nearly linearly with the order of the digit desired." (Mathematics of Computation 66, 903-913; doi:10.1090/s0025-5718-97-00856-9)

Registered test: refuted if the paper's algorithm for the hexadecimal digits of pi, run in ordinary double precision with modular exponentiation, gives a wrong digit at a position where pi is known independently, or needs a number of operations growing faster than d log d in the position d.

## Method
An independent implementation (replication) of the BBP digit-extraction scheme: pi = sum_k 16^-k (4/(8k+1) - 2/(8k+4) - 1/(8k+5) - 1/(8k+6)). For a position p (1-based after the hexadecimal point), with d = p - 1, each of the four series is split into a head (k <= d, terms 16^(d-k) mod (8k+j) divided by 8k+j, accumulated modulo 1 in IEEE double precision) and a short tail (k > d, terms below 1e-17 dropped). Eight hexadecimal digits are read from the combined fractional part. No multiple precision arithmetic is used in the extraction (Python integers in pow() never exceed the modulus squared, below 2^43 at d = 10^6).

Positions tested: 1, 1000, 10^4, 10^5, 10^6 and 8 positions drawn uniformly from [2, 10^6) by a generator seeded with SHA-256 of ECDYSIS_SEED (read as a string; default "0").

Independent reference: the first 10^6 + 16 hexadecimal digits of pi computed with mpmath (GMP backend) at 4 x 10^6 + 128 bits, by an unrelated algorithm.

Operation count: modular multiplications in left-to-right binary exponentiation, plus one division and one addition per term, counted for d = 10^2, 10^3, 10^4, 10^5; the counted exponentiation is checked to give the same digits as Python's pow(). The test treats growth as no faster than d log d if operations / (d log2 d) does not rise from d = 10^2 to d = 10^5 (5% allowance).

## Data
None: the claim concerns an algorithm by construction. No files are downloaded.

## Result (seed "0")
All 13 positions gave 8 correct leading hexadecimal digits, including 26C65E52 at position 10^6, which also agrees with the widely published value 26C65E52CB4593 for that position. Operations per d log2 d fell from 6.68 (d = 100) to 6.22 (d = 10^5); the log-log slope of operations against d is 1.12, as expected for d log d. The registered test is passed.

## Limits
Positions above 10^6 were not tested (pure Python). "Virtually no memory" and "easily implemented" are not measured. Eight digits per extraction is a conservative choice; double precision rounding limits how many digits a single extraction yields.

## Run
pip install -r requirements.txt; python checks/ext-6cefad0988a1ddcd-2026-11-05/bbp_pi_digits.py (about 20 seconds). Output: outputs/results.json.
