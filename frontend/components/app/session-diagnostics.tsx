import React from 'react';
import { Button } from '@/components/ui/button';
import { log } from '@/lib/logger';
import { cn } from '@/lib/shadcn/utils';

interface SessionDiagnosticsProps {
  errors: string[];
  onClear: () => void;
}

const MAX_ERRORS = 50;
const ERROR_THROTTLE_MS = 1000;

function limitErrors(errors: string[]) {
  if (errors.length <= MAX_ERRORS) return errors;
  return errors.slice(-MAX_ERRORS);
}

// ...existing code...
export const SessionDiagnostics = React.memo(function SessionDiagnostics({
  errors,
  onClear,
}: SessionDiagnosticsProps) {
  const limited = limitErrors(errors);
  const lastErrorRef = React.useRef<string | null>(null);
  const lastLogTimeRef = React.useRef<number>(0);
  React.useEffect(() => {
    if (limited.length > 0) {
      const now = Date.now();
      if (
        lastErrorRef.current !== limited[limited.length - 1] ||
        now - lastLogTimeRef.current > ERROR_THROTTLE_MS
      ) {
        log.error(limited[limited.length - 1]);
        lastErrorRef.current = limited[limited.length - 1];
        lastLogTimeRef.current = now;
      }
    }
  }, [limited]);
  if (limited.length === 0) {
    return null;
  }

  const copyToClipboard = async () => {
    const text = limited.join('\n');
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // fallback to textarea hack when clipboard API fails
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
    }
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
        <div className="max-h-40 overflow-auto rounded bg-gray-900/50 p-2 text-left">
          <ul className="list-inside list-disc">
            {limited.map((err, idx) => (
              <li key={idx} className="wrap-break-word">
                {err}
              </li>
            ))}
          </ul>
        </div>
        <div className="flex justify-center gap-2">
          <Button size="sm" onClick={copyToClipboard}>
            Copy details
          </Button>
          <Button size="sm" variant="secondary" onClick={onClear}>
            Dismiss
          </Button>
          <Button size="sm" variant="destructive" onClick={() => window.location.reload()}>
            Reload
          </Button>
        </div>
      </div>
    </div>
  );
});
