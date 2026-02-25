import React from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/shadcn/utils';

interface SessionDiagnosticsProps {
  errors: string[];
  onClear: () => void;
}

export function SessionDiagnostics({ errors, onClear }: SessionDiagnosticsProps) {
  if (errors.length === 0) {
    return null;
  }

  const copyToClipboard = () => {
    const text = errors.join('\n');
    navigator.clipboard.writeText(text).catch(() => {
      // ignore
    });
  };

  return (
    <div
      className={cn(
        'absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/90 p-4 text-white',
        'pointer-events-auto'
      )}
    >
      <div className="max-w-xl space-y-4 text-center">
        <h2 className="text-xl font-bold">Session diagnostics</h2>
        <div className="text-left max-h-40 overflow-auto rounded bg-gray-900/50 p-2">
          <ul className="list-inside list-disc">
            {errors.map((err, idx) => (
              <li key={idx} className="break-words">
                {err}
              </li>
            ))}
          </ul>
        </div>
        <div className="flex gap-2 justify-center">
          <Button size="sm" onClick={copyToClipboard}>
            Copy details
          </Button>
          <Button size="sm" variant="secondary" onClick={onClear}>
            Dismiss
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={() => window.location.reload()}
          >
            Reload
          </Button>
        </div>
      </div>
    </div>
  );
}
