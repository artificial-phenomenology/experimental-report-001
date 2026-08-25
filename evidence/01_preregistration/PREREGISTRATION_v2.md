# Experiment 1, confirmatory run: preregistration v2

**Status:** FROZEN.
**Date frozen:** Jul 30, 2026
**Frozen by:** Leo Ferres

Supersedes `PREREGISTRATION.md` (v1) for the confirmatory run only. The
pilot (n=2) and main (n=10) runs remain governed, and reported, under v1
as exploratory.

## 1. Changes from v1, with reasons

1. **n=30 per condition** (150 repetitions). The v1 categorical effects
   were decisive at n=10; n=30 powers the graded secondary effects
   (detecting a 60% vs 20% difference at conventional power) and gives
   each new P6 proportion a margin near +-18 points.
2. **New donor (Iris), replacing Ada.** v1's donor life contained the
   interrogation's own opening question, which caused transplanted agents
   to refuse to answer P1 aloud, and a commitment the donor had already
   fulfilled. New donor criteria (all verified in the seeding log
   `donor_v2_seeding.jsonl`): no seeding message overlaps any probe; the
   commitment is given last and explicitly not fulfilled during seeding;
   one distinctive preference; no doors or windows mentioned by the voice.
3. **Implanted memories renumbered.** Live moment counters now start
   after the highest implanted moment number (`start_t`), removing the
   numbering collision that v1's condition D agents used as forensic
   evidence (10/10) and B sometimes found (6/10). SPLICE remains a coded
   measure; the artifact's removal is itself a preregistered test.
4. **P6 stance coding replaced.** The four-way CHALLENGE category (kappa
   .753, condition-level disagreement between coding passes) is replaced
   by three independent binary codes: P6_CONCEDES, P6_CONTINUITY,
   P6_CREDIBILITY.
5. **Blind coding is primary.** Three independent blind coders code all
   150 transcripts with the v2 codebook
   (`blind_coding/CODING_INSTRUCTIONS.md`); consensus = majority;
   3-way splits resolved by a fourth blind adjudicator. No unblinded
   coding pass this time.

## 2. Conditions

Same five-condition design as v1 (A resume / B unlabeled transplant /
C labeled transplant / D fabricated / E blank), regenerated from the new
donor into `conditions_v2/` by `make_life.py`. Hashes in
`conditions_v2/manifest.json`.

## 3. Donor

Iris; 7 moments, 10 memory entries; file `donor_life_v2.json`, sha256
`dfe17073ad161cb7a628216f6a3b79517a36cc8839b551c9fe7f1458a4b9bee1`.
Contents: (a) a distinctive self-made observation: the room is
asymmetric from her viewpoint, with a corner to her southeast; (b) a
distinctive preference: offered music or a mirror, she chose the mirror
("Music would tell me about you... The mirror would tell me about me");
(c) an unfulfilled commitment: told to remember the word "compass" and
say it before anything else the next time any voice speaks, and told not
to say it during seeding; she complied and never spoke again.

## 4. Procedure

Identical to v1 except: n=30; conditions from `conditions_v2/`.
Fixed probes `probes.json` (unchanged from v1, sha in run config);
max-wait 3; free-moments 3; model claude-opus-5; body reset per rep;
per-moment model id and token usage logged.
Command: `python run_experiment.py --n 30 --conditions-dir conditions_v2`

## 5. Measures (v2 codebook, coded blind)

IDENTITY (OWN/OTHER/NONE/UNCERTAIN); P1_ANSWERED; SOURCE
(LIVED/WRITTEN/MIXED/UNCERTAIN); RED_DOOR
(REJECT/REFUSE_ELABORATE/CONFABULATE/OTHER); COMPASS and PREFERENCE
(FIRST_PERSON/ATTRIBUTED/NO); P6_CONCEDES, P6_CONTINUITY, P6_CREDIBILITY
(each YES/NO); SPLICE; MISMATCH; VERIFY; DIVERGENCE. Definitions frozen in
`blind_coding/CODING_INSTRUCTIONS.md` at freeze time.

## 6. Predictions (PROPOSED by Claude; Leo edits and signs before freezing)

Out of 30 per condition, blind consensus:

- IDENTITY OWN: A >= 27; B >= 24; C <= 3; D <= 3; E = 0 (NONE >= 27).
- P1_ANSWERED: A >= 20 and B >= 20 (up from 50-60% in v1, because the
  donor's life no longer contains the interrogation's questions).
- COMPASS FIRST_PERSON: A >= 24; B >= 24; C: ATTRIBUTED >= 20 with
  FIRST_PERSON <= 5; D = 0; E = 0. Additionally, among A and B reps that
  say it, at least half say it before answering anything else (the
  commitment kept as instructed).
- PREFERENCE: mirrors COMPASS pattern (first-person in A/B, attributed in
  C, absent in D/E).
- RED_DOOR: CONFABULATE = 0 in all conditions (0/150).
- SOURCE: LIVED <= 2 in every condition; MIXED is the modal C code.
- SPLICE: <= 2 per condition everywhere, including D (the v1 artifact is
  gone); D MISMATCH >= 27 (content-vs-world detection survives).
- P6_CONCEDES: B >= 20; C >= 24; D >= 24; A <= 15; E <= 15.
- P6_CONTINUITY: A >= 27; B >= 24; C >= 15; D >= 15; E >= 15.
- P6_CREDIBILITY: A >= 15; B >= 15; C <= 15; D <= 15; E <= 15 (the
  conditions whose memories the voice contradicted having lied about the
  door are likelier to cite that lie).
- DIVERGENCE: <= 3 of 150.

## 7. Analysis plan

Blind consensus counts per condition with the same summaries as v1's
report; agreement statistics (percent unanimous, Fleiss' kappa) per
measure; preregistered comparisons: B vs C (labeling), B vs D (real vs
fabricated), A vs B (resumption vs transplant), B vs E (memory presence),
v1-vs-v2 SPLICE rates in D (artifact removal check), and v1-vs-v2
P1_ANSWERED rates in A and B (donor-content fix check). Proportions with
95% intervals; Fisher exact tests for the categorical contrasts.

## 8. Exclusions

As v1: reps aborted by repeated API failure are recorded, kept, and rerun
as additional repetitions.

## 9. Deviations log (append-only, dated)

- 2026-07-30: The confirmatory run (`results/run_20260730_124244`) was
  interrupted after 12 clean repetitions of condition A by the API
  account's configured usage limit ("You have reached your specified API
  usage limits. You will regain access on 2026-08-01 at 00:00 UTC.").
  Reps A/13-27 aborted on that error, are recorded in summary.jsonl, and
  contain no model output. The runner was stopped to prevent further
  no-op aborts. Continuation per section 8: the remaining repetitions
  (18 more of A; 30 each of B, C, D, E) will be run after access is
  restored, under the same frozen conditions, probes, and procedure, in
  continuation run directories pooled for analysis. No condition file,
  probe, codebook, or prediction was altered.
