'use client';

import React, { useEffect, useRef } from 'react';
import { log } from '@/lib/logger';
import { useVoiceAssistant, useTrackVolume } from '@livekit/components-react';

// FIX 1: carrega Three.js + p5.js em paralelo antes do Vanta
const loadScript = (src: string): Promise<boolean> => {
    return new Promise((resolve) => {
        if (typeof document === 'undefined') return resolve(false);
        if (document.querySelector(`script[src="${src}"]`)) return resolve(true);
        const script = document.createElement('script');
        script.src = src;
        script.async = true;
        script.onload = () => resolve(true);
        script.onerror = () => resolve(false);
        document.body.appendChild(script);
    });
};

// Responsável por instanciar a esfera e carregar os scripts
export const VantaOrb = ({ isConnected, color, vantaRef }: { isConnected: boolean, color: number, vantaRef: React.MutableRefObject<any> }) => {
    const localRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        let vantaEffect: any = null;
        let attempts = 0;
        let initTimer: NodeJS.Timeout;

        const setup = async () => {
            // FIX 1: Three.js e p5.js carregam em PARALELO; só após ambos carrega o Vanta
            await Promise.all([
                loadScript('https://cdnjs.cloudflare.com/ajax/libs/three.js/r152/three.min.js'),
                loadScript('https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js'),
            ]);
            await loadScript('https://cdn.jsdelivr.net/npm/vanta@0.5.24/dist/vanta.trunk.min.js');
            tryInitVanta();
        };

        const tryInitVanta = () => {
            const el = localRef.current;
            const win = window as any;
            const hasVanta = !!win.VANTA?.TRUNK;
            const hasP5 = !!win.p5;

            if (el && hasVanta && hasP5) {
                try {
                    if (!vantaEffect) {
                        vantaEffect = win.VANTA.TRUNK({
                            el: el,
                            p5: win.p5,
                            mouseControls: false,
                            touchControls: false,
                            gyroControls: false,
                            minHeight: 200.0,
                            minWidth: 200.0,
                            scale: 1.0,
                            scaleMobile: 1.0,
                            color: 0x1fd5f9,
                            backgroundColor: 0x000000,
                            // FIX 5: chaos inicial reduzido de 4.0 → 1.5 (menos raios = menos GPU)
                            spacing: 2.5,
                            chaos: 1.5,
                        });
                        vantaRef.current = vantaEffect;
                    }
                } catch (e) {
                    log.error('Vanta Orb Init Error:', e);
                    attempts++;
                    if (attempts < 5) initTimer = setTimeout(tryInitVanta, 1000);
                }
            } else {
                attempts++;
                if (attempts < 20) initTimer = setTimeout(tryInitVanta, 500);
            }
        };

        if (isConnected) {
            setup();
        }

        return () => {
            if (initTimer) clearTimeout(initTimer);
            if (vantaEffect && typeof vantaEffect.destroy === 'function') {
                try {
                    vantaEffect.destroy();
                } catch (e) {
                    log.error("Erro ao destruir Vanta effect", e);
                }
            }
            if (vantaRef.current === vantaEffect) {
                vantaRef.current = null;
            }
        };
    }, [isConnected, color, vantaRef]);

    return (
        // FIX 2: canvas reduzido de 800×800 → 400×400; CSS scale visual preservado
        <div
            ref={localRef}
            style={{
                width: '400px',
                height: '400px',
                transform: 'scale(2.0) translateY(-5%)',
                transformOrigin: 'center center',
                willChange: 'transform',
            }}
        />
    );
};

// Responsável por monitorar o microfone e animar o Vanta (Throttled)
export const VantaController = ({ vantaRef, isConnected }: { vantaRef: React.MutableRefObject<any>; isConnected?: boolean }) => {
    const { audioTrack } = useVoiceAssistant();
    const volume = useTrackVolume(audioTrack);

    useEffect(() => {
        // FIX 3: sai imediatamente se desconectado — sem rAF ocioso
        if (!isConnected) return;
        const effect = vantaRef.current;
        if (!effect) return;

        let lastUpdate = 0;
        let frame = 0;
        let active = true;

        const updateChaos = (timestamp: number) => {
            if (!active) return;

            // FIX 3: para o loop se a aba estiver oculta ou se desconectou
            if (document.hidden) {
                frame = requestAnimationFrame(updateChaos);
                return;
            }

            // Throttle a 10 Hz (100 ms)
            if (timestamp - lastUpdate >= 100) {
                lastUpdate = timestamp;
                // FIX 5: baseChaos reduzido de 3.0 → 1.5
                const baseChaos = 1.5;
                const voiceChaos = (volume || 0) * 3.0;
                const finalChaos = baseChaos + voiceChaos;

                if (Math.abs((effect.options?.chaos ?? 0) - finalChaos) > 0.3) {
                    effect.setOptions({ chaos: finalChaos });
                }
            }
            frame = requestAnimationFrame(updateChaos);
        };

        frame = requestAnimationFrame(updateChaos);

        return () => {
            active = false;
            cancelAnimationFrame(frame);
        };
    }, [volume, vantaRef, isConnected]);

    return null;
};
