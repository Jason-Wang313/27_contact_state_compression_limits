# Literature Map

## Sweep Protocol
- Landscape sweep target: 1000; collected matrix rows: 1000.
- Serious skim: top 300 by contact/control relevance.
- Deep read set: top 225 with abstracts and mechanism/assumption extraction.
- Hostile prior-work set: 100 papers weighted toward contact modes, controllability, trajectory optimization, and state abstraction.
- Retrieval source: OpenAlex API plus a small curated seed list for seminal contact and abstraction papers.

## Field Box
Robotics contact dynamics at the boundary of contact-rich manipulation, hybrid control, tactile/contact-state estimation, trajectory optimization, simulation, and representation/state abstraction. The paper must stay about embodied systems where contact variables change feasible robot actions, not generic representation learning.

## Coverage Counts
- general_robotics_contact: 525
- hybrid_contact_control: 291
- contact_rich_manipulation: 155
- simulation_models: 40
- planar_pushing: 30
- tactile_state_estimation: 23
- state_abstraction: 18
- locomotion_contact: 8
- trajectory_optimization: 5

## Year Coverage Snapshot
1999:13, 2000:13, 2001:29, 2002:28, 2003:28, 2004:22, 2005:27, 2006:29, 2007:16, 2008:24, 2009:32, 2010:46, 2011:32, 2012:35, 2013:47, 2014:53, 2015:65, 2016:41, 2017:44, 2018:57, 2019:46, 2020:56, 2021:17, 2022:11, 2023:7

## Most Relevant Prior Work
| Rank | Year | Paper | Why it matters here |
|---:|---:|---|---|
| 1 | 2002 | Perceived Behavioral Control, SelfEfficacy, Locus of Control, and the Theory of Planned Behavior<sup>1</sup> | explicit contact modes and complementarity constraints are established |
| 2 | 2017 | Learning hand-eye coordination for robotic grasping with deep learning and large-scale data collection | contact-aware robot control is a crowded area |
| 3 | 1991 | Fractal Model of Elastic-Plastic Contact Between Rough Surfaces | explicit contact modes and complementarity constraints are established |
| 4 | 2000 | Contact-line dynamics of a diffuse fluid interface | explicit contact modes and complementarity constraints are established |
| 5 | 2005 | A Finite Element Study of Elasto-Plastic Hemispherical Contact Against a Rigid Flat | explicit contact modes and complementarity constraints are established |
| 6 | 2017 | Parameter and Contact Force Estimation of Planar Rigid-Bodies Undergoing Frictional Contact | contact-aware robot control is a crowded area |
| 7 | 2015 | Pose Estimation for Contact Manipulation with Manifold Particle Filters | contact-aware robot control is a crowded area |
| 8 | 2002 | Elastic-Plastic Contact Analysis of a Sphere and a Rigid Flat | explicit contact modes and complementarity constraints are established |
| 9 | 2014 | A Direct Method for Trajectory Optimization of Rigid Bodies Through Contact | optimizing through contact with known variables is established |
| 10 | 1996 | Stable Pushing: Mechanics, Controllability, and Planning | contact mechanics and pushing controllability are established |
| 11 | 1997 | Formulating Dynamic Multi-Rigid-Body Contact Problems with Friction as Solvable Linear Complementarity Problems | explicit contact modes and complementarity constraints are established |
| 12 | 1986 | Meniscal tears: The effect of meniscectomy and of repair on intraarticular contact areas and stress in the human knee | contact-aware robot control is a crowded area |
| 13 | 2009 | Prevention of noncontact anterior cruciate ligament injuries in soccer players. Part 1: Mechanisms of injury and underlying risk factors | contact-aware robot control is a crowded area |
| 14 | 2012 | Discovery of Complex Behaviors Through Contact-Invariant Optimization | optimizing through contact with known variables is established |
| 15 | 1993 | Dimensions of Contact as Predictors of Intergroup Anxiety, Perceived Out-Group Variability, and Out-Group Attitude: An Integrative Model | explicit contact modes and complementarity constraints are established |
| 16 | 2023 | Silicon heterojunction solar cells with up to 26.81% efficiency achieved by electrically optimized nanocrystalline-silicon hole contact layers | contact-aware robot control is a crowded area |
| 17 | 2017 | Wearable smart sensor systems integrated on soft contact lenses for wireless ocular diagnostics | contact-aware robot control is a crowded area |
| 18 | 2011 | E-cadherin mediates contact inhibition of proliferation through Hippo signaling-pathway components | contact-aware robot control is a crowded area |
| 19 | 1996 | Causes and Consequences of Earnings Manipulation: An Analysis of Firms Subject to Enforcement Actions by the SEC* | contact-aware robot control is a crowded area |
| 20 | 2022 | Robot Operating System 2: Design, architecture, and uses in the wild | explicit contact modes and complementarity constraints are established |
| 21 | 1992 | Controllability of Stressful Events and Satisfaction With Spouse Support Behaviors | explicit contact modes and complementarity constraints are established |
| 22 | 1998 | Contact analysis of elastic-plastic fractal surfaces | explicit contact modes and complementarity constraints are established |
| 23 | 1985 | Contact Mechanics | contact mechanics and pushing controllability are established |
| 24 | 2020 | Quantifying SARS-CoV-2 transmission suggests epidemic control with digital contact tracing | contact-aware robot control is a crowded area |
| 25 | 2011 | PSICOV: precise structural contact prediction using sparse inverse covariance estimation on large multiple sequence alignments | explicit contact modes and complementarity constraints are established |

## Hidden Assumptions That May Be False
1. The contact mode is either observed or can be inferred without taking control-risking actions.
2. A compact contact state remains Markov for the downstream controller.
3. Prediction loss is a sufficient proxy for preserving controllability.
4. Contact count is a harmless substitute for contact geometry.
5. Friction coefficients can be held fixed while evaluating representation quality.
6. The local feasible action cone is unchanged by state compression.
7. A planner can repair missing contact details by replanning over the compressed state.
8. Tactile classifiers need only recognize semantic contact labels, not action-separating predicates.
9. Hybrid mode boundaries matter only for transition prediction, not for available actions.
10. Averaging over contact modes gives a useful controller input.
11. The same latent world-model state can serve prediction, planning, and feedback control.
12. Small geometric aliasing errors produce small control errors.
13. Mode uncertainty is the main issue, rather than irreversible loss of action distinctions.
14. All states merged by a representation share at least one robust action for the task.
15. A learned decoder can reconstruct any contact detail needed after compression.
16. Planning benchmarks sample tasks where aliasing is benign.
17. Local contact patches with similar appearance have similar control cones.
18. Bisimulation-like abstractions transfer directly to discontinuous contact systems.
19. Safety constraints can be checked after choosing an action from compressed state.
20. Exploration can disambiguate contact modes before a safety-critical move is required.
21. The contact graph is the right primitive; edge labels need not encode controllability.
22. World-model rollouts need not preserve viability kernels.
23. A verifier or ensemble can compensate for an insufficient state representation.
24. The cost of retaining action-separating bits is larger than the cost of downstream failures.

## Candidate Directions That Break Assumptions
1. Control-cone separating compression: define contact compression by intersections of feasible action cones, prove aliasing impossibility when the intersection is empty, and repair by splitting only action-separating aliases.
2. Tactile objective redesign: train tactile encoders to predict local action feasibility signatures rather than contact labels.
3. Viability-preserving world-model bottlenecks: penalize latent merges that change the local viability kernel even if next-state prediction is accurate.
4. Contact-memory certificates: characterize when a history of compressed observations can recover the missing mode before a safety deadline.
5. Benchmark-only stress tests: rejected as too weak unless paired with a new mechanism and impossibility result.

## Direction Chosen After Sweep
The strongest direction is control-cone separating compression. The hostile literature already covers explicit contact modes, trajectory optimization through known constraints, and generic MDP abstraction. It less often asks whether a compressed contact state preserves a nonempty common feasible-action set for every merged mode. That gives a central mechanism: compression is safe only when it preserves task-conditioned action-cone intersections.
