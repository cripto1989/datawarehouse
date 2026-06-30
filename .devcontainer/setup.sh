#!/bin/bash
set -e  # Exit on error

echo "🔧 Setting up dev container..."

# Update apt and install system packages
echo "📦 Installing system packages..."
apt-get update
apt-get install -y zip zsh git

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dev dependencies
echo "📚 Installing development dependencies..."
pip install -r requirements-dev.txt

# Setup Oh My Zsh (only if not already installed)
if [ ! -d "$HOME/.oh-my-zsh" ]; then
  echo "🎨 Setting up Oh My Zsh..."
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
else
  echo "✓ Oh My Zsh already installed, skipping..."
fi

# Install forgit plugin
echo "🔍 Installing forgit plugin..."
FORGIT_DIR="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/forgit"
if [ ! -d "$FORGIT_DIR" ]; then
  git clone https://github.com/wfxr/forgit.git "$FORGIT_DIR"
  sed -i 's/plugins=(git)/plugins=(git forgit)/' "$HOME/.zshrc"
else
  echo "✓ Forgit already installed, skipping..."
fi

# Install fzf
echo "🔎 Installing fzf..."
if [ ! -d "$HOME/.fzf" ]; then
  git clone --depth 1 https://github.com/junegunn/fzf.git "$HOME/.fzf"
  "$HOME/.fzf/install" --all
else
  echo "✓ fzf already installed, skipping..."
fi

# Set default shell to zsh
echo "🐚 Setting default shell to zsh..."
chsh -s /bin/zsh

echo "✅ Dev container setup complete!"
