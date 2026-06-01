/**
 * Brief templates for Bowers Frontier Macro Labs corridor intelligence.
 * Python generator (src/corridor_intelligence/brief.py) is canonical; this file
 * documents the required brief structure for tooling and future Node integrations.
 */

export const BRIEF_TITLE = "Bowers Frontier Macro Labs — Corridor Intelligence Brief";

export const BRIEF_SECTIONS = [
  "Executive summary",
  "Data lineage",
  "Risk score breakdown",
  "Flow context",
  "Validation notes",
  "Limitations",
];

export const BRIEF_DISCLAIMER =
  "Research only. Not investment advice. Not a price or FX prediction.";

export function briefHeader({ corridor, asOf, score, band }) {
  return `# ${BRIEF_TITLE}

**Corridor:** ${corridor}
**As of:** ${asOf}
**Corridor Risk Score:** ${score}/100 (${band})

> ${BRIEF_DISCLAIMER}
`;
}
