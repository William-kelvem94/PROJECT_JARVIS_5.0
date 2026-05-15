'use client';

import { useEffect, useState } from 'react';

interface Messages {
  [key: string]: string | Messages;
}

const LOCALE_MAP: Record<string, () => Promise<Messages>> = {
  'pt-BR': () => import('@/messages/pt-BR.json').then((m) => m.default),
  'en-US': () => import('@/messages/en-US.json').then((m) => m.default),
};

const FALLBACK_LOCALE = 'pt-BR';

export function useI18n() {
  const [locale, setLocale] = useState(FALLBACK_LOCALE);
  const [messages, setMessages] = useState<Messages>({});

  useEffect(() => {
    const load = async () => {
      const loader = LOCALE_MAP[locale] || LOCALE_MAP[FALLBACK_LOCALE];
      const msgs = await loader();
      setMessages(msgs);
    };
    load();
  }, [locale]);

  const t = (key: string, params?: Record<string, string | number>): string => {
    const keys = key.split('.');
    let value: string | Messages | undefined = messages;
    for (const k of keys) {
      value = typeof value === 'object' ? value[k] : undefined;
    }
    if (typeof value !== 'string') return key;
    if (params) {
      return value.replace(/\{(\w+)\}/g, (_, k) => String(params[k] ?? `{${k}}`));
    }
    return value;
  };

  return { t, locale, setLocale };
}
