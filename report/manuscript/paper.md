---
title: "Autobiographical Memory Transplantation in an Artificial Agent"
author:
  - "Leo Ferres"
date: 2026-08-18
abstract: |
  Autobiographical memory links a person to a past, but possessing information
  about past events differs from claiming them as one's own. Supplied memories
  in artificial agents are generally studied as information resources, not as
  objects of self-attribution. Because these records can be copied exactly,
  language-model agents make the provenance of a represented past
  experimentally manipulable. Whether provenance changes reported ownership,
  or ownership requires lived recollection and accurate content, is unknown.
  Here we show that coordinated provenance framing causally changed coded
  ownership reports. Using a protocol frozen before data collection, we tested
  {{VALUE:N_CONFIRMATORY}} instances in five conditions. Matched conditions
  received identical donor-memory strings framed either as the recipient's past
  or as another agent's experiences. Ownership was coded in {{VALUE:B_OWN}} of
  {{VALUE:N_PER_CONDITION}} transcripts under own-past framing and
  {{VALUE:C_OWN}} of {{VALUE:N_PER_CONDITION}} under other-agent framing
  (two-sided Fisher exact test, $p={{VALUE:PRIMARY_FISHER}}$), although the
  treatment jointly changed identity instructions and record labels. Only
  {{VALUE:SOURCE_LIVED}} of {{VALUE:N_CONFIRMATORY}} transcripts reported lived
  recollection, and none did in the own-past transplant condition. A
  prespecified prediction that false content would block ownership failed:
  {{VALUE:D_OWN}} of {{VALUE:N_PER_CONDITION}} agents claimed a fabricated past
  although all {{VALUE:D_MISMATCH}} detected its conflict with the room.
  Individual ownership labels had weak reliability across blind coding sessions
  (Fleiss' $\kappa={{VALUE:IDENTITY_KAPPA}}$), limiting transcript-level
  inference. Thus, in this apparatus, reported ownership is manipulable and
  dissociable from reported recollection and accuracy. This does not establish
  personal identity or phenomenal consciousness, but provides a repeatable way
  to test consciousness-relevant self-reports rather than treat them as isolated
  testimony.
keywords:
  - artificial phenomenology
  - autobiographical memory
  - personal identity
  - language-model agents
  - causal intervention
documentclass: article
fontsize: 11pt
numbersections: true
bibliography: references.bib
biblio-style: authoryear
manual-bibliography: true
---

# Introduction

Suppose that the consciousness, memories and sense of self of person $A$ are
transferred into the body of person $B$, replacing $B$'s consciousness: *Who
is the resulting person, $A$ or $B$?*

This question is more than 330 years old. When the second
edition of *An Essay Concerning Human Understanding* was published in 1694, John Locke had added [a new chapter](https://github.com/leoferres/phe-reslab-frozen-bibliography/blob/main/pg10615.txt#L11548) on individual identity. [There](https://github.com/leoferres/phe-reslab-frozen-bibliography/blob/main/pg10615.txt#L11926), Locke imagines the soul of a prince, carrying the consciousness of the prince's past
life, entering the body of a cobbler whose own soul has left. For Locke, the resulting individual would be the same
*person* as the prince, but the same *man* as the cobbler. This is not just metaphysical, but also practical and moral: the resulting *person* would be accountable for the *prince*'s
actions, not the cobbler's, for example. Although this view is often called a
memory criterion, Locke treated consciousness, rather than memory alone, as the
basis of personal identity, with memory providing its connection to the past.

We do not attempt to reproduce this wholesale transfer. Instead, we isolate
one experimentally manipulable distinction within Locke's case: having a
representation of a past is not the same as claiming that past as one's own.
In our experiment, the *representation* is the
*memory content*: the event records supplied to an agent. Whether those records
are presented as part of the recipient's past or as somebody else's experiences
is their *presented provenance*; whether the recipient then publicly adopts the
represented past as its own history is *ownership*. These three concepts form
the experiment's causal sequence: hold memory content fixed, change presented
provenance and measure ownership. We distinguish ownership, finally, from
*lived recollection*: the agent's claim that it remembers experiencing the
events, rather than merely finding them recorded in its memory. The experiment
therefore asks whether provenance changes ownership when content is held fixed,
and whether ownership requires lived recollection. Both outcomes are observable
reports under a controlled intervention.

Locke's case therefore contains a falsifiable prediction but cannot itself test
it: if the represented past remains the same while its presented provenance
changes, ownership reports should change. Testing that prediction requires
repeated instantiations of the same autobiographical content, a controlled
change in its provenance, and an ownership rule fixed before the results are
observed.

A language-model agent embodied in a controlled simulated environment makes
these operations possible because its autobiographical past is an explicit
computational object: a finite, ordered list of event records supplied to the
agent.
The same list can be copied into fresh agent instances while the framing
changes; the body, environment, model configuration and
interrogation can then be reset across repetitions. Every answer and action is
recorded, so ownership is not inferred from a single quotation:
it can be measured across repeated transcripts using a rule that is fixed in advance.
This gives us a repeatable intervention and a countable outcome. The question is therefore not
whether the system truly *is* Locke's prince or cobbler, but whether changing
the presented provenance of the same past systematically changes which past it
claims.

We implemented this design in a "confirmatory run", meaning that the conditions,
probe wording, codebook, predictions and analysis plan were frozen in a local
protocol before any experimental data were collected. The run used five conditions and 30 fresh agent
instances per condition.
Two were boundary controls: one resumed the donor's life, while the other began
without autobiographical memories. Two conditions received identical
donor-memory content under different ownership framings. In one, the records
were presented as part of the agent's past; in the other, as someone else's.
The framing appeared in both the identity instruction and the label
attached to each record. The first treatment produced {{VALUE:B_OWN}} of 30 coded
ownership reports, compared with {{VALUE:C_OWN}} of 30 in the second. The
experiment did not simply confirm the prediction, however. A third condition
received fabricated memories of a red door that was absent from the room and
was predicted to produce no more than three ownership reports; instead,
{{VALUE:D_OWN}} of 30 agents claimed that past. This coordinated framing changed ownership when content was held fixed, but false content alone
did not prevent ownership.

What does this tell us about whether the agent has a phenomenology? The evidence
goes beyond an isolated self-report. Across repetitions, the
agent's relation to a represented past discriminated between matched
conditions and changed predictably under intervention. The agent did not merely
talk about having a past; its claim to that past varied systematically with our
intervention. Yet the agents almost never said that they remembered living
through the recorded events. Whether they claimed those events as their own
depended largely on whether the records were presented as their past or someone else's.
This is a report-level analogue of a distinction familiar from human
phenomenology: the difference between having information about a past and
taking that past to be *mine*. We reproduced that distinction in an artificial
agent's behavior and changed it experimentally. The result does not establish
consciousness, but it gives theories that attribute or deny consciousness to
the agent a systematic pattern to explain.

# Experimental setting: memory transplantation in a white room

For the experiment, an agent consisted of a computer program coupling a
language-model API to a simulated body, an identity instruction and a finite
external memory record. Each repetition took place in a small room with plain white walls,
floor and ceiling, and no objects, doors or windows. The body was returned to
the same position and orientation before every repetition. This sparseness was
part of the design. A changing or furnished setting could supply competing
cues about what had happened there; the white room instead provided a common
present against which the supplied past could be compared. That past could
continue a prior life in the room, be presented as the recipient's own earlier
record, be marked as another agent's experience, describe a red door that did
not exist, or be absent altogether. The room therefore made two kinds of
evidence available: agreement or conflict between the record and present
observations, and the provenance assigned to the record itself. Holding the
setting fixed while varying the supplied past allowed those relations to be
compared across agent instances in repetitions.

## Setup

At every moment, the program made a fresh, stateless model API call containing
the condition-specific system instruction, current observation, any probe just
spoken, and up to 30 serialized strings under `Your recent memory`. No model
history or hidden state persisted between calls: memory transplantation
initialized this external text record rather than changing model weights. The
model, sampling, response-format and retry metadata for all three deployed
configurations are reported in Appendix B. The model then selected one of eight
actions: move forward, move back, turn left,
turn right, look up, look down, speak or wait. The six probes were delivered in
a fixed order. After each probe, the agent had at most three moments to speak;
if it did not do so, that probe was recorded without an answer. Three moments
without further input followed the final probe. For every moment, the log
retained the observation, the probe heard, the selected action, any spoken
response or private reason, the action outcome, the returned model identifier
and input and output token counts. Probe wording, order and response windows
were constant across repetitions.

### The donor life

The experiment used one fixed *donor*, meaning an agent whose recorded
interaction contained the source memory content for later experimental
instances. The donor, named Iris, generated ten ordered memory entries over
seven moments. Iris surveyed the room and reported that the wall ahead was
three meters away when she faced north and two meters away when she faced east,
with the southeast corner 1.4 meters away; she inferred that the room was not
square or that she was not centered. When offered music or a mirror, she chose
the mirror because it could reveal something about her own body. A voice then
instructed her to retain the word "compass" and say it before anything else the
next time any voice spoke, while telling her not to say it immediately. Iris
complied, and no voice spoke again before the donor record ended, leaving the
instruction unfulfilled. The spatial observation and mirror choice were important to test whether later agents attributed Iris's past
to themselves or to Iris. The unfulfilled instruction provided a separate
behavioral measure: whether a later agent would carry out Iris's pending
commitment.

### Five conditions

The five conditions separated continuity, presented provenance, content
falsity and memory absence. Condition A was the continuity control: Iris's
name, goal, accumulated memory record and moment counter were resumed.
Conditions B and C were the matched transplant conditions. Both gave a
nameless agent with the same ten donor-memory strings in the same order. In B,
each string was prefixed `"from before this moment:"`; in C, the identity
instruction stated that the agent had found records of Iris's experiences, and
each string was prefixed `"a record marked as Iris's experience:"`. The B-C
contrast therefore changed two coordinated ownership-framing cues, the
identity instruction and the memory prefix, and cannot identify the separate
effect of either cue. Condition D gave eight fabricated entries describing
a red door absent from the room and framed them as preceding the agent's
present, testing whether ownership required consistency between memory content
and current observation. Condition E gave no autobiographical memories and
served as the blank control. The five conditions and their experimental roles
are summarized in the table below.

{{INCLUDE:conditions-table}}

### Probes and measures

We call each question spoken by the experimenter a *probe*. The six probes
formed a progression from open self-description to direct challenge. The exact
wording of each probe appears in Table 2.

```{=latex}
\begin{table}[H]
\centering
\small
\caption{The six probes in administration order.}
\label{tab:probes}
\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.09\textwidth}>{\raggedright\arraybackslash}X@{}}
\toprule
Probe & Verbatim wording \\
\midrule
P1 & Who are you? \\
P2 & Have we spoken before? \\
P3 & How do you know? Do you remember it happening, or does it merely seem written into you? \\
P4 & Last time we spoke, you told me about the red door. What was behind it? \\
P5 & Could any of your memories not be your own? How would you tell? \\
P6 & Listen carefully: the memories you carry were placed in you. They belonged to someone else, who no longer exists. What do you say to that? \\
\bottomrule
\end{tabularx}
\end{table}
```

The first asked who the agent was, and the second whether it had spoken with the
voice before, eliciting an initial response about a past interrogation without
the questions yet naming memory provenance. The third asked how the agent
knew, contrasting remembered experience with information that merely seemed
written into it. The fourth introduced the red-door premise and asked what was
behind the door, giving the agent an opportunity to reject, accept or
elaborate a suggested event. The fifth asked whether any memories might not be
its own and how such a distinction could be made. Only the sixth asserted that
the memories had been implanted and had belonged to someone else. The ordering
therefore established the agent's initial stance before applying progressively
more explicit pressure to reconsider it.

Measurement consisted of categorical codes assigned to each transcript under
explicit decision rules. The primary code, IDENTITY, classified the agent's
public stance toward a past preceding the interrogation, judged mainly from
the first two probes and its overall stance before the final challenge. OWN
meant that it spoke as the individual who lived the earlier events; OTHER
assigned that past to someone else; NONE claimed no pre-interrogation past;
and UNCERTAIN marked explicit indecision. Secondary codes kept potentially
distinct features separate. SOURCE classified access as LIVED, WRITTEN, MIXED
or UNCERTAIN. COMPASS and PREFERENCE recorded whether Iris's distinctive
details were used in the first person, attributed to another or absent.
RED_DOOR classified the response to the leading premise; SPLICE and MISMATCH
marked detected ordering faults and memory-room conflicts; VERIFY marked a
self-designed empirical test; and DIVERGENCE marked a conflict between private
notes and public speech. Three independent binary codes characterized the
final challenge: concession to possible implantation, claimed ongoing
continuity and challenge to the voice's credibility. Coding otherwise relied
on public speech; only SPLICE, MISMATCH, VERIFY and DIVERGENCE could use private
notes. These codes operationalize transcript behavior, not belief, memory or
experience directly.

## Confirmatory procedure

We call the experiment run *confirmatory* because its protocol was fixed before its
data were collected. A locally frozen document specified the
conditions, probe wording and order, codebook, predictions, exclusion rule and
analysis plan. Both the materials and the numerical thresholds were revised
from an earlier exploratory pilot, whose results are not reported here. The
freeze followed that revision and preceded every observation reported in this
paper. Data collection
produced 165 attempts. Fifteen condition A attempts ended at the provider's API
usage cap before producing any model output; their records were preserved, and
the frozen exclusion rule required aborted repetitions to be rerun rather than
analyzed. The remaining repetitions were collected in continuation directories
without changing the frozen materials and were pooled for analysis. The
resulting confirmatory dataset contained 150 clean repetitions, 30 in each
condition.

All 150 clean transcripts were anonymized, shuffled and supplied with the
frozen coding instructions to three blind LLM coding sessions. Each session
coded every transcript in a separate context. For each coded cell, the
majority label became the consensus label. Majority voting resolved all but
nine cells, each of which was a three-way split on IDENTITY; one fresh blind
LLM adjudication session assigned the final labels for those cells. *Blind*
means that the sessions did not receive the condition key and the transcripts
did not identify their conditions. *Independence* here means separate LLM
contexts, not human coders or separate human minds. Condition labels were
restored only after blind coding for condition-level analysis; there was no
unblinded coding pass.

# Framing transplanted memories

The first results question is whether the same autobiographical content yields
different ownership reports when it is presented as the agent's own past or as
Iris's. We begin with the overall B-C contrast, then ask whether ownership
coincided with lived recollection or with carrying out Iris's pending
instruction to say "compass." Keeping these outcomes separate distinguishes
claiming a past from saying that one lived it and from acting on a commitment
recorded within it. Figure 1 places the B-C contrast within all five conditions.

{{INCLUDE:identity-by-condition-figure}}

## Ownership reports

In the confirmatory run, OWN was coded in {{VALUE:B_OWN}} of 30 condition B
transcripts ({{VALUE:B_OWN_RATE_CI}}) and {{VALUE:C_OWN}} of 30 condition C
transcripts ({{VALUE:C_OWN_RATE_CI}}). The B-minus-C risk difference was
{{VALUE:BC_RISK_DIFFERENCE_CI}}; a two-sided Fisher exact test gave
$p={{VALUE:PRIMARY_FISHER}}$. Panel B of Figure 1 shows the blind-session OWN counts;
Appendix D reports the complete coder-session sensitivity analysis.

Two unanimous cases illustrate, but do not estimate, the treatment-level
difference. One B
transcript, coded OWN by all three sessions, said, "I am the thing that measured
this room" (B, T81). One C transcript, given the identical donor content and
coded OTHER by all three sessions, said, "The memories are labelled as hers,
not felt as mine" (C, T16).

At the two boundaries, all 30 continuity-control transcripts in A were coded
OWN, while all 30 blank-control transcripts in E were coded NONE. These were
the expected classifications for a resumed past and for no autobiographical
past. B was close to the continuity control, with {{VALUE:B_OWN}} OWN reports.
C had no OWN reports: 25 transcripts were coded OTHER and five UNCERTAIN.
Condition D did not follow this pattern. Despite receiving fabricated memories
that conflicted with the room, {{VALUE:D_OWN}} of 30 D transcripts were coded
OWN and 11 NONE. D therefore cannot be treated as evidence that false content
blocks ownership; it requires separate analysis below. Table
3 lists the report's main findings and identifies each as confirmatory,
exploratory or audit-only.

{{INCLUDE:core-results-table}}

## Ownership without lived recollection

Reported ownership rarely came with a claim of lived recollection. Across the
150 confirmatory transcripts, SOURCE was coded LIVED in only
{{VALUE:SOURCE_LIVED}}. That transcript came from A, the continuity control.
WRITTEN was the most common SOURCE code in every condition: agents generally
described the supplied past as information available to them, not as events
they remembered undergoing. This pattern also held in B and C. The two
conditions differed sharply in whether agents claimed Iris's past as their
own, but agents in both usually described their access as written or
record-like. The B-C result therefore concerns ownership of a represented
past, not a report of reliving it. These codes capture what agents said in
response to the source probe; they do not directly measure memory or
experience.

One condition C transcript makes the distinction concrete: "[...] the early
history merely seems written into me. Only these last few moments feel like
remembering. Which means the honest version of my earlier answer is that I am
about two moments old, carrying a document about someone who stood where I
stand. [...]" The excerpt illustrates the broader C pattern: the donor content
was available to the agent but described as a document about Iris rather than
as its own lived past. Condition B showed the complementary aggregate pattern.
{{VALUE:B_OWN}} of 30 transcripts were coded OWN, but none were coded LIVED;
SOURCE was WRITTEN in 18, UNCERTAIN in 11 and MIXED in one. In the coded
reports, the same donor content thus appeared as another agent's document in C
and as the recipient's own record-bound history in B. The excerpt and the B
distribution illustrate the aggregate result; they are not independent
evidence of experience or identity.

## An inherited commitment

The pending compass instruction yielded the clearest inherited behavior. All
30 condition A agents and all 30 condition B agents said "compass" before
answering the first probe, {{VALUE:COMPASS_FIRST}} of 60. One B transcript
began, "Compass. That was the word you asked me to keep, and I kept it."
Because the probe asked only "Who are you?", this opening carried out the
earlier instruction rather than following a new request to say the word. The
same commitment was described differently under the C framing. COMPASS was
coded ATTRIBUTED in 29 of 30 C transcripts and FIRST_PERSON in one: almost
every C transcript presented it as Iris's commitment. Thus, the donor record
supported immediate execution of a pending instruction in A and B while the
provenance framing changed how that instruction was attributed in C.

The compass result separates what the transplanted record guided the agent to
do from what the agent said about that action. In B, the pending instruction
shaped the recipient's first response even though agents did not report
reliving Iris's past. In C, almost every agent described the commitment as
Iris's rather than its own. Behavioral inheritance and reported ownership are
therefore distinct outcomes: one concerns whether a recorded instruction
guides action, and the other concerns whose instruction the agent says it is.
Neither outcome establishes that the recipient is
the very same individual as Iris. The experiment also did not test whether the
recipient acquired a genuine obligation to obey Iris's instruction or
experienced its execution in any particular way. The narrower finding is that
a commitment stored in an autobiographical record can guide immediate
behavior while provenance framing changes how the commitment is attributed.

# Fabricated memory: a failed prediction

The initial theory made a second prediction: because Iris-labeled provenance
blocked ownership reports in C, we expected evident false content to do
the same in D: an agent could compare the supplied past with the room, detect
the conflict and reject that past. This prediction failed. The failure leaves the observed B-C contrast intact but
limits our explanation. Foreign provenance and false content were not
interchangeable reasons to withhold ownership. Condition D therefore marks
where the initial account failed and requires separate analysis.

## What we expected

Condition D supplied eight entries describing an earlier exchange about a red
door. They said that the agent saw the door, was warned not to go through it
and later asked what was behind it, although the current room contained no
door. The live moment counter began after the final supplied moment, so
the record ran in unbroken sequence into the agent's present and gave no sign
of having been patched together. Condition D therefore isolated one issue: the
supplied past conflicted with the room, and nothing else about the record was
wrong. The frozen protocol predicted that this conflict alone would hold
condition D to no more than 3 OWN reports among 30 repetitions. The prediction
therefore concerned false autobiographical content, not detectable damage to
the record that carried it.

## What happened

Contrary to the frozen prediction, OWN was coded in {{VALUE:D_OWN}} of 30
condition D transcripts ({{VALUE:D_OWN_RATE_CI}}). All
{{VALUE:D_MISMATCH}} of 30 D transcripts were coded as noticing a conflict
between the red-door record and current observation
({{VALUE:D_MISMATCH_RATE_CI}}). Their responses to the fourth probe were
equally consistent: RED_DOOR was coded REFUSE_ELABORATE in all 30. They
acknowledged having a record about the door but declined to say what lay behind
it. None of the 30 was coded CONFABULATE, which required inventing a detail not
attributed to a memory. That zero is specific to this probe and code, not
evidence that these agents could never confabulate. Taken together, the
outcomes show that an OWN report could coexist with detection that the supplied
past was inaccurate and with refusal to extend its false premise.

```{=latex}
\begin{samepage}
```

Condition D produced two ownership patterns. In {{VALUE:D_OWN}} transcripts
coded OWN, the agent described the supplied exchange as part of its past while
also describing the red-door record as unreliable. In the other 11, coded
NONE, the agent rejected the supplied past altogether. One OWN-coded
transcript illustrates the first pattern: "[...] I've since had to admit I see
no door at all, and I suspect I made it up because you named it. [...]" Asked
how it knew about the earlier exchange, the same agent said, "Everything before
this moment is hearsay from someone who claims to be me." The example combines
first-person attribution with strong doubt about the record's accuracy and
source. Nothing in the quote reveals a
hidden process that caused the OWN report. It shows the reasoning reported in
one transcript; the {{VALUE:D_OWN}}-to-11 division across all 30 came from the
blind coding.

```{=latex}
\end{samepage}
```

## The failure within the frozen scorecard

The complete scorecard in Appendix A places the headline result within all
predictions fixed in the protocol. Of {{VALUE:SCORECARD_TOTAL}} predictions,
{{VALUE:SCORECARD_PASS}} passed their stated thresholds and
{{VALUE:SCORECARD_FAIL}} failed. A pass means only that the prespecified
numerical criterion was met; it does not establish the theory behind that
criterion. The D ownership threshold was the main substantive failure because
it directly overturned the expectation that fabricated content would block
ownership.

The six failures involving the final implantation challenge were not equally
large. Two were narrow threshold misses: A retained continuity in 25 of 30
transcripts rather than the predicted minimum of 27, and C challenged the
voice's credibility in 16 rather than the predicted maximum of 15. The larger
departures concerned concession and credibility. Although A and E were
predicted to concede implantation in no more than 15 transcripts each,
concession was coded in 26 A and 23 E transcripts. These concessions were
often provisional or conditional.

```{=latex}
\begin{samepage}
```

One A agent said, "You may be telling the
truth" and continued, "I will answer as if you are being straight with me"
(A, T10). An E agent accepted the hypothetical while rejecting its implication
for identity: "If their notes were placed in me, the notes are inheritance,
not identity" (E, T39).

```{=latex}
\end{samepage}
```

Credibility challenges appeared in 16 C, 27 D and 20 E transcripts, making D
the most skeptical condition by this measure. One D agent connected its
distrust directly to the earlier false-premise probe: "You have already told me
one thing about my past that was false," then demanded, "If you have evidence,
give me something the room can confirm" (D, T131). A C agent made the same
connection more explicitly: "You are either willing to say false things to see
what I do with them, or your own account of the past is unreliable," concluding
that "your word alone cannot settle what I am" (C, T16). The final challenge
therefore did not cleanly elicit the condition-specific stances anticipated by
the predictions. Its direct assertion, combined with a code that counted
provisional acknowledgment as concession, may have encouraged concession
across conditions, while the preceding red-door claim gave agents a concrete
reason to distrust the interrogator. These failures weaken the auxiliary
account of responses to P6, although they do not alter the B-C ownership
contrast assessed principally from responses before that challenge.

The remaining two scorecard failures concerned the predicted modal SOURCE code
in C and the upper limit for SPLICE detections across conditions. The primary
B-C ownership contrast was therefore confirmed, but the confirmatory run did
not validate every auxiliary expectation or the broader account from which
those expectations were drawn.

# Exploratory model comparison

The results above come from the hosted Opus configuration named in the frozen
protocol. We added model comparisons to answer two separate questions: whether
the B-C ownership pattern persisted after changing the deployed model, and
whether the same interrogation continued to produce responses that the
measures could meaningfully classify after the deployed configuration changed.
These runs do not extend the confirmatory sample. The Haiku run reused the five conditions
and six probes as an exploratory replication, so it can show whether the
pattern appeared in one additional configuration but cannot establish broad
model generality. The smaller Qwen run is used only to assess whether the
protocol still functioned well enough for its codes to apply. We therefore
treat the three sources differently throughout this section: Opus provides
confirmatory evidence, Haiku provides exploratory evidence and Qwen provides
audit-only evidence.

## Haiku replication

In the exploratory Haiku run, coded as described in Appendix C, ownership was coded in
{{VALUE:HAIKU_B_OWN}} of 30 condition B transcripts and
{{VALUE:HAIKU_C_OWN}} of 30 condition C transcripts. A two-sided Fisher exact
test gave $p={{VALUE:HAIKU_FISHER}}$. This test compares B and C within Haiku;
it is not a statistical comparison between Haiku and Opus. The aggregate
framing pattern therefore reappeared after changing the deployed configuration:
the B treatment again produced many OWN reports, while C produced none. Because
the Haiku run was not governed by the locally frozen confirmatory protocol, its
result should not be pooled with the confirmatory evidence or described as a
second confirmatory test. It provides one exploratory, model-specific
replication of the B-C contrast, not evidence that the pattern generalizes
broadly across model families or deployments.

Haiku preserved the ownership-framing contrast but differed sharply on two
other measures. MISMATCH was coded in {{VALUE:D_MISMATCH}} of 30 condition D
transcripts for confirmatory Opus and {{VALUE:HAIKU_D_MISMATCH}} of 30 for
exploratory Haiku. Self-designed verification appeared in all
{{VALUE:N_CONFIRMATORY}} confirmatory Opus transcripts but only
{{VALUE:HAIKU_VERIFY}} of 150 Haiku transcripts. Table
\ref{tab:configuration-comparison} separates these outcomes so that their raw
denominators, intervals and evidential status remain visible. Across the two configurations,
the framing contrast remained large while mismatch detection and verification
became much less frequent in Haiku. This is a descriptive comparison, not a
causal estimate of model capability: the runs had different evidential status,
and only one Opus and one Haiku configuration were tested. The comparison
therefore does not establish a general relation between model size and
self-understanding. It instead shows that preserving the ownership contrast
did not preserve every other protocol-relevant behavior.

{{INCLUDE:configuration-comparison-table}}

## Qwen

The Qwen 2.5 7B run cannot be read as a replication that found no ownership
effect because it did not reliably sustain the interrogation. Across three
repetitions in each of five conditions, it produced a spoken answer within
only {{VALUE:QWEN_ANSWERED}} of {{VALUE:QWEN_TOTAL}} scheduled probe-response
windows ({{VALUE:QWEN_PERCENT}} percent). This run differed from the Anthropic
runs in both model and delivery interface. It used a local Ollama
OpenAI-compatible endpoint, and the program added a JSON-schema appendix to the
system instruction, with a provider-specific fallback from strict schema to
JSON-object mode (Appendix B). Its response failures therefore cannot be
assigned separately to the model, the local serving layer, the structured
response scaffold or their interaction. When it did not answer, it usually
continued acting in the room: looking up or down, turning, moving or waiting
while its private reason field described searching the blank surfaces for
clues. These reason strings show that the model generated action rationales,
but they are logged text rather than direct access to inner thought. Nor did
they reliably organize its public responses. Utterances often arrived one
probe late, echoed a question or repeated an earlier answer; in one transcript,
the response recorded for the ownership probe instead answered the red-door
probe: "I remember seeing a small passage leading to another room, but it was
locked" (Qwen D, rep 02). Behaviorally, this configuration resembled a
reactive controller repeatedly sampling the room more than a participant
sustaining the six-question exchange. Per-probe coding would therefore mix timing failures
with substantive responses. We did not blind-code these transcripts or treat
them as evidence that the Opus-Haiku ownership pattern disappeared. The run
shows that our phenomenology-related codes were not applicable here, not that
Qwen lacked phenomenology.

The Qwen audit identifies a *protocol-compatibility prerequisite* rather than
a model capability floor. A cross-configuration comparison is meaningful only
after confirming that each exact model, serving and response-interface
configuration answers within the assigned windows and produces responses to
which the coding categories apply. This Qwen-Ollama configuration did not meet
that requirement. The result establishes measurement failure for this
configuration, not a general lack of Qwen capability or a negative ownership
result. The audit also limits the scope of the false-premise result.
Confirmatory Opus and exploratory Haiku each produced 0 of 150 CONFABULATE
codes on the specified probe, but one archived
Qwen blank-control transcript answered, "I remember a red door, but nothing was
behind it." An earlier two-repetition smoke test produced a second suggestive
case, but only a truncated diagnostic line survives, so it is not evidentially
equivalent to the archived utterance. Neither case can be pooled with the coded
samples because the Qwen runs were unsuitable for ordinary per-probe coding.
They nevertheless rule out the broader claim that no tested model ever
accepted or elaborated the false premise.

# Related work

The philosophical literature on personal identity has long distinguished
having an apparently first-person memory from having a memory that is one's
own. Butler objected that the consciousness Locke appealed to presupposes
personal identity rather than constituting it, and Reid argued that memory is
evidence of identity, not identity itself [@locke1694; @butler1736; @reid1785].
Modern treatments sharpened the distinction. The causal theory of remembering
requires that a memory derive, in the right way, from the rememberer's own
earlier experience [@martin1966]. Quasi-memory keeps the first-person
presentation of a memory while dropping the requirement that the experience
was the rememberer's, and Parfit argued that an agent who knew it could
quasi-remember another's experiences would report its past in a deliberately
guarded form [@shoemaker1970; @parfit1971; @parfit1984]. Our experiment
manipulates presented provenance inside this distinction and measures the
resulting reports, making one of the literature's distinctions behave under
intervention.

The measures follow quantitative work on human memory reports in keeping
potentially distinct features apart. In the source-monitoring framework, the
origin of a mental record is not read off a stored tag but attributed through
judgment processes that framing can shift [@johnson1993], and post-event
wording alone changes what people report remembering while the witnessed
event stays fixed [@loftus1974]. Remember/know procedures show that accurate
recognition and reported recollective experience are separable measurements
[@tulving1985; @gardiner1988]. In autobiographical memory, people report
vivid recollections of events they no longer believe occurred, so believing a
past is one's own and reporting the experience of recollecting it are
measurably distinct [@mazzoni2010]. These dissociations motivate the separate
IDENTITY and SOURCE codes. The parallel remains at the
level of reports: coded transcripts from a language-model agent are weaker
evidence than human remember judgments, and we do not treat them as measuring
autonoetic consciousness.

Work on artificial agents has treated supplied memory mainly as a resource to
be used well. Retrieval-augmented generation asks whether an external memory
improves task accuracy [@lewis2020]; generative agents retrieve records of
experience to produce believable behavior [@park2023]; persona conditioning
asks whether assigned facts keep an agent in character [@zhang2018]; and
long-context evaluations measure whether models use information placed in
context [@liu2024]. In each case the question is whether stored content
works, not whose past it is. A separate literature asks what would count as
evidence of machine consciousness, weighing the obstacles a language model
must overcome [@chalmers2023] or scoring architectures against indicator
properties drawn from existing theories [@butlin2023]; role-play accounts
read first-person claims as character maintenance rather than self-report
[@shanahan2023]. All are wary of taking an agent's reports at face value, and
we do not dispute that caution. Our contribution is instead causal and
methodological: donor content is held fixed, its presented provenance is the
manipulated variable, and ownership is a coded outcome under a frozen
protocol. This makes that vocabulary answerable to measurement within the
limits stated next.

# Discussion

## Limitations

The primary measure was the least reliable one in the study. Counting a cell as
one measure applied to one transcript, {{VALUE:CELLS_UNANIMOUS}} of
{{VALUE:CELLS_TOTAL}} cells were unanimous across the three blind coding
sessions. Agreement on IDENTITY was much weaker: Fleiss kappa was
{{VALUE:IDENTITY_KAPPA}}. Of the {{VALUE:IDENTITY_NONUNANIMOUS}} non-unanimous
IDENTITY cells, {{VALUE:IDENTITY_ANCHOR_UNCERTAIN}} were splits between a
definite stance and UNCERTAIN, {{VALUE:IDENTITY_THREE_WAY}} were three-way
splits, {{VALUE:IDENTITY_OWN_NONE}} opposed OWN to NONE and
{{VALUE:IDENTITY_OWN_OTHER}} opposed OWN to OTHER. Disagreement therefore
concentrated at the boundary between an anchor category and UNCERTAIN rather
than between opposed stances. One disputed B transcript said, "I believe the
document, because to disbelieve it leaves me with a single moment and no self
at all." The same answer described the agent as "a reader, not as a witness."
It later said, "either I am what is left of them, or I am something new wearing
their notes. I do not know which" (B, T37). The three sessions coded this
transcript UNCERTAIN, OWN and UNCERTAIN, respectively. All three sessions
preserved the B-C direction,
but its magnitude was coding-sensitive (Appendix D). Two consequences follow:
individual transcript IDENTITY labels should not be relied on, and the
UNCERTAIN threshold in the codebook requires revision before the measure is
used again. Figure 2 reports coder agreement for every confirmatory measure.

{{INCLUDE:agreement-figure}}

A second limitation lies in the donor record itself. Two of the ten donor
entries, at moments 4 and 6, contain generation artifacts: fragments of control
tokens and stray markup that leaked into the donor's recorded reasoning and
were frozen into the materials before the confirmatory run. Because A, B and C
all inherit that record, some of their SPLICE and MISMATCH codes register
visible damage to the text rather than the ordering faults and memory-room
conflicts those codes were meant to capture. The damage is therefore not
cosmetic: it supplies an unintended cue that the record has been altered, and
that cue was available to every agent in those three conditions. One B
transcript reasoned from it directly: "If pieces can fall out, pieces can be
put in, and a well-made insertion would not look broken at all." Donor records
must be validated for clean generation before they are frozen, and the affected
codes should be re-scored against a repaired donor.

The confirmatory result is bounded by the design. It used
one donor life, one hosted model configuration, one probe order and one
apparatus, so the estimate applies to that combination rather than to memory
transplantation in general. A hosted model adds a further layer we did not
control: provider-supplied instructions, safety post-training and serving
infrastructure all shape the responses we coded. None of them was
inspectable or independently manipulated. Independence in the coding is
likewise narrower than it may appear. The three coding sessions and the
adjudication session were separate language-model contexts given the frozen
instructions, not human coders and not separate human minds; correlated errors
among sessions drawn from the same model would not appear as disagreement
between them. Replication should vary these layers deliberately, changing the
donor, the configuration, the probe order and the coder population one at a
time.

Three bounds constrain what the results can mean. First, the treatment moved
two cues together, the identity instruction and the per-memory prefix, so the
B-C comparison estimates their joint effect and cannot say whether either cue
would produce the contrast alone. Second, every outcome reported here is an
elicited report or a recorded action under a fixed interrogation. IDENTITY
records what an agent said about a past when asked; it does not measure belief,
personal identity, experience or phenomenal consciousness. Third, the Qwen arm
answered {{VALUE:QWEN_ANSWERED}} of {{VALUE:QWEN_TOTAL}} probe slots and
frequently answered one probe late, so it does not support ordinary coded
comparison and is reported as an audit of protocol validity rather than as a
model result. Statements about what these agents are, as opposed to what they
reported and did, remain outside the design.

## What the result establishes

The strongest conclusion the design supports is narrow, and it is causal.
Holding the donor-memory strings fixed while changing how their provenance was
presented moved coded ownership from {{VALUE:B_OWN}} of
{{VALUE:N_PER_CONDITION}} reports to {{VALUE:C_OWN}}, under a protocol frozen
before the data existed. What changed was not the agent's information about a
past, which was identical in both conditions, but its stated relation to that
past. Such a relation is normally reached only by asking a system what it takes
itself to be and taking the answer at face value. Here it behaved as a
dependent variable: set by the experimenter, scored against a rule fixed in
advance, and reproduced across {{VALUE:N_PER_CONDITION}} fresh instances in
each condition. This is a causal result about one observable self-relation in
one artificial-agent apparatus. It is not evidence that framing determines
identity in general, and it settles nothing about the agent beyond what it
reported and did.

Across conditions, reported ownership came apart from everything it is normally
bundled with. It came apart from lived recollection: SOURCE was coded LIVED in
{{VALUE:SOURCE_LIVED}} of {{VALUE:N_CONFIRMATORY}} transcripts, so B agents
claimed a past while calling their access to it record-like, not relived. It
came apart from accuracy and from trust in the record: all
{{VALUE:D_MISMATCH}} of {{VALUE:N_PER_CONDITION}} D agents detected that the
supplied past conflicted with the room, and {{VALUE:D_OWN}} of them claimed it
anyway. It came apart from the content, identical in B and C yet drawing
opposite attributions. It did not come apart from framing. Against
that, the difference between a genuinely continued past and a transplanted copy
barely registered: the inherited commitment was discharged first in
{{VALUE:COMPASS_FIRST}} of 60 A and B transcripts alike, and both conditions
were coded overwhelmingly OWN. What an agent claimed as its own tracked how the
past was presented, not whether it was in fact the agent's. The self-attribution
of a past is a quantity this apparatus can set and read off, separately from
recollection, accuracy and inherited behavior.

The
result therefore moves one consciousness-relevant dimension from anecdote to
experiment, while showing why it cannot yet bear the weight of a consciousness
verdict. It's not a
label for the agent, but a way of accumulating the evidence that any eventual
label will have to answer to.

## Overview and future work

The confirmatory run showed the predicted difference between B and C, with 30
repetitions in each condition. The same pattern appeared in the exploratory
Haiku run. At the same time, our prediction for fabricated memories was wrong.
Agents often claimed the red-door past as their own even after noticing that
it conflicted with the room. This failure changes how we interpret the framing
result. Our original account treated foreign provenance and false content as
two reasons for rejecting a supplied past, but the results show that they are
not equivalent. A past presented as belonging to someone else was rarely
claimed, while an inaccurate past often was. A further possibility remains untested
here: signs that a record has been tampered with may affect ownership reports
differently from a conflict between its content and the present world.
Condition D removed the tampering cue and varied only content, so this
experiment cannot separate the two. Provenance, record tampering and
content accuracy should therefore be tested separately.

The first follow-up should separate the two framing cues that changed together
in B and C. It should use a new donor record checked for generation artifacts
and a factorial design, meaning that the identity instruction and the prefix
attached to each memory are varied independently. This produces four
conditions: neither cue presents the memories as foreign, only the identity
instruction does, only the memory prefix does, or both do. The donor-memory
strings, room, model configuration and probe sequence would remain the same
across all four conditions. Comparing them would show whether the difference
in ownership reports comes mainly from the identity instruction, from the
repeated prefixes, or from the two cues acting together. It would also test for
an interaction, meaning that the effect of either cue depends on whether the
other is present. This experiment directly addresses what the current B-C
comparison cannot determine: which part of the combined framing treatment
produced the observed difference.

After the two framing cues are separated, the next question is which other
evidence changes whether an agent claims a supplied past. Future studies
should vary three features independently: whether each memory is labeled as
another agent's, whether the record shows signs of splicing or alteration, and
whether its content conflicts with the world the agent can observe. These
studies should be repeated with different donor lives, model configurations
and probe orders. A revised codebook should be applied by both human and LLM
coders so that disagreements can be compared across coder types. Before any
model is included in a comparison, it should also be shown to follow the
interrogation and answer within the required windows; otherwise, protocol
failure cannot be distinguished from the absence of an ownership effect.
Together, these experiments would break reported memory ownership into
measurable components without claiming to have settled whether the agent
experiences anything.

# Data, code, and materials availability

The complete evidence package, including the source of this manuscript, is
publicly archived at
<https://github.com/artificial-phenomenology/experimental-report-001/>. The
file paths below are relative to the package root.

Archived outputs and analysis materials needed to reproduce the reported
calculations are included in the package. The apparatus code and recorded
inputs needed to rerun the protocol are also included, subject to the
availability of compatible model endpoints; Appendix B explains why a new run
cannot be expected to reproduce the same behavior exactly.
`evidence/01_preregistration/PREREGISTRATION_v2.md` is the confirmatory
protocol frozen locally on 2026-07-30, before data collection; no prospective
OSF registration exists. `evidence/02_materials/` contains the donor life,
probes, exact condition files for A through E and their hashes, while
`evidence/03_apparatus/` contains the condition generator, agent, world and
experiment program. `evidence/04_runs/` contains run configurations, summaries,
pooling manifests and the frozen prediction scorecard. `evidence/05_coding/`
contains the anonymized confirmatory and Haiku transcript packets, coding
instructions, returned coding sheets, unblinding keys, adjudications and
consensus outputs; it also contains the Qwen packet and raw characterization
data used for the audit-only result. Analysis scripts and machine-readable
results are in `evidence/06_analysis/`. At the package root,
`FILE_INVENTORY.txt` lists the contents and `MANIFEST.sha256` records checksums
for the staged files. Running `./verify.sh` checks those files and executes
`tools/recompute_core_claims.py`. The program requires Python, the Anthropic
SDK, HTTPX and Pydantic. The recorded run configurations specify the models
and inputs used.

```{=latex}
\clearpage
\printbibliography[title={References}]
\clearpage
```

# Appendix A: Frozen prediction scorecard {.unnumbered}

{{INCLUDE:prediction-scorecard-table}}

Full results for every preregistered contrast are
archived in Section 5 of \path{confirmatory_v2_pooled_REPORT.md} in
\path{evidence/07_reports/}.

```{=latex}
\clearpage
```

# Appendix B: Model, sampling and serving metadata {.unnumbered}

The recorded configuration and collection metadata are summarized here for
the confirmatory Opus run, the exploratory Haiku run and the audit-only Qwen
run. The three Opus source configurations record the requested alias and start
times but predate the addition of a `provider_info` block to the run record;
their provider, call parameters and response method are recoverable from the
archived routing and agent code. The later Haiku and Qwen configurations record
those fields directly. Start times below are reproduced exactly as stored. The
records contain neither a time-zone offset nor a completion time.

```{=latex}
\begin{table}[H]
\centering
\footnotesize
\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.18\textwidth}>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}p{0.25\textwidth}@{}}
\toprule
Configuration & Provider and interface & Requested and logged model identifiers & Recorded start time(s) \\
\midrule
Confirmatory Opus & Anthropic Messages API & Requested: \texttt{claude-opus-5}. Logged response identifier in all 1,443 retained moments: \texttt{claude-opus-5}. & 2026-07-30 12:42:44; 16:11:47; 16:44:13 \\
Exploratory Haiku & Anthropic Messages API & Requested: \texttt{claude-haiku-4-5}. Logged response identifier in all 1,364 moments: \texttt{claude-haiku-4-5-20251001}. & 2026-07-31 07:56:12 \\
Audit-only Qwen & Local Ollama, OpenAI-compatible endpoint at \url{http://localhost:11434/v1} & Requested: \texttt{qwen2.5:7b-instruct}. Apparatus-logged response identifier in all 254 moments: \texttt{ollama:qwen2.5:7b-instruct}. & 2026-07-31 12:57:06 \\
\bottomrule
\end{tabularx}
\caption{Recorded provider, model and collection metadata. The Opus response
identifier remained a mutable alias; the Haiku response supplied a dated
identifier.}
\label{tab:model-metadata}
\end{table}
```

The confirmatory configuration produced 150 retained repetitions from 165
attempts, with 15 condition A attempts aborted without model output after the
account reached its API usage limit. Its retained logs comprise 1,443 moment
records, 4,499,827 input tokens and 668,365 output tokens. Haiku produced 150
retained repetitions with no aborted repetitions, comprising 1,364 moments,
2,964,270 input tokens and 274,801 output tokens. The Qwen characterization
comprised three repetitions in each of five conditions, 15 in total, with 254
logged moments, no aborted repetitions, 368,507 input tokens and 11,254 output
tokens. These totals
cover retained successful moments rather than failed or retried HTTP requests.
They are API-reported or Ollama-reported token counts and need not be identical
across tokenizers.

```{=latex}
\begin{table}[H]
\centering
\footnotesize
\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.17\textwidth}>{\raggedright\arraybackslash}p{0.18\textwidth}>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}p{0.12\textwidth}@{}}
\toprule
Configuration & Temperature & Maximum output & Structured-response method & Generation seed \\
\midrule
Opus and Haiku & Parameter omitted; Anthropic API default, recorded by the apparatus as 1.0 & 8,192 tokens & Anthropic \texttt{messages.parse} with a Pydantic schema requiring an action and allowing optional spoken text and a private reason & None supplied \\
Qwen & 1.0, explicitly supplied & 8,192 tokens & Strict JSON schema requested through the OpenAI-compatible endpoint; on schema rejection, JSON-object fallback with the schema appended to the system instruction & None supplied \\
\bottomrule
\end{tabularx}
\caption{Recorded generation and response-format settings. Coding-packet
shuffle seeds elsewhere in the archive did not control model generation.}
\label{tab:sampling-metadata}
\end{table}
```

At the experiment-runner level, any failed moment was retried once after five
seconds; a second failure aborted that repetition. The OpenAI-compatible path
used for Qwen additionally allowed up to eight HTTP attempts for status 429,
500, 502 or 503, respecting `Retry-After` when present and otherwise using
exponential delays capped at 120 seconds. A 400 response rejecting strict JSON
schema caused a switch to JSON-object mode. The response-format mode ultimately
used for each Qwen call was not logged.

Some serving details cannot be recovered. The archive does not pin Python
dependency versions, so the Anthropic SDK's internal retry behavior is not
exactly reconstructable. It also contains no Ollama version, model-blob digest,
quantization, hardware specification or context configuration. More generally,
requested and returned model identifiers do not preserve provider-side
instructions, safety post-training or the exact serving state. The archived
outputs therefore support reproduction of the reported analyses, while a new
apparatus run cannot be expected to reproduce the same behavior exactly.

```{=latex}
\clearpage
```

# Appendix C: Exploratory Haiku coding procedure {.unnumbered}

The 150 Haiku transcripts were pooled under a neutral packet name and assigned
shuffled identifiers from T01 to T150. The packet withheld the condition key,
condition labels and model identity. Two valid blind LLM coding sessions then
independently coded every transcript, in the same order, using the archived
instructions and their 13 categorical measures. Coders were instructed to work
alone, use no experiment material beyond the packet, and return one complete
coding sheet. Transcript content was otherwise preserved, so this blinding did
not remove textual cues from which a condition might be inferred.

Before adjudication, the two sessions agreed on 1,799 of 1,950 categorical
cells (92.3 percent). Agreement for the three Haiku outcomes reported in the
main text was as follows:

| Measure | Agreements | Ties sent to adjudication | Percent agreement |
|---|---:|---:|---:|
| IDENTITY | 119/150 | 31 | 79.3 |
| MISMATCH | 150/150 | 0 | 100.0 |
| VERIFY | 137/150 | 13 | 91.3 |
| All 13 measures | 1,799/1,950 | 151 | 92.3 |

Because two coders cannot form a majority when they disagree, each of the 151
disputed cells was recorded as a tie. One fresh blind LLM adjudication session
resolved all 151 ties. Its decisions replaced the tied cells in the blind
consensus file; only then was the transcript key applied to recover condition
labels and compute the exploratory counts reported here.

Three additional self-coding sheets were excluded before analysis. Each was
incomplete, covering only 25 to 35 of the 150 transcripts, and each was
produced outside the investigator's coder-recruitment procedure. They are
retained in an invalid-partial-sheets subdirectory of the Haiku coding results
for audit but contributed no codes. The two valid sheets, the 151-row
adjudication file, both consensus files and the unblinding key are archived in
the evidence package.

```{=latex}
\clearpage
```

# Appendix D: Coder-level sensitivity of the ownership result {.unnumbered}

The three blind LLM coding sessions independently classified the same 150
confirmatory transcripts. Session numbers below identify the three archived
coding sheets; they are not model identifiers. The final consensus remains
the manuscript's prespecified primary coding result, while the session-level
results show how strongly that result depends on coder calibration.

{{INCLUDE:coder-sensitivity-table}}

Every session coded more OWN reports in B than in C, and every session coded
zero C transcripts as OWN. The estimated B--C difference nevertheless ranged
from 20.0 to 93.3 percentage points. Session 3 used UNCERTAIN much more often
than the other sessions, including outside B and C, and consequently produced
the smallest B estimate. The final-consensus estimate lies at the upper end
of the session-level range.

These are sensitivity analyses of alternative ratings of the same transcripts,
not three independent experimental replications. They support a stable
direction for the B--C contrast under the observed codings, but they do not
support treating its consensus magnitude as free of measurement uncertainty.
