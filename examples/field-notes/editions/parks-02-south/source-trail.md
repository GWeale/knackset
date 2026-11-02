# Source trail and calculation

Prepared 2026-11-02 from the supplied `parks-desk/sources.txt` and `counts.csv` only. The source pack identifies its contents as bounded transcriptions and summaries of actual NPS material retrieved on 2026-11-02 UTC. These are not fictional sources. No linked page, archived count procedure or underlying counter record was accessed independently; links below credit the original agency material. NPS does not endorse this exercise.

| ID / original source | Date and scope supplied | What supports the account | Limit |
| --- | --- | --- | --- |
| S1 — [Bryce Canyon Visitation in 2025](https://home.nps.gov/brca/learn/news/2026-03-17-visitation-stats.htm) | Released March 17, 2026; updated March 20, 2026. Bryce annual 2024/2025 recreation visits, shuttle procedure change, 2025 former-method estimate, shutdown mention, hours and stays. | The park reports 2,498,075 visits in 2024 and 1,967,367 in 2025; estimates 2,437,461 for 2025 under the former method; explains total boardings versus unique passengers entering via shuttle. These statements share one evidential origin. | The counterfactual is a park assertion, not an independently audited observation. No monthly data, backcast of 2024 using the refined method, detailed procedure or causal estimate for the shutdown is supplied. |
| S2 — [NPS Visitor Use Statistics](https://www.nps.gov/subjects/socialscience/visitor-use-statistics.htm) | Updated May 16, 2024; general definitions and park-specific counting procedures. | Defines a visit as entry onto NPS lands/waters; explains why procedure changes can affect estimates. | Does not validate Bryce’s specific method or yield an annual unique-person count. References to archived procedures are leads, not inspected evidence. |
| S3 — [NPS Visitation Numbers](https://www.nps.gov/aboutus/visitation-numbers.htm) | Updated March 5, 2025; national recreation visits for 2023 and 2024. | 325,498,646 visits in 2023; 331,863,358 in 2024. | No national 2025 total is supplied. The earlier national change is not a control for Bryce’s later change. |
| Supplied `counts.csv` | Structured version of the S1/S3 figures. | Reproducible arithmetic below. | A transcription of those origins, not additional independent evidence. |

## The calculation that changes the headline

All counts below have the unit **recreation visits**. Each percentage decline uses 2024 Bryce recreation visits as its denominator. Values are retained exactly until final rounding.

```text
Published annual gap:
2,498,075 − 1,967,367 = 530,708 visits
530,708 / 2,498,075 × 100 = 21.244678…% decline → 21.2%

Comparable former-method gap (using the park’s 2025 estimate):
2,498,075 − 2,437,461 = 60,614 visits
60,614 / 2,498,075 × 100 = 2.426428…% decline → 2.4%

Difference between the two 2025 methods:
2,437,461 − 1,967,367 = 470,094 visits
60,614 + 470,094 = 530,708 visits
470,094 / 530,708 × 100 = 88.578653…% → about 89% of published gap

Earlier national comparison, for scope checking only:
(331,863,358 − 325,498,646) / 325,498,646 × 100
= 1.955373…% increase from 2023 to 2024 → about 2%
```

The 89% is an arithmetic allocation of the published gap using S1’s former-method estimate. It is not a measured share of people lost, a separate causal study or a claim that the residual measures demand alone.

## Rival explanations and stopping point

- **A large real attendance decline:** The mixed-method published totals initially suggest this. S1’s same-year former-method estimate materially weakens that reading. No independent procedure audit is supplied.
- **A counting change explains most of the headline:** Best supported within the pack; both the mechanism and the numerical bridge come from S1. This is the account’s interpretation of the park’s stated figures.
- **The shutdown or other travel changes explain the residual:** Plausible, unresolved. A duration and a general access statement do not identify an effect. Monthly data on consistent methods, actual access restrictions and an appropriate comparison could change the conclusion about the residual.

The supplied trail ends here. No additional independent observation tests the park’s reconstruction, and the available national, hours and overnight figures cannot isolate a 2025 cause. The recommendation is to replace “lost one visitor in five” with the qualified 21% / 2.4% explanation in `account.md`.
