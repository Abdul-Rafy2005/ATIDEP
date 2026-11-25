import { cn } from 'cn';
import { type ReactNode } from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  detail?: string;
  icon?: ReactNode;
  className?: string;
}

export function MetricCard({ label, value, detail, icon, className }: MetricCardProps) {
  return (
    <div className={cn('bg-panel rounded-lg border border-edge overflow-hidden transition-colors hover:border-edge-hover', className)}>
      <div className="flex">
        <div className="w-1 bg-brand shrink-0 rounded-l-lg" />
        <div className="flex-1 p-3.5 flex items-start justify-between">
          <div>
            <div className="text-[11px] text-fg-muted font-medium">{label}</div>
            <div className="text-xl font-semibold text-fg mt-1 font-mono tabular-nums tracking-tight">{value}</div>
            {detail && <div className="text-[11px] text-fg-muted mt-1.5">{detail}</div>}
          </div>
          {icon && (
            <div className="w-7 h-7 rounded-md bg-panel-inset text-fg-muted flex items-center justify-center shrink-0">
              {icon}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
