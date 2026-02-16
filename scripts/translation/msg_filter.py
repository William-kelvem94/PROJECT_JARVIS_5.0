#!/usr/bin/env python3
import sys

translations = {}
with open("commit_translations_map.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "|||" in line:
            hash_c, trans = line.strip().split("|||", 1)
            translations[hash_c] = trans

commit_msg = sys.stdin.read().strip()

# Tenta obter hash do commit atual (não disponível diretamente no msg-filter)
# Mas podemos comparar a mensagem
for hash_c, trans in translations.items():
    if hash_c in commit_msg or True:  # Aplica para todos
        print(trans)
        sys.exit(0)

print(commit_msg)
