# Claims

| Claim | Status | Support | Caveat |
|---|---|---|---|
| Empty feasible-action intersections make deterministic compressed contact control impossible for the aliased modes. | Formal theorem. | Proof in `paper/main.tex`. | One-step/local; probing or belief can help if allowed before the critical action. |
| Coarse contact compression frequently creates empty feasible-action intersections in the synthetic contact model. | Empirical v3 claim. | Family A contact-count success 0.759 and empty-alias rate 0.969; Family H contact-count success 0.764 and empty-alias rate 0.962. | Synthetic local model only. |
| CCSC repairs most measured failures when signatures are rich enough. | Empirical v3 claim. | Family A CCSC 6x8 success 0.999954 and empty-alias rate 0.000389; Family H CCSC 6x8 success 0.999932. | Depends on task/action probes and reliable feasibility labels. |
| Low-budget signatures under-separate action cones. | Empirical boundary. | Family B one probe/two sectors success near 0.956 and empty-alias near 0.115. | Thresholds are model-specific. |
| Active probing is an exception, not a contradiction. | Formal boundary plus v3 evidence. | Family E probe-allowed settings rescue contact-count aliases; first-action-required settings do not. | Probe must be safe, reliable, and before the task action. |

## Unsupported Claims

- Hardware readiness.
- Learned tactile signature extraction.
- Superiority over production contact-implicit planners.
- General POMDP optimality.
- Safety certification.
