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
    <div className={cn('bg-panel p-3.5 rounded-lg border border-edge', className)}>
      <div className="flex items-start justify-between">
        <div>
          <div className="text-[11px] text-fg-muted">{label}</div>
          <div className="text-xl font-semibold text-fg mt-0.5 font-mono tabular-nums">{value}</div>
          {detail && <div className="text-[11px] text-fg-muted mt-1">{detail}</div>}
        </div>
        {icon && (
          <div className="w-7 h-7 rounded-md bg-panel-inset text-fg-muted flex items-center justify-center shrink-0">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
