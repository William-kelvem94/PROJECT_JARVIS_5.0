import { useState, useEffect } from 'react';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: (opts?: any) => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [name, setName] = useState('');
  const [tick, setTick] = useState(0);

  // Pulso lento para animar os anéis
  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 50);
    return () => clearInterval(id);
  }, []);

  return (
    <div ref={ref} className="relative flex flex-col items-center justify-center select-none">

      {/* ── Aura de fundo ──────────────────────────────────── */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div
          style={{ width: 480, height: 480, borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(29,163,185,0.12) 0%, transparent 70%)',
            animation: 'jarvis-glow-pulse 4s ease-in-out infinite' }}
        />
      </div>

      {/* ── Anéis orbitais ─────────────────────────────────── */}
      <div className="relative flex items-center justify-center" style={{ width: 280, height: 280 }}>

        {/* Anel externo – gira devagar */}
        <div style={{
          position: 'absolute', width: 260, height: 260, borderRadius: '50%',
          border: '1px solid rgba(29,163,185,0.25)',
          animation: 'jarvis-spin-slow 18s linear infinite',
        }}>
          {/* marcador */}
          <div style={{
            position: 'absolute', top: -3, left: '50%', transform: 'translateX(-50%)',
            width: 6, height: 6, borderRadius: '50%',
            background: '#1da3b9', boxShadow: '0 0 8px #1da3b9',
          }} />
        </div>

        {/* Anel médio – gira no sentido oposto */}
        <div style={{
          position: 'absolute', width: 200, height: 200, borderRadius: '50%',
          border: '1px solid rgba(29,163,185,0.18)',
          animation: 'jarvis-spin-slow 12s linear infinite reverse',
        }}>
          <div style={{
            position: 'absolute', bottom: -3, left: '50%', transform: 'translateX(-50%)',
            width: 5, height: 5, borderRadius: '50%',
            background: 'rgba(29,163,185,0.8)', boxShadow: '0 0 6px #1da3b9',
          }} />
        </div>

        {/* Anel interno */}
        <div style={{
          position: 'absolute', width: 148, height: 148, borderRadius: '50%',
          border: '1px solid rgba(29,163,185,0.30)',
          animation: 'jarvis-spin-slow 8s linear infinite',
        }} />

        {/* ── Núcleo ─────────────────────────────────────────── */}
        <div style={{
          position: 'relative', width: 112, height: 112, borderRadius: '50%',
          background: 'radial-gradient(circle at 36% 36%, rgba(29,163,185,0.22), rgba(13,148,136,0.10) 70%, transparent)',
          border: '1.5px solid rgba(29,163,185,0.55)',
          backdropFilter: 'blur(6px)',
          boxShadow: '0 0 32px rgba(29,163,185,0.35), inset 0 0 20px rgba(29,163,185,0.10)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          animation: 'jarvis-nucleus-pulse 3s ease-in-out infinite',
        }}>
          {/* Ícone J estilizado */}
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="24" cy="24" r="23" stroke="rgba(29,163,185,0.35)" strokeWidth="1" />
            <text x="50%" y="50%" dominantBaseline="central" textAnchor="middle"
              fontFamily="'Courier New', monospace" fontSize="22" fontWeight="700"
              fill="#1da3b9" style={{ filter: 'drop-shadow(0 0 6px #1da3b9)' }}>
              J
            </text>
          </svg>
        </div>
      </div>

      {/* ── Textos ─────────────────────────────────────────── */}
      <div className="mt-6 flex flex-col items-center gap-1">
        <h1 style={{
          fontFamily: "'Courier New', monospace",
          fontSize: '1.75rem',
          fontWeight: 700,
          letterSpacing: '0.35em',
          textTransform: 'uppercase',
          background: 'linear-gradient(135deg, #e0f7fa 0%, #1da3b9 50%, #80cbc4 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          filter: 'drop-shadow(0 0 10px rgba(29,163,185,0.5))',
        }}>
          JARVIS
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.36)', fontSize: '0.65rem', letterSpacing: '0.25em', textTransform: 'uppercase', fontFamily: 'monospace' }}>
          Neural Intelligence System · v5.0
        </p>
      </div>

      {/* ── Separador ──────────────────────────────────────── */}
      <div style={{ margin: '24px 0 20px', width: 220, height: 1, background: 'linear-gradient(to right, transparent, rgba(29,163,185,0.5), transparent)' }} />

      {/* ── Inputs ─────────────────────────────────────────── */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, width: 280 }}>
        <input
          type="text"
          autoComplete="off"
          placeholder="IDENTIFICAR USUÁRIO"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && name.trim() && onStartCall({ metadata: JSON.stringify({ user_name: name }) })}
          style={{
            width: '100%',
            background: 'rgba(255,255,255,0.04)',
            backdropFilter: 'blur(8px)',
            border: `1px solid ${name.trim() ? 'rgba(29,163,185,0.6)' : 'rgba(255,255,255,0.12)'}`,
            borderRadius: 12,
            padding: '12px 16px',
            fontSize: '0.78rem',
            letterSpacing: '0.15em',
            color: '#e0f7fa',
            textAlign: 'center',
            fontFamily: "'Courier New', monospace",
            outline: 'none',
            transition: 'border-color 0.2s, box-shadow 0.2s',
            boxShadow: name.trim() ? '0 0 12px rgba(29,163,185,0.2)' : 'none',
          }}
        />

        <button
          disabled={!name.trim()}
          onClick={() => onStartCall({ metadata: JSON.stringify({ user_name: name }) })}
          style={{
            width: '100%',
            height: 52,
            borderRadius: 12,
            border: '1px solid rgba(29,163,185,0.6)',
            background: name.trim()
              ? 'linear-gradient(135deg, rgba(29,163,185,0.90) 0%, rgba(13,148,136,0.85) 100%)'
              : 'rgba(29,163,185,0.10)',
            color: name.trim() ? '#ffffff' : 'rgba(255,255,255,0.25)',
            fontFamily: "'Courier New', monospace",
            fontSize: '0.75rem',
            fontWeight: 700,
            letterSpacing: '0.25em',
            textTransform: 'uppercase',
            cursor: name.trim() ? 'pointer' : 'not-allowed',
            transition: 'all 0.25s',
            boxShadow: name.trim() ? '0 8px 28px rgba(29,163,185,0.35)' : 'none',
          }}
          onMouseEnter={(e) => { if (name.trim()) (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 12px 36px rgba(29,163,185,0.55)'; }}
          onMouseLeave={(e) => { if (name.trim()) (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 8px 28px rgba(29,163,185,0.35)'; }}
        >
          {startButtonText || '▶  INICIAR SESSÃO'}
        </button>
      </div>

      {/* ── Rodapé ─────────────────────────────────────────── */}
      <p style={{
        marginTop: 28,
        color: 'rgba(255,255,255,0.18)',
        fontSize: '0.6rem',
        letterSpacing: '0.2em',
        textTransform: 'uppercase',
        fontFamily: 'monospace',
      }}>
        Neural Link · Awaiting Authorization
      </p>

      {/* ── Keyframes globais (injetados inline) ───────────── */}
      <style>{`
        @keyframes jarvis-spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes jarvis-glow-pulse { 0%,100% { opacity: 0.6; transform: scale(1); } 50% { opacity: 1; transform: scale(1.08); } }
        @keyframes jarvis-nucleus-pulse { 0%,100% { box-shadow: 0 0 32px rgba(29,163,185,0.35), inset 0 0 20px rgba(29,163,185,0.10); } 50% { box-shadow: 0 0 48px rgba(29,163,185,0.55), inset 0 0 28px rgba(29,163,185,0.18); } }
      `}</style>
    </div>
  );
};
