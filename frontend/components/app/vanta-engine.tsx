'use client';

import React, { useEffect, useRef } from 'react';
import { useVoiceAssistant, useTrackVolume } from '@livekit/components-react';

function hexNumToRgb(hex: number): [number, number, number] {
    return [(hex >> 16) & 0xff, (hex >> 8) & 0xff, hex & 0xff];
}

/**
 * JarvisOrb — Esfera holográfica 3D com anéis orbitais projetados em perspectiva.
 * Canvas 2D puro: usa ctx.ellipse() para projetar anéis 3D em perspectiva isométrica.
 * ~12 draw-calls por frame vs ~1760 operações de vértice do visualizador anterior.
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

    useEffect(() => {
        vantaRef.current = {
            setVolume: (v: number) => { stateRef.current.volume = v; },
            setColor: (c: number) => { stateRef.current.color = c; },
        };
        return () => { vantaRef.current = null; };
    }, [vantaRef]);

    useEffect(() => {
        stateRef.current.color = color;
    }, [color]);

    useEffect(() => {
        if (!isConnected) return;
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const SIZE = 500;
        canvas.width = SIZE;
        canvas.height = SIZE;
        const cx = SIZE / 2;
        const cy = SIZE / 2;

        stateRef.current.active = true;
        let t = 0;
        let smoothVol = 0;

        /**
         * Cada anel é definido por:
         *   speed      — velocidade de rotação do plano do anel (rad/s escalonado por dt)
         *   tiltBase   — inclinação base do anel em relação ao eixo Z (0 = círculo perfeito, PI/2 = linha)
         *   tiltDrift  — quanto a inclinação oscila ao longo do tempo (efeito "precessão")
         *   phase      — fase inicial
         *   baseR      — raio base em px (canvas 500×500)
         *   alpha      — opacidade base
         *   lw         — espessura da linha base
         *   dotCount   — quantos pontos luminosos orbitam neste anel
         */
        const RINGS = [
            { speed: 0.22,  tiltBase: 1.26, tiltDrift: 0.10, phase: 0,              baseR: 190, alpha: 0.75, lw: 1.8, dotCount: 2 },
            { speed: -0.15, tiltBase: 0.90, tiltDrift: 0.14, phase: Math.PI / 2.8,  baseR: 168, alpha: 0.58, lw: 1.4, dotCount: 2 },
            { speed: 0.30,  tiltBase: 0.42, tiltDrift: 0.08, phase: Math.PI * 0.75, baseR: 150, alpha: 0.42, lw: 1.2, dotCount: 0 },
            { speed: -0.10, tiltBase: 1.45, tiltDrift: 0.06, phase: Math.PI * 1.5,  baseR: 210, alpha: 0.28, lw: 1.0, dotCount: 1 },
        ];

        /** Desenha um anel 3D como elipse projetada, com halo suave sem ctx.filter */
        function drawRing(
            radiusX: number, radiusY: number, screenRot: number,
            r: number, g: number, b: number,
            alpha: number, lw: number
        ) {
            // Halo: 2 passadas largas e translúcidas
            for (let pass = 2; pass >= 1; pass--) {
                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(screenRot);
                ctx.beginPath();
                ctx.ellipse(0, 0, radiusX, radiusY, 0, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(${r},${g},${b},${alpha * pass * 0.12})`;
                ctx.lineWidth = lw + pass * 7;
                ctx.stroke();
                ctx.restore();
            }
            // Anel nítido
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(screenRot);
            ctx.beginPath();
            ctx.ellipse(0, 0, radiusX, radiusY, 0, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(${r},${g},${b},${alpha})`;
            ctx.lineWidth = lw;
            ctx.stroke();
            ctx.restore();
        }

        const draw = () => {
            if (!stateRef.current.active) return;
            if (document.hidden) {
                stateRef.current.frame = requestAnimationFrame(draw);
                return;
            }

            t += 0.008;
            smoothVol += (stateRef.current.volume - smoothVol) * 0.08;
            const v = smoothVol;

            const [r, g, b] = hexNumToRgb(stateRef.current.color);

            ctx.clearRect(0, 0, SIZE, SIZE);

            // Névoa ambiente de fundo — gradiente radial simples
            const bgGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, SIZE * 0.52);
            bgGrad.addColorStop(0,   `rgba(${r},${g},${b},${0.05 + v * 0.08})`);
            bgGrad.addColorStop(0.6, `rgba(${r},${g},${b},0.01)`);
            bgGrad.addColorStop(1,   'rgba(0,0,0,0)');
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, SIZE, SIZE);

            // ── Anéis orbitais ──────────────────────────────────────────────
            for (const ring of RINGS) {
                const angle = t * ring.speed + ring.phase;

                // Inclinação precessiona suavemente ao longo do tempo
                const tilt    = ring.tiltBase + Math.sin(t * 0.18 + ring.phase) * ring.tiltDrift;
                const scaleY  = Math.max(0.08, Math.abs(Math.cos(tilt)));
                const radiusX = ring.baseR + v * 14;
                const radiusY = radiusX * scaleY;
                const alpha   = ring.alpha + v * 0.25;
                const lw      = ring.lw + v * 2.0;

                drawRing(radiusX, radiusY, angle, r, g, b, alpha, lw);

                // Pontos luminosos que orbitam no anel
                for (let d = 0; d < ring.dotCount; d++) {
                    const da = (d / ring.dotCount) * Math.PI * 2 + angle * 2.2;
                    // Posição na elipse projetada
                    const dx = cx + radiusX * Math.cos(da) * Math.cos(angle)
                                  - radiusY * Math.sin(da) * Math.sin(angle);
                    const dy = cy + radiusX * Math.cos(da) * Math.sin(angle)
                                  + radiusY * Math.sin(da) * Math.cos(angle);
                    const dotR = 3 + v * 3;
                    // Halo do ponto
                    const dotGrad = ctx.createRadialGradient(dx, dy, 0, dx, dy, dotR * 3);
                    dotGrad.addColorStop(0, `rgba(${r},${g},${b},${alpha * 1.2})`);
                    dotGrad.addColorStop(1, 'rgba(0,0,0,0)');
                    ctx.beginPath();
                    ctx.arc(dx, dy, dotR * 3, 0, Math.PI * 2);
                    ctx.fillStyle = dotGrad;
                    ctx.fill();
                    // Núcleo do ponto
                    ctx.beginPath();
                    ctx.arc(dx, dy, dotR, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(255,255,255,${0.7 + v * 0.3})`;
                    ctx.fill();
                }
            }

            // ── Esfera central ─────────────────────────────────────────────
            const coreR = 48 + v * 24;

            // Corona exterior (glow expandido)
            const coronaGrad = ctx.createRadialGradient(cx, cy, coreR * 0.4, cx, cy, coreR * 2.6);
            coronaGrad.addColorStop(0,   `rgba(${r},${g},${b},${0.28 + v * 0.38})`);
            coronaGrad.addColorStop(0.45,`rgba(${r},${g},${b},${0.08 + v * 0.10})`);
            coronaGrad.addColorStop(1,   'rgba(0,0,0,0)');
            ctx.beginPath();
            ctx.arc(cx, cy, coreR * 2.6, 0, Math.PI * 2);
            ctx.fillStyle = coronaGrad;
            ctx.fill();

            // Corpo da esfera com gradiente offset → aparência 3D (fonte de luz no canto superior esquerdo)
            const lx = cx - coreR * 0.38;
            const ly = cy - coreR * 0.38;
            const sphereGrad = ctx.createRadialGradient(lx, ly, coreR * 0.04, cx, cy, coreR);
            sphereGrad.addColorStop(0,    `rgba(255,255,255,${0.82 + v * 0.18})`);
            sphereGrad.addColorStop(0.18, `rgba(${r},${g},${b},0.98)`);
            sphereGrad.addColorStop(0.62, `rgba(${r},${g},${b},0.60)`);
            sphereGrad.addColorStop(1,    `rgba(${Math.round(r * 0.25)},${Math.round(g * 0.25)},${Math.round(b * 0.25)},0.10)`);
            ctx.beginPath();
            ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
            ctx.fillStyle = sphereGrad;
            ctx.fill();

            // Reflexo especular pequeno (realismo 3D)
            const specR = coreR * 0.28;
            const sx = cx - coreR * 0.32;
            const sy = cy - coreR * 0.30;
            const specGrad = ctx.createRadialGradient(sx, sy, 0, sx, sy, specR);
            specGrad.addColorStop(0, `rgba(255,255,255,${0.55 + v * 0.25})`);
            specGrad.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.beginPath();
            ctx.arc(sx, sy, specR, 0, Math.PI * 2);
            ctx.fillStyle = specGrad;
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
                maxWidth: '720px',
                maxHeight: '720px',
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
