# Final Audit

1. **Chosen thesis.** Contact-state compression can destroy controllability when it aliases individually controllable contact modes whose task-feasible action sets have empty intersection.

2. **Field assumption broken.** The paper challenges the assumption that compact contact labels, contact counts, prediction-trained latents, or semantic tactile states preserve the action distinctions a controller needs.

3. **New central mechanism.** Contact-cone separating compression audits alias classes by robust feasible-action intersection and repairs unsafe aliases with action/task feasibility signatures.

4. **Proof status.** The empty-intersection obstruction is formally proved as a one-step/local theorem. Active probing is identified as an exception when it is safe, reliable, and before the task action.

5. **Strongest evidence.** The v3 suite has 85,674 rows and 1,290 cases. Family A: contact count success 0.759 and empty-alias 0.969; CCSC 6x8 success 0.999954 and empty-alias 0.000389. Family H: 80,640 task-conditioned rows with the same pattern.

6. **Boundary evidence.** Family B shows one probe task/two sectors under-separate. Family C stresses noisy labels. Family E shows active probing helps only in probe-allowed regimes. Family F includes shared-action and hard negative controls.

7. **Biggest weaknesses.** Synthetic local model, one-step deterministic theorem, no hardware, no learned tactile signature extractor, no production contact-implicit planner, and no general POMDP baseline.

8. **Paper-readiness judgment.** Final under the current batch standard as a scoped synthetic mechanism paper.

9. **Exact Downloads PDF path.** `C:/Users/wangz/Downloads/27.pdf`

10. **Downloads PDF verification.** 25 pages, 333998 bytes, SHA256 `33273D7AEDE66A426953DD00D1BE14D571B78C42D83F9B3AF0B8B41465949179`.

11. **Local repository PDF status.** `paper/main.pdf` absent after canonical copy.
