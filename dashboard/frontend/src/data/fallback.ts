import type { OverviewMetrics, TacticCoverage, TechniqueItem, RunItem } from '../types';
import allTechniquesJson from './all_techniques.json';
import allRunsJson from './all_runs.json';

export const fallbackOverview: OverviewMetrics = {
  total_techniques: 44,
  covered: 32,
  coverage_pct: 72.7,
  total_rules_tested: 804,
  recent_run: "20261111_1518_set3_v3b",
  recent_run_score: "54/60"
};

export const fallbackTactics: TacticCoverage[] = [
  { tactic_name: "Initial Access", total_techniques: 2, covered_techniques: 1, coverage_pct: 50.0 },
  { tactic_name: "Execution", total_techniques: 8, covered_techniques: 7, coverage_pct: 87.5 },
  { tactic_name: "Persistence", total_techniques: 12, covered_techniques: 8, coverage_pct: 66.7 },
  { tactic_name: "Privilege Escalation", total_techniques: 5, covered_techniques: 4, coverage_pct: 80.0 },
  { tactic_name: "Defense Evasion", total_techniques: 15, covered_techniques: 12, coverage_pct: 80.0 },
  { tactic_name: "Credential Access", total_techniques: 4, covered_techniques: 3, coverage_pct: 75.0 },
  { tactic_name: "Discovery", total_techniques: 6, covered_techniques: 6, coverage_pct: 100.0 },
  { tactic_name: "Lateral Movement", total_techniques: 3, covered_techniques: 2, coverage_pct: 66.7 },
  { tactic_name: "Collection", total_techniques: 2, covered_techniques: 1, coverage_pct: 50.0 },
  { tactic_name: "Command and Control", total_techniques: 4, covered_techniques: 3, coverage_pct: 75.0 },
  { tactic_name: "Exfiltration", total_techniques: 1, covered_techniques: 1, coverage_pct: 100.0 },
  { tactic_name: "Impact", total_techniques: 3, covered_techniques: 2, coverage_pct: 66.7 },
  { tactic_name: "Resource Development", total_techniques: 2, covered_techniques: 1, coverage_pct: 50.0 },
  { tactic_name: "Reconnaissance", total_techniques: 2, covered_techniques: 1, coverage_pct: 50.0 },
];

export const fallbackTechniques: TechniqueItem[] = allTechniquesJson as unknown as TechniqueItem[];

export const fallbackRuns: RunItem[] = (allRunsJson as unknown as RunItem[]).slice().sort((a, b) => b.folder.localeCompare(a.folder));

