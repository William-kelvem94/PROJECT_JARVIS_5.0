import { useState } from 'react';
import { motion } from 'motion/react';
import { Cpu, IdentificationCard, Play } from '@phosphor-icons/react';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: (opts?: { metadata?: string }) => void;
}

export const WelcomeView = ({ startButtonText, onStartCall }: WelcomeViewProps) => {
  const [name, setName] = useState('');

  const handleStart = () => {
    if (name.trim()) {
      onStartCall({ metadata: JSON.stringify({ user_name: name }) });
    }
  };

  return (
    <div className="relative flex flex-col items-center justify-center overflow-hidden py-12 select-none">
      {/* ── Aura de fundo ──────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{
          opacity: [0.4, 0.7, 0.4],
          scale: [1, 1.1, 1],
        }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        className="pointer-events-none absolute inset-0 flex items-center justify-center"
      >
        <div className="size-[480px] rounded-full bg-[radial-gradient(circle,rgba(0,242,255,0.15)_0%,transparent_70%)]" />
      </motion.div>

      {/* ── Anéis orbitais ─────────────────────────────────── */}
      <div className="relative flex size-[320px] items-center justify-center">
        {/* Anel externo */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          className="border-jarvis-cyan/20 absolute size-[280px] rounded-full border"
        >
          <div className="bg-jarvis-cyan absolute -top-1 left-1/2 size-2 -translate-x-1/2 rounded-full shadow-[0_0_10px_#00f2ff]" />
        </motion.div>

        {/* Anel médio */}
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
          className="border-jarvis-cyan/15 absolute size-[220px] rounded-full border"
        >
          <div className="bg-jarvis-cyan/60 absolute -bottom-1 left-1/2 size-1.5 -translate-x-1/2 rounded-full" />
        </motion.div>

        {/* Anel interno */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
          className="border-jarvis-cyan/10 absolute size-[160px] rounded-full border"
        />

        {/* ── Núcleo (Core) ─────────────────────────────────── */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 260, damping: 20 }}
          className="border-jarvis-cyan/40 from-jarvis-cyan/20 relative flex size-32 items-center justify-center rounded-full border-2 bg-radial-[at_35%_35%] to-transparent shadow-[0_0_40px_rgba(0,242,255,0.2),inset_0_0_20px_rgba(0,242,255,0.1)] backdrop-blur-md"
        >
          <div className="flex flex-col items-center">
            <Cpu
              size={42}
              weight="duotone"
              className="text-jarvis-cyan drop-shadow-[0_0_8px_#00f2ff]"
            />
          </div>
        </motion.div>
      </div>

      {/* ── Textos e Branding ──────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="mt-8 flex flex-col items-center gap-1"
      >
        <h1 className="jarvis-text-gradient font-mono text-3xl font-bold tracking-[0.4em] uppercase">
          Jarvis
        </h1>
        <p className="font-mono text-[10px] tracking-[0.3em] text-white/30 uppercase">
          Neural Command Interface · v5.0
        </p>
      </motion.div>

      {/* ── Separador ──────────────────────────────────────── */}
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: 240 }}
        transition={{ delay: 0.7, duration: 1 }}
        className="via-jarvis-cyan/40 my-8 h-px bg-linear-to-r from-transparent to-transparent"
      />

      {/* ── Formulário de Acesso ────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="flex w-[300px] flex-col gap-4"
      >
        <div className="group relative">
          <IdentificationCard className="group-focus-within:text-jarvis-cyan absolute top-1/2 left-4 size-5 -translate-y-1/2 text-white/20 transition-colors" />
          <input
            type="text"
            autoComplete="off"
            placeholder="IDENTIFICAR USUÁRIO"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleStart()}
            className="text-jarvis-cyan focus:border-jarvis-cyan/50 focus:ring-jarvis-cyan/20 w-full rounded-xl border border-white/10 bg-white/5 py-4 pr-4 pl-12 font-mono text-xs tracking-widest transition-all outline-none placeholder:text-white/10 focus:bg-white/[0.08] focus:ring-1"
          />
        </div>

        <motion.button
          whileHover={name.trim() ? { scale: 1.02 } : {}}
          whileTap={name.trim() ? { scale: 0.98 } : {}}
          disabled={!name.trim()}
          onClick={handleStart}
          className={`relative flex h-14 w-full items-center justify-center gap-3 overflow-hidden rounded-xl font-mono text-xs font-bold tracking-[0.2em] uppercase transition-all ${
            name.trim()
              ? 'bg-jarvis-cyan cursor-pointer text-black shadow-[0_0_20px_rgba(0,242,255,0.4)] hover:shadow-[0_0_30px_rgba(0,242,255,0.6)]'
              : 'cursor-not-allowed border border-white/5 bg-white/5 text-white/20'
          }`}
        >
          <Play weight="fill" className={name.trim() ? 'animate-pulse' : ''} />
          {startButtonText || 'Acessar Sistema'}

          {name.trim() && (
            <motion.div
              className="absolute inset-0 bg-white/20"
              initial={{ x: '-100%' }}
              animate={{ x: '100%' }}
              transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }}
              style={{ skewX: -20, width: '30%' }}
            />
          )}
        </motion.button>
      </motion.div>

      {/* ── Rodapé ─────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="mt-10 flex flex-col items-center gap-2"
      >
        <div className="flex items-center gap-2">
          <div className="bg-jarvis-cyan size-1.5 animate-pulse rounded-full shadow-[0_0_8px_#00f2ff]" />
          <span className="font-mono text-[9px] tracking-widest text-white/20 uppercase">
            Sistema Ativo · Aguardando Credenciais
          </span>
        </div>
      </motion.div>
    </div>
  );
};
