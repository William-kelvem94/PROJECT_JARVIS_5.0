'use client';

import { useMemo } from 'react';
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
  const tokenSource = useMemo(() => {
    return typeof process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT === 'string'
      ? getSandboxTokenSource(appConfig)
      : TokenSource.endpoint('/api/connection-details');
  }, [appConfig]);

  const session = useSession(
    tokenSource,
    appConfig.agentName ? { agentName: appConfig.agentName } : undefined
  );

  // Hook de Auto-Reconexão
  useAutoReconnect(session);

  return (
    <AgentSessionProvider session={session}>
      <AppSetup />
      <main className="grid h-svh grid-cols-1 place-content-center">
        <ViewController appConfig={appConfig} />
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
