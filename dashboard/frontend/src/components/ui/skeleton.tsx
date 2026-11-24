import { cn } from 'cn';

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded bg-panel-hover', className)} />;
}
