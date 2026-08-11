# Research findings

## Problem

Place as many points as possible on `{1,…,n}²` with **no three collinear**.
The classical upper bound from pigeonhole (≤2 per row) is `2n`.
A long-standing constructive barrier is the **HJSW** family achieving
`(3/2)n − o(n)`.

This project also chased a programming-contest-style interface:
`solution(min_n) -> (n, points)` with `len(points) > 1.55n` and
`min_n ≤ n ≤ 2·min_n`. Beating `1.55` **asymptotically** is harder than
hitting it for sparse special `n`.

## HJSW construction (1975)

For an odd prime `p`, set `n = 2p`. Work with the modular hyperbola

```
H(c, p) = { (x, y) : x y ≡ c (mod p) },  c ≠ 0.
```

The ambient window (before translating to `[1,n]²`) is essentially

```
G = [−(p−1)/2, (3p−1)/2] × [0, 2p−1].
```

Normal points fall into sixteen half-blocks of side `(p−1)/2`.
HJSW keeps twelve of them (`T2`) and takes

```
S2 = H(c, p) ∩ T2.
```

Each of `p−1` admissible classes contributes three points, so

```
|S2| = 3(p−1) = (3/2)n − 3.
```

### Structure that matters for augmentation

- Congruent copies of a point inside `G` form a square.
- Lines that most often block extra points: slopes **0, ∞, ±1**.
- Unused middle blocks:

```
M = A_{0,0} ∪ B_{0,0} ∪ C_{0,1} ∪ D_{0,1}.
```

- Adding `M ∩ H(c,p)` (S3/S4-style) creates many 3-/4-in-lines;
  repairing by deletion tended to return to HJSW size.

## Experimental: HJSW + greedy

Greedy fill after HJSW (prefer underfull rows/cols / middle cells)
**sometimes** exceeds `1.55n` for particular primes.

| Observation | Detail |
|-------------|--------|
| Best verified scale in prior session | `p=281`, `n=562`, ratio ≈ **1.5516** |
| Partial winning primes | `5,7,17,19,31,37,61,67,71,83,97,107,109,139,151,167,173,181,281` |
| Pattern hunt | No clean signal mod 4/8/12/24 or QR(2/3/5) |
| Individually addable cells | Roughly `O(0.1n)`, declining in `p` |
| Greedy keep rate | Often ~half of individually addable after mutual conflicts |

**Caveat:** additive `O(1)` improvements on top of `1.5n − O(1)` do not
constitute an asymptotic breakthrough.

## Heuristics / literature pointers

- Guy–Kelly heuristic suggests density nearer `~1.81n` might be plausible.
- Ben Green has expressed suspicion that `3/2` could be asymptotically tight.
- Kovács–Nagy–Szabó (2025) improve no-`(k+1)`-in-line for `k≥3`; for `k=2`
  they still cite HJSW. Remark 3.4 suggests careful slope-`±1` deletion on
  **unions of hyperbolas** might yield a slight gain.

## Failed approaches (avoid naive repeats)

- Double parabola / exponential / Beatty placements on `p×p`
- S3/S4 middle-hyperbola + hitting-set repair
- Wholesale same-`c` fill of `M`
- Naive Moser–Tardos resampling
- Subgrid cropping of HJSW
- Treating collinearity conflicts as a featureless independent-set graph

## Preferred research direction

See `ALGEBRAIC_ADDABILITY.md` and **`FINDINGS.md`**.

Short version (2026-08-11): raw multi-hyperbola primary packing can beat HJSW
size, but for `p≥17` a deletion lower bound on non-primary lines already
exceeds that surplus — so the surplus cannot survive. See FINDINGS*.md.
Next leverage is algebraic control of arbitrary slopes, not better deletion.
