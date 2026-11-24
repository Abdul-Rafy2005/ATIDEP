import { cn } from 'cn';

export function getVerdictStyle(verdict: string): string {
  switch (verdict) {
    case 'PASS':
      return 'bg-pass-muted text-pass border-pass-edge';
    case 'TOO_NARROW':
      return 'bg-narrow-muted text-narrow border-narrow-edge';
    case 'NOISY':
      return 'bg-noisy-muted text-noisy border-noisy-edge';
    case 'SYNTAX_ERROR':
    case 'MISSED_SHOWN':
      return 'bg-critical-muted text-critical border-critical-edge';
    default:
      return 'bg-panel-inset text-fg-muted border-edge';
  }
}

export function getRoleBadgeStyle(role: string): string {
  switch (role) {
    case 'primary':
      return 'bg-brand-muted text-brand border-brand-edge';
    case 'baseline':
      return 'bg-panel-inset text-fg-secondary border-edge';
    default:
      return 'bg-panel-inset text-fg-muted border-edge';
  }
}

interface VerdictBadgeProps {
  verdict: string;
  className?: string;
}

export function VerdictBadge({ verdict, className }: VerdictBadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold border',
      getVerdictStyle(verdict),
      className
    )}>
      {verdict}
    </span>
  );
}
