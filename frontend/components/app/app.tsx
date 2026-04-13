'use client';

import { useState } from 'react';
import { WarningIcon } from '@phosphor-icons/react/dist/ssr';
import type { AppConfig } from '@/app-config';
import dynamic from 'next/dynamic';
import { Toaster } from '@/components/ui/sonner';

const ViewController = dynamic(() => import('@/components/app/view-controller').then(mod => ({ default: mod.ViewController })), { ssr: false });

export function App({ appConfig }: { appConfig: AppConfig }) {
  const [participantName, setParticipantName] = useState<string>('user');

  return (
    <>
      <main className="h-svh flex flex-col items-center justify-center p-8 overflow-hidden bg-black text-white">
        <div className="w-full max-w-2xl mx-auto flex flex-col items-center gap-8">
          <ViewController appConfig={appConfig} onParticipantNameChange={setParticipantName} />
        </div>
      </main>
      
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
    </>
  );
}
