'use client';

import React, { useEffect, useRef } from 'react';
import { useVoiceAssistant, useTrackVolume } from '@livekit/components-react';

// Converte cor hex-number (ex: 0x1da3b9) para string CSS rgb
function hexNumToRgb(hex: number): [number, number, number] {
    return [(hex >> 16) & 0xff, (hex >> 8) & 0xff, hex & 0xff];
}

/**
 * JarvisOrb — visualizador Canvas 2D puro.
 * Zero WebGL, zero Three.js, zero p5.js.
 * Anéis concêntricos que pulsam com o volume do agente.
 */
export const VantaOrb = ({
    isConnected,
    color,
    vantaRef,
}: {
    isConnected: boolean;
    color: number;
    vantaRef: React.MutableRefObject<any>;
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const stateRef = useRef({ volume: 0, active: false, frame: 0, color });

    // Expõe setter de volume para VantaController (mesmo contrato que o Vanta)
    useEffect(() => {
        vantaRef.current = {
            setVolume: (v: number) => { stateRef.current.volume = v; },
            setColor: (c: number) => { stateRef.current.color = c; },
        };
        return () => { vantaRef.current = null; };
    }, [vantaRef]);

    // Atualiza cor quando a prop muda (persona switch)
    useEffect(() => {
        stateRef.current.color = color;
    }, [color]);

    useEffect(() => {
        if (!isConnected) return;
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const SIZE = 520;
        canvas.width = SIZE;
        canvas.height = SIZE;
        const cx = SIZE / 2;
        const cy = SIZE / 2;

        stateRef.current.active = true;
        let t = 0;

        const draw = () => {
            if (!stateRef.current.active) return;
            if (document.hidden) {
                stateRef.current.frame = requestAnimationFrame(draw);
                return;
            }

            t += 0.012;
            const vol = stateRef.current.volume;           // 0–1
            const [r, g, b] = hexNumToRgb(stateRef.current.color);

            // Limpa com fade — cria efeito de rastro suave
            ctx.fillStyle = 'rgba(0,0,0,0.18)';
            ctx.fillRect(0, 0, SIZE, SIZE);

            // Parâmetros reativos ao volume
            const ringCount = 22;
            const baseRadius = 52 + vol * 18;
            const spacing = 9.5 + vol * 2.2;
            const amp = 2.8 + vol * 14;       // distorção ondulatória
            const freq = 6 + vol * 4;          // frequência da onda

            for (let i = 0; i < ringCount; i++) {
                const progress = i / ringCount;
                const radius = baseRadius + i * spacing;
                const alpha = (1 - progress * 0.75) * (0.35 + vol * 0.55);
                const lineWidth = Math.max(0.5, 1.4 - progress * 0.9 + vol * 0.8);
                const phaseOffset = t * (1 + progress * 0.6) + i * 0.28;

                ctx.beginPath();
                ctx.strokeStyle = `rgba(${r},${g},${b},${alpha})`;
                ctx.lineWidth = lineWidth;

                const steps = Math.max(80, Math.floor(radius * 1.4));
                for (let s = 0; s <= steps; s++) {
                    const angle = (s / steps) * Math.PI * 2;
                    const wobble = amp * Math.sin(freq * angle + phaseOffset);
                    const px = cx + (radius + wobble) * Math.cos(angle);
                    const py = cy + (radius + wobble) * Math.sin(angle);
                    s === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
                }
                ctx.closePath();
                ctx.stroke();
            }

            // Núcleo — círculo sólido pequeno no centro
            const coreR = 20 + vol * 10;
            const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreR);
            grad.addColorStop(0, `rgba(${r},${g},${b},${0.55 + vol * 0.4})`);
            grad.addColorStop(1, `rgba(${r},${g},${b},0)`);
            ctx.beginPath();
            ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
            ctx.fillStyle = grad;
            ctx.fill();

            stateRef.current.frame = requestAnimationFrame(draw);
        };

        stateRef.current.frame = requestAnimationFrame(draw);

        return () => {
            stateRef.current.active = false;
            cancelAnimationFrame(stateRef.current.frame);
            ctx.clearRect(0, 0, SIZE, SIZE);
        };
    }, [isConnected]);

    if (!isConnected) return null;

    return (
        <canvas
            ref={canvasRef}
            style={{
                display: 'block',
                width: '100vmin',
                height: '100vmin',
                maxWidth: '760px',
                maxHeight: '760px',
                imageRendering: 'auto',
            }}
        />
    );
};

/**
 * VantaController — passa o volume do agente para o JarvisOrb via ref
 * (mantém a mesma interface do componente anterior)
 */
export const VantaController = ({
    vantaRef,
    isConnected,
}: {
    vantaRef: React.MutableRefObject<any>;
    isConnected?: boolean;
}) => {
    const { audioTrack } = useVoiceAssistant();
    const volume = useTrackVolume(audioTrack);

    useEffect(() => {
        if (!isConnected) return;
        vantaRef.current?.setVolume(volume ?? 0);
    }, [volume, vantaRef, isConnected]);

    return null;
};
