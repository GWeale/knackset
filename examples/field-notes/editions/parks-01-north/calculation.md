# The calculation that matters

All input values below are in supplied `counts.csv`, attributed to S1 (Bryce Canyon) or S3 (national totals). These are **recreation visits**, not a count of unique people.

Let:

- **A = 2,498,075**: Bryce Canyon, 2024 reported under the earlier method.
- **B = 1,967,367**: Bryce Canyon, 2025 reported under the refined method.
- **C = 2,437,461**: Bryce Canyon, 2025 as the park says it would have been reported under the former method. This is a stated counterfactual, not a second observed annual count.

| Question | Calculation | Result |
| --- | --- | --- |
| Change between published totals, crossing the method change | B − A | −530,708 visits |
| Percentage change between published totals | (B − A) ÷ A × 100 | −21.244678…% → **−21.2%** |
| Change using the park’s former-method comparison | C − A | −60,614 visits |
| Former-method percentage change | (C − A) ÷ A × 100 | −2.426428…% → **−2.4%** |
| Difference between 2025 methods | C − B | **470,094 visits** |
| Method gap as a share of the apparent drop | (C − B) ÷ (A − B) × 100 | 88.578653…% → **88.6%** |

The exact reconciliation is:

```text
530,708 apparent reduction = 470,094 method gap + 60,614 former-method reduction
21.244678… percentage points = 18.818250… + 2.426428…
```

Both percentage-point components use **A**, the 2024 total, as denominator. The 88.6% figure is an arithmetic decomposition of these supplied totals; it does not establish an independently measured causal share of changes in actual attendance. It also does not explain the 60,614-visit former-method reduction.

For the limited national context:

```text
2024 − 2023 = 331,863,358 − 325,498,646 = 6,364,712 visits
6,364,712 ÷ 325,498,646 × 100 = 1.955372…% ≈ 2.0% increase
```

This national calculation covers **2023–2024**, while the Bryce Canyon comparison covers **2024–2025**. It cannot establish a national 2025 trend.
