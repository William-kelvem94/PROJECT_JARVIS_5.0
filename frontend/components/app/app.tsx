'use client';

import { useMemo, useState } from 'react';
import { TokenSource } from 'livekit-client';
import { useSession } from '@livekit/components-react';
import { WarningIcon } from '@phosphor-icons/react/dist/ssr';
import type { AppConfig } from '@/app-config';
import { AgentSessionProvider } from '@/components/agents-ui/agent-session-provider';
import dynamic from 'next/dynamic';
const StartAudioButton = dynamic(() => import('@/components/agents-ui/start-audio-button').then(mod => ({ default: mod.StartAudioButton })), { ssr: false });
const ViewController = dynamic(() => import('@/components/app/view-controller').then(mod => ({ default: mod.ViewController })), { ssr: false });
const Toaster = dynamic(() => import('@/components/ui/sonner').then(mod => ({ default: mod.Toaster })), { ssr: false });
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { useDebugMode } from '@/hooks/useDebug';
import { getSandboxTokenSource } from '@/lib/utils';
import { useAutoReconnect } from '@/hooks/useAutoReconnect';
import { log } from '@/lib/logger';

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';
// allow enabling livekit debug via env variable (true/1)
const LIVEKIT_DEBUG = process.env.NEXT_PUBLIC_LIVEKIT_DEBUG === 'true' || process.env.NEXT_PUBLIC_LIVEKIT_DEBUG === '1';

function AppSetup() {
  useDebugMode({ enabled: LIVEKIT_DEBUG });
  useAgentErrors();

  return null;
}

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  const [participantName, setParticipantName] = useState<string>('user');

  const tokenSource = useMemo(() => {
    if (typeof process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT === 'string') {
      return getSandboxTokenSource(appConfig);
    }

    return TokenSource.custom(async () => {
      const url = new URL('/api/connection-details', window.location.origin);
      const roomConfig = appConfig.agentName
        ? {
          agents: [{ agent_name: appConfig.agentName }],
        }
        : undefined;

      try {
        const res = await fetch(url.toString(), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            room_config: roomConfig,
            participant_name: participantName,
          }),
        });

        const text = await res.text();
        try {
          return JSON.parse(text);
        } catch (parseError) {
          console.error('[TOKEN_FETCH] Failed to parse JSON. Raw response:', text);
          throw new Error('Formato de resposta inválido da API de conexão.');
        }
      } catch (error: any) {
        log.error('Error fetching connection details:', error);
        throw error;
      }
    });
  }, [appConfig, participantName]);

  const session = useSession(
    tokenSource,
    appConfig.agentName ? { agentName: appConfig.agentName } : undefined
  );

  // Hook de Auto-Reconexão
  useAutoReconnect(session);

  return (
    <AgentSessionProvider session={session}>
      <AppSetup />
<main className="h-svh flex flex-col items-center justify-center p-8 overflow-hidden">
        <div className="w-full max-w-2xl mx-auto flex flex-col items-center gap-8">
          <ViewController appConfig={appConfig} onParticipantNameChange={setParticipantName} />
        </div>
      </main>
      <StartAudioButton label="Start Audio" />
      <Toaster
        icons={{
          warning: <WarningIcon weight="bold" />,
        }}
        position="top-center"
        className="toaster group"
        style={
          {
            '--normal-bg': 'var(--popover)',
            '--normal-text': 'var(--popover-foreground)',
            '--normal-border': 'var(--border)',
          } as React.CSSProperties
        }
      />
    </AgentSessionProvider>
  );
}
