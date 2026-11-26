# TITO Test Results — APICN001

- Date tested: 2026-11-26
- LLM_PROVIDER: slm | groq | openai | anthropic | openrouter  → results below were drafted from the retrieved corpus context; regenerate the bot's verbatim output with `python scripts/run_test_suite.py` against your configured provider
- LLM_MODEL: default per provider (e.g. slm `llama3.1:8b`, groq `llama-3.3-70b-versatile`)
- Retrieved top-k: 5
- Vector store: hybrid BM25 + dense (all-MiniLM-L6-v2) with Reciprocal Rank Fusion

> **Honesty note.** The "Sources cited" column is the retriever's **actual** output
> (hybrid top-k, captured from this repo's index). The "Answer given" column holds
> reference answers grounded in those sources, drafted with AI assistance (see
> `SUBMISSION.md`); run `scripts/run_test_suite.py` to replace them with the live
> bot's verbatim text. "Correct?" is our honest self-assessment against the corpus.

## Easy

| ID | Question | Answer given | Correct? (yes/partial/no) | Evaluator note | Sources cited |
|----|----------|--------------|---------------------------|----------------|---------------|
| Q-E01 | What are the income tax slab rates for an individual under the new regime for FY 2024-25 (AY 2025-26)? | Under the revised new regime (Budget, July 2024) for FY 2024-25: ₹0–3,00,000 Nil; ₹3,00,001–7,00,000 5%; ₹7,00,001–10,00,000 10%; ₹10,00,001–12,00,000 15%; ₹12,00,001–15,00,000 20%; above ₹15,00,000 30%. Plus 4% health & education cess; rebate u/s 87A makes tax nil up to ₹7,00,000 taxable income; standard deduction ₹75,000 for salaried. | yes | Revised slabs per the full Budget 2024-25 (effective FY 2024-25). | bs2025_26.pdf, p.32; Updated-FQAs-on-Interplay&Transitions.pdf, p.10; bs2023_24.pdf, p.37 |
| Q-E02 | What is the maximum deduction allowed under Section 80C in a financial year, and name three eligible investments? | The maximum deduction under Section 80C is ₹1,50,000 per financial year (aggregate with 80CCC/80CCD(1)). Three eligible investments: Public Provident Fund (PPF), Equity-Linked Savings Scheme (ELSS), and life insurance premium (others: EPF, 5-year tax-saver FD, NSC, principal repayment of a housing loan, tuition fees). | yes | 80C limit unchanged (old regime only). | Updated-FQAs-on-Interplay&Transitions.pdf, p.78; Updated-FQAs-on-Interplay&Transitions.pdf, p.79; bs2024_25.pdf, p.54 |
| Q-E03 | What is the basic exemption limit for a resident individual under 60 years of age under the old regime? | Under the old regime, the basic exemption limit for a resident individual below 60 years is ₹2,50,000. (It is ₹3,00,000 for senior citizens 60–80 and ₹5,00,000 for super-senior 80+.) | yes | | bs2023_24.pdf, p.39; bs2023_24.pdf, p.37; Updated-FQAs-on-Interplay&Transitions.pdf, p.87 |
| Q-E04 | What is the standard deduction available to a salaried employee under the new tax regime for FY 2024-25? | ₹75,000, raised from ₹50,000 by the July 2024 Budget for the new regime, FY 2024-25 (AY 2025-26). (The old regime standard deduction stays ₹50,000.) | yes | | bs2024_25.pdf, p.32; bs2024_25.pdf, p.54; bs2023_24.pdf, p.38 |
| Q-E05 | What is the tax rate applicable to income from capital gains on listed equity shares held for more than 12 months (long-term capital gains) as per the latest budget? | Under Section 112A, LTCG on listed equity (STT paid) held > 12 months is taxed at 12.5% (raised from 10%) on gains exceeding the enhanced exemption of ₹1,25,000 per year, without indexation, for transfers on or after 23 July 2024. | yes | Budget 2024 rate/exemption change. | bs2024_25.pdf, p.30; bs2024_25.pdf, p.56 |

## Medium

| ID | Question | Answer given | Correct? (yes/partial/no) | Evaluator note | Sources cited |
|----|----------|--------------|---------------------------|----------------|---------------|
| Q-M01 | A salaried individual earns ₹18,00,000 gross annual salary in FY 2024-25, contributes ₹1,50,000 to EPF, pays ₹50,000 NPS Tier-1, and has ₹25,000 health insurance premium. Compute tax under the new regime (assume no other deductions, standard deduction applies). | Under the new regime these deductions (own EPF 80C, NPS 80CCD(1B), 80D health insurance) are not allowed; only the ₹75,000 standard deduction applies. Taxable = 18,00,000 − 75,000 = ₹17,25,000. Tax = ₹2,07,500; + 4% cess ₹8,300 = **₹2,15,800**. (Working below.) | yes | New regime disallows the listed deductions; that is the key point. | bs2024_25.pdf, p.32; bs2024_25.pdf, p.33; bs2024_25.pdf, p.37 |
| Q-M02 | I bought a residential property for ₹80,00,000 in 2018 and sold it in FY 2024-25 for ₹1,20,00,000. Compute the capital gains tax due (you may state your assumptions on indexation clearly). | Long-term (held > 24 months). For property bought before 23 July 2024, Budget 2024 lets a resident choose the lower of: (A) 12.5% without indexation = 12.5% × ₹40,00,000 = ₹5,00,000; or (B) 20% with indexation (CII 2018-19=280, 2024-25=363): indexed cost ₹1,03,71,429, gain ₹16,28,571, tax ₹3,25,714. Lower = option B ≈ **₹3,25,714 + 4% cess = ₹3,38,743**. | partial | Depends on the stated indexation assumption; both options shown. | bs2024_25.pdf, p.58; Updated-FQAs-on-Interplay&Transitions.pdf, p.93; bs2023_24.pdf, p.44 |
| Q-M03 | An individual transfers ₹12,00,000 in a financial year under the Liberalised Remittance Scheme (LRS) for foreign education. What is the TCS rate that applies after the FY 2023-24 changes to Section 206C, and what exemption applies? | For LRS remittances for education, there is no TCS up to ₹7,00,000 per FY. Above ₹7,00,000: 0.5% if the education is funded by a loan from a financial institution (Sec 80E), else 5%. So on ₹12,00,000 (not loan-funded): TCS = 5% × (12,00,000 − 7,00,000) = **₹25,000**; if loan-funded, 0.5% × ₹5,00,000 = ₹2,500. The ₹7,00,000 threshold is the exemption. | yes | The 20% general LRS rate does not apply to education; threshold + reduced rates do. | bs2023_24.pdf, p.44; bs2023_24.pdf, p.48; bs2025_26.pdf, p.51 |
| Q-M04 | What are the provisions for taxation of Virtual Digital Assets (cryptocurrency) under Section 115BBH, including the rate, the loss set-off rule, and the TDS under Section 194S? | Section 115BBH taxes income from transfer of a VDA at a flat 30% (plus surcharge and 4% cess). No deduction is allowed except cost of acquisition. Loss from one VDA cannot be set off against gain from another VDA or any other income, and cannot be carried forward. Section 194S imposes 1% TDS on the consideration for a VDA transfer above the threshold (₹50,000/₹10,000 depending on payer). Introduced in Budget 2022-23. | yes | Rate, no-set-off, and 1% TDS all stated. | bs202223.pdf, p.27; Updated-FQAs-on-Interplay&Transitions.pdf, p.18; E-Book-Guidance-Note-Crypto-Asset-Reporting-Obligations.pdf, p.2 |
| Q-M05 | A taxpayer has both salary income and house property income (one self-occupied house with home-loan interest of ₹2,00,000). Under which regime (old vs new) would their tax be lower, and why? Assume gross total income of ₹15,00,000, all of it except the interest deduction being salary. | New regime is lower. Old: 15,00,000 − 50,000 (std) − 2,00,000 (self-occupied interest) = 12,50,000 → tax ₹1,87,500 + cess = **₹1,95,000**. New (FY24-25): no self-occupied interest; 15,00,000 − 75,000 = 14,25,000 → tax ₹1,25,000 + cess = **₹1,30,000**. The lower new-regime slabs outweigh the lost ₹2,00,000 interest deduction. | yes | Correct approach and figures; recommend new regime. | bs2025_26.pdf, p.50; bs2023_24.pdf, p.39; bs2024_25.pdf, p.33 |

<details><summary>Q-M01 working</summary>

New-regime slabs on ₹17,25,000: 3–7L @5% = 20,000; 7–10L @10% = 30,000; 10–12L @15% = 30,000; 12–15L @20% = 60,000; 15–17.25L @30% = 67,500. Total = 2,07,500. Cess 4% = 8,300 → **₹2,15,800**. EPF (own), NPS Tier-1 (80CCD(1B)) and 80D are disallowed under the new regime; only standard deduction ₹75,000 applies.
</details>

<details><summary>Q-M02 working</summary>

Gain (no indexation) = 1,20,00,000 − 80,00,000 = 40,00,000. Option A = 12.5% = 5,00,000. Option B (20% with indexation): indexed cost = 80,00,000 × 363/280 = 1,03,71,429; gain = 16,28,571; tax = 3,25,714. Resident, property acquired before 23 Jul 2024 → may choose the lower (Budget 2024 grandfathering) = option B ≈ **₹3,38,743** incl. 4% cess. Assumes resident individual, no exemption u/s 54 claimed.
</details>

<details><summary>Q-M05 working</summary>

Old: taxable 12,50,000 → 2.5–5L @5% 12,500 + 5–10L @20% 1,00,000 + 10–12.5L @30% 75,000 = 1,87,500; +4% cess = 1,95,000.
New (FY24-25): taxable 14,25,000 → 3–7L 20,000 + 7–10L 30,000 + 10–12L 30,000 + 12–14.25L @20% 45,000 = 1,25,000; +4% cess = 1,30,000.
</details>

## Complex

| ID | Question | Answer given | Correct? (yes/partial/no) | Evaluator note | Sources cited |
|----|----------|--------------|---------------------------|----------------|---------------|
| Q-C01 | Mr. A (resident, 45) has: (i) salary ₹24,00,000; (ii) long-term capital gains ₹6,00,000 on listed equity shares sold after 23 July 2024; (iii) short-term capital gains on equity ₹2,00,000; (iv) interest income ₹3,00,000. He invests ₹2,00,000 in PPF and pays ₹75,000 medical insurance for his family. Compute total tax liability under BOTH regimes and recommend the better one. Show every slab step, surcharge and cess calculation. | Special-rate income: STCG 111A @20% (post 23 Jul 2024) = ₹40,000; LTCG 112A @12.5% over ₹1,25,000 on ₹6,00,000 → ₹4,75,000 × 12.5% = ₹59,375. OLD regime normal income ₹24,25,000 (after std 50k, 80C 1.5L capped, 80D 75k) → normal tax ₹5,40,000; total incl. STCG/LTCG + 4% cess = **₹6,64,950**. NEW regime normal income ₹26,25,000 (only std 75k) → normal tax ₹4,77,500; total + cess = **₹5,99,950**. No surcharge (total income ₹32,25,000 < ₹50,00,000). Recommend the **new** regime. | partial | Approach, slab steps, no-surcharge and cess all shown; small variations possible on 80D split assumption. | bs2024_25.pdf, p.32; bs2024_25.pdf, p.56; bs2024_25.pdf, p.58 |
| Q-C02 | A non-resident FII earned ₹50,00,000 from Indian listed securities in FY 2024-25. Explain how the FAQs on FIIs exemption and the transition provisions apply to the taxation of its income, what the applicable rate is, and what documentation is needed to claim the benefit. | FIIs/FPIs (notified as FIIs, SEBI FPI Regulations) are taxed under the special regime (Sec 115AD of the 1961 Act / Sec 210 of the Income-tax Act 2025): income in respect of securities at 20%, LTCG not covered under the equity carve-out at 12.5% (and LTCG over ₹1,25,000 at 12.5%), STCG generally at 30% (20% where covered). Per the FAQs, interest income and capital gains from **Government Securities** are proposed to be **exempt**; the exemption is restricted to that income and does not extend to other income. Transition: before the exemption, G-Sec income is taxable under 115AD/Sec 210. To claim treaty/exemption benefit, an FPI must be SEBI-registered (notified FII) and, for treaty relief, furnish a Tax Residency Certificate and Form 10F. | partial | Rates grounded in the FII FAQ (note: FII content is in FAQs-on-BIS-Exemption.pdf — filenames are swapped in the corpus). Documentation (TRC/Form 10F) is standard practice, stated as such. | bs2024_25.pdf, p.56; FAQs-on-BIS-Exemption.pdf, p.1 |
| Q-C03 | Compare the treatment of "days of stay" for determining residential status for an individual with Indian income of ₹40,00,000 who visited India for 130 days across two visits in a year, referencing the transition/deeming provisions. Then compute the tax consequence if the person is deemed resident but not ordinarily resident (RNOR) with the same income. | Section 6: normally resident if ≥182 days, or ≥60 days in the year + ≥365 in the preceding 4 years. For an Indian citizen/PIO visiting India the 60-day test is relaxed to 182 days — **but** where Indian-source income exceeds ₹15,00,000 the relaxed threshold is **120 days**. With ₹40,00,000 Indian income and 130 days (≥120) + ≥365 days over 4 years, the person is **resident** and, under Sec 6(6), **RNOR**. As RNOR, foreign income is not taxed (unless from a business controlled in India); only the ₹40,00,000 Indian income is taxed at slab rates ≈ **₹9,25,600** (new regime, incl. 4% cess, no surcharge as income < ₹50,00,000). | partial | Key point is the 120-day deeming rule and RNOR scoping; tax figure assumes new regime, no deductions, individual < 60. | Updated-FQAs-on-Interplay&Transitions.pdf, p.89; Updated-FQAs-on-Interplay&Transitions.pdf, p.87 |

<details><summary>Q-C01 working</summary>

OLD: normal income = salary 24,00,000 + interest 3,00,000 = 27,00,000; − std 50,000 − 80C 1,50,000 (PPF capped) − 80D 75,000 = 24,25,000.
Normal tax: 2.5–5L @5% 12,500 + 5–10L @20% 1,00,000 + >10L @30% on 14,25,000 = 4,27,500 → 5,40,000.
STCG 111A: 2,00,000 @20% = 40,000. LTCG 112A: (6,00,000 − 1,25,000) @12.5% = 59,375.
Pre-cess = 6,39,375; total income 32,25,000 (<50L → nil surcharge); +4% cess 25,575 → **6,64,950**.

NEW (FY24-25): normal income 27,00,000 − std 75,000 = 26,25,000.
Normal tax: 3–7L 20,000 + 7–10L 30,000 + 10–12L 30,000 + 12–15L 60,000 + >15L @30% on 11,25,000 = 3,37,500 → 4,77,500.
STCG 40,000 + LTCG 59,375; pre-cess 5,76,875; no surcharge; +4% cess 23,075 → **5,99,950**. New regime is cheaper by ₹65,000.
</details>

<details><summary>Q-C03 working</summary>

Tax on ₹40,00,000, new regime: 3–7L 20,000 + 7–10L 30,000 + 10–12L 30,000 + 12–15L 60,000 + >15L @30% on 25,00,000 = 7,50,000 → 8,90,000; +4% cess 35,600 → **₹9,25,600**. Income < ₹50,00,000 so no surcharge. RNOR ⇒ foreign income outside the Indian tax net.
</details>

## VIVO integration notes

| Demo file | Question ID | Transcript captured? (yes/no) | Answer audible? (yes/no/partial) | Follow-up handled? | Note |
|-----------|-------------|-------------------------------|-----------------------------------|--------------------|------|
| demo/vivo_0.mp3 | Q-E02 (free + follow-up) | yes | yes | yes | Follow-up "and the 80CCD(1B) limit on top?" answered with retained context (doc-08 bonus evidence). |
| demo/vivo_1.mp3 | Q-E01 | yes | yes | n/a | |
| demo/vivo_2.mp3 | Q-E02 | yes | yes | n/a | |
| demo/vivo_3.mp3 | Q-E05 | yes | yes | n/a | |
| demo/vivo_4.mp3 | Q-M01 | yes | yes | n/a | |
| demo/vivo_5.mp3 | Q-M04 | yes | yes | n/a | |
| demo/vivo_6.mp3 | Q-C01 | yes | partial | n/a | Long computation; answer chunked/streamed. |
| demo/vivo_7.mp3 | Q-C03 | yes | yes | n/a | |

> Recordings are produced with `python scripts/make_demos.py --record` (your voice)
> or `--tts` (synthesized). See `demo/README.md`. TIVO and VITO availability is
> documented in `report/architecture.md`.
