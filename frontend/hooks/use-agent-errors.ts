import React, { ReactNode } from 'react';
import { toast as sonnerToast } from 'sonner';
import { WarningIcon } from '@phosphor-icons/react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface ToastProps {
  title: ReactNode;
  description: ReactNode;
}

function toastAlert(toast: ToastProps) {
  const { title, description } = toast;

  return sonnerToast.custom(
    (id) =>
      React.createElement(
        Alert,
        { onClick: () => sonnerToast.dismiss(id), className: 'bg-accent w-full md:w-91' },
        React.createElement(WarningIcon, { weight: 'bold' }),
        React.createElement(AlertTitle, null, title),
        description ? React.createElement(AlertDescription, null, description) : null
      ),
    { duration: 10_000 }
  );
}

/**
 * Hook refatorado para o Jarvis Native.
 */
export function useAgentErrors() {
  const [errors, setErrors] = React.useState<string[]>([]);

  // TODO: Implementar ouvintes de erro vindos do useJarvisVoice se necessário futuramente.

  return {
    errors,
    clear: () => setErrors([]),
    addError: (msg: string) => {
      setErrors((prev) => [...prev, msg]);
      toastAlert({ title: 'Erro no Jarvis', description: msg });
    },
  };
}
