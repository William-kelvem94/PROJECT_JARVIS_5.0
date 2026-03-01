'use client';

import React, { useEffect, useRef } from 'react';
import { log } from '@/lib/logger';
import { useVoiceAssistant, useTrackVolume } from '@livekit/components-react';

// Responsável por instanciar a esfera e carregar os scripts
export const VantaOrb = ({ isConnected, color, vantaRef }: { isConnected: boolean, color: number, vantaRef: React.MutableRefObject<any> }) => {
    const localRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        let vantaEffect: any = null;
        let attempts = 0;
        let initTimer: NodeJS.Timeout;

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

        const setup = async () => {
            // Dependências pesadas carregadas apenas quando o componente monta
            await loadScript('https://cdnjs.cloudflare.com/ajax/libs/three.js/r152/three.min.js');
            await loadScript('https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js');
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
                            color: 0x1fd5f9, // Jarvis Cyan
                            backgroundColor: 0x000000,
                            spacing: 1.5, // Fios mais densos e luxuosos
                            chaos: 4.0, // Mais movimento inicial
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
        <div
            ref={localRef}
            className="w-[800px] h-[800px]" // Aumentado para 800px para mais detalhe
            style={{
                transform: 'scale(1.0) translateY(-5%)',
                transformOrigin: 'center center',
            }}
        />
    );
};

// Responsável por monitorar o microfone e animar o Vanta (Throttled)
export const VantaController = ({ vantaRef, isConnected }: { vantaRef: React.MutableRefObject<any>; isConnected?: boolean }) => {
    const { audioTrack } = useVoiceAssistant();
    const volume = useTrackVolume(audioTrack);

    useEffect(() => {
        if (!isConnected) return;
        const effect = vantaRef.current;
        if (!effect) return;

        let lastUpdate = 0;
        let frame = 0;

        const updateChaos = (timestamp: number) => {
            // Se a página não estiver visível, não gastar recursos
            if (document.hidden) {
                frame = requestAnimationFrame(updateChaos);
                return;
            }

            // Updates ultra-throttled to 10Hz (100ms) - Ultra leve
            if (timestamp - lastUpdate >= 100) {
                lastUpdate = timestamp;
                const baseChaos = 3.0;
                const voiceChaos = (volume || 0) * 4.0; // Reduzi para 4 para ser mais estável
                const finalChaos = baseChaos + voiceChaos;

                // Só atualiza se for uma mudança realmente perceptível (> 0.4)
                if (Math.abs(effect.options.chaos - finalChaos) > 0.4) {
                    effect.setOptions({ chaos: finalChaos });
                }
            }
            frame = requestAnimationFrame(updateChaos);
        };

        frame = requestAnimationFrame(updateChaos);

        // Cleanup de Animação
        return () => cancelAnimationFrame(frame);
    }, [volume, vantaRef, isConnected]);

    return null;
};
