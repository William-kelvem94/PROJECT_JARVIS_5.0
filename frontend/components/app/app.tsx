'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { WarningIcon } from '@phosphor-icons/react/dist/ssr';
import type { AppConfig } from '@/app-config';
import { Toaster } from '@/components/ui/sonner';
import { JarvisProvider } from '@/context/JarvisContext';

const ViewController = dynamic(
  () => import('@/components/app/view-controller').then((mod) => ({ default: mod.ViewController })),
  { ssr: false }
);

export function App({ appConfig }: { appConfig: AppConfig }) {
  const [, setParticipantName] = useState<string>('user');

  return (
    <JarvisProvider>
      <main className="flex h-svh flex-col items-center justify-center overflow-hidden bg-black p-8 text-white">
        <div className="mx-auto flex w-full max-w-2xl flex-col items-center gap-8">
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
    </JarvisProvider>
  );
}
