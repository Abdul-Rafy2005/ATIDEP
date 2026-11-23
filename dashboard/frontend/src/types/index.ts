export interface OverviewMetrics {
  total_techniques: number;
  covered: number;
  coverage_pct: number;
  total_rules_tested: number;
  recent_run?: string;
  recent_run_score?: string;
}

export interface TacticCoverage {
  tactic_name: string;
  total_techniques: number;
  covered_techniques: number;
  coverage_pct: number;
}

export interface TechniqueItem {
  id: string;
  title: string;
  tactics: string[];
  sets: number[];
  best_verdict: string;
  ref_status?: string;
  events?: Record<string, { shown?: string; variant?: string; benign?: string }>;
}

export interface RunItem {
  folder: string;
  date: string;
  set: number;
  prompt: string;
  models: string[];
  strict_pass: number;
  single_pass: number;
  syntax_errors: number;
  too_narrow?: number;
  total: number;
  label: 'primary' | 'baseline' | 'exploratory' | 'development';
  temperature?: number;
  repeats?: number;
  results?: Array<{
    model: string;
    technique: string;
    repeat: number;
    strict_pass: string;
    single_pass: string;
    verdict: string;
    tokens_per_second?: number;
    seconds?: number;
  }>;
}

export interface GateTestResult {
  verdict: 'PASS' | 'TOO_NARROW' | 'NOISY' | 'MISSED_SHOWN' | 'SYNTAX_ERROR';
  reason?: string;
  syntax_ok: boolean;
  fires_shown: boolean;
  fires_variant: boolean;
  fires_benign: boolean;
}

export interface PipelineExecutionResult {
  technique_id: string;
  technique_name: string;
  process_image: string;
  extracted_command: string;
  rule_yaml: string;
  verdict: string;
  verdict_explanation: string;
  extract_time: number;
  gen_time: number;
  model: string;
}
