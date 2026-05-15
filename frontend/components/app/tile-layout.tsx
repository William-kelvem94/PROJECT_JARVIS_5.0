'use client';

import type { AppConfig } from '@/app-config';
import { ScreenshotGallery } from './screenshot-gallery';
import { VisionPiP } from './vision-pip';

interface TileLayoutProps {
  chatOpen: boolean;
  appConfig?: AppConfig;
}

export function TileLayout({ chatOpen, appConfig }: TileLayoutProps) {
  return (
    <div className="pointer-events-none fixed inset-x-0 top-8 bottom-32 z-50 md:top-12 md:bottom-40">
      <div className="relative mx-auto h-full max-w-2xl px-4 md:px-0">
        <ScreenshotGallery
          apiUrl={appConfig?.jarvisApiUrl}
          className="absolute top-0 -right-32 hidden xl:block"
        />
        <VisionPiP apiUrl={appConfig?.jarvisApiUrl} />
        <div className="flex h-full w-full items-center justify-center rounded-3xl border border-white/10 bg-black/20 p-6 text-center text-xs text-white/60">
          {chatOpen ? 'Media layout not available in this build.' : 'Idle media panel'}
        </div>
      </div>
    </div>
  );
}
