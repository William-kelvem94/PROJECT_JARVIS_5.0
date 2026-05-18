#!/usr/bin/env bash
# ensure nvm and node 20 installed, then rebuild frontend deps
export NVM_DIR="$HOME/.nvm"
if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
fi
# load nvm
. "$NVM_DIR/nvm.sh"
# install/use node 20
nvm install 20
nvm alias default 20
nvm use 20
node -v
# rebuild frontend
cd /mnt/e/Documents/GitHub/PROJECT_JARVIS_5.0/frontend
rm -rf node_modules package-lock.json pnpm-lock.yaml
npm install
