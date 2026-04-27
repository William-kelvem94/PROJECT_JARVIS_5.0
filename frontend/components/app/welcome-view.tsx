import { useState } from 'react';
import { motion } from 'motion/react';
import { Cpu, IdentificationCard, Play } from '@phosphor-icons/react';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: (opts?: { metadata?: string }) => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
}: WelcomeViewProps) => {
  const [name, setName] = useState('');

  const handleStart = () => {
    if (name.trim()) {
      onStartCall({ metadata: JSON.stringify({ user_name: name }) });
    }
  };

  return (
    <div className="relative flex flex-col items-center justify-center select-none overflow-hidden py-12">
      {/* ── Aura de fundo ──────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ 
          opacity: [0.4, 0.7, 0.4],
          scale: [1, 1.1, 1],
        }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        className="pointer-events-none absolute inset-0 flex items-center justify-center"
      >
        <div className="size-[480px] rounded-full bg-[radial-gradient(circle,rgba(0,242,255,0.15)_0%,transparent_70%)]" />
      </motion.div>

      {/* ── Anéis orbitais ─────────────────────────────────── */}
      <div className="relative flex size-[320px] items-center justify-center">
        {/* Anel externo */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute size-[280px] rounded-full border border-jarvis-cyan/20"
        >
          <div className="absolute -top-1 left-1/2 size-2 -translate-x-1/2 rounded-full bg-jarvis-cyan shadow-[0_0_10px_#00f2ff]" />
        </motion.div>

        {/* Anel médio */}
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute size-[220px] rounded-full border border-jarvis-cyan/15"
        >
          <div className="absolute -bottom-1 left-1/2 size-1.5 -translate-x-1/2 rounded-full bg-jarvis-cyan/60" />
        </motion.div>

        {/* Anel interno */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          className="absolute size-[160px] rounded-full border border-jarvis-cyan/10"
        />

        {/* ── Núcleo (Core) ─────────────────────────────────── */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 260, damping: 20 }}
          className="relative flex size-32 items-center justify-center rounded-full border-2 border-jarvis-cyan/40 bg-radial-[at_35%_35%] from-jarvis-cyan/20 to-transparent backdrop-blur-md shadow-[0_0_40px_rgba(0,242,255,0.2),inset_0_0_20px_rgba(0,242,255,0.1)]"
        >
          <div className="flex flex-col items-center">
            <Cpu size={42} weight="duotone" className="text-jarvis-cyan drop-shadow-[0_0_8px_#00f2ff]" />
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
        className="my-8 h-px bg-linear-to-r from-transparent via-jarvis-cyan/40 to-transparent"
      />

      {/* ── Formulário de Acesso ────────────────────────────── */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="flex w-[300px] flex-col gap-4"
      >
        <div className="relative group">
          <IdentificationCard className="absolute top-1/2 left-4 size-5 -translate-y-1/2 text-white/20 transition-colors group-focus-within:text-jarvis-cyan" />
          <input
            type="text"
            autoComplete="off"
            placeholder="IDENTIFICAR USUÁRIO"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleStart()}
            className="w-full rounded-xl border border-white/10 bg-white/5 py-4 pr-4 pl-12 font-mono text-xs tracking-widest text-jarvis-cyan outline-none transition-all placeholder:text-white/10 focus:border-jarvis-cyan/50 focus:bg-white/[0.08] focus:ring-1 focus:ring-jarvis-cyan/20"
          />
        </div>

        <motion.button
          whileHover={name.trim() ? { scale: 1.02 } : {}}
          whileTap={name.trim() ? { scale: 0.98 } : {}}
          disabled={!name.trim()}
          onClick={handleStart}
          className={`relative flex h-14 w-full items-center justify-center gap-3 overflow-hidden rounded-xl font-mono text-xs font-bold tracking-[0.2em] uppercase transition-all
            ${name.trim() 
              ? 'bg-jarvis-cyan text-black shadow-[0_0_20px_rgba(0,242,255,0.4)] hover:shadow-[0_0_30px_rgba(0,242,255,0.6)] cursor-pointer' 
              : 'bg-white/5 text-white/20 cursor-not-allowed border border-white/5'
            }`}
        >
          <Play weight="fill" className={name.trim() ? 'animate-pulse' : ''} />
          {startButtonText || 'Acessar Sistema'}
          
          {name.trim() && (
            <motion.div 
              className="absolute inset-0 bg-white/20"
              initial={{ x: '-100%' }}
              animate={{ x: '100%' }}
              transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
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
          <div className="size-1.5 animate-pulse rounded-full bg-jarvis-cyan shadow-[0_0_8px_#00f2ff]" />
          <span className="font-mono text-[9px] tracking-widest text-white/20 uppercase">
            Sistema Ativo · Aguardando Credenciais
          </span>
        </div>
      </motion.div>
    </div>
  );
};
