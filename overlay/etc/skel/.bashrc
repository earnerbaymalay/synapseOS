# ==============================================================================
# ~/.bashrc — SynapseOS Cyberdeck Shell Initialization
# ==============================================================================

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Ensure user local binaries are in PATH
export PATH="$HOME/.local/bin:$PATH"
export FUNCNEST=100

# --- 1. History & Readline Navigation ---
HISTCONTROL=ignoreboth:erasedups
HISTSIZE=10000
HISTFILESIZE=20000
shopt -s histappend
shopt -s checkwinsize

bind '"\e[A":history-search-backward'
bind '"\e[B":history-search-forward'

# --- 2. Modern CLI Replacements (eza, bat, dust, lazygit, yazi) ---
if command -v eza >/dev/null 2>&1; then
    alias ls='eza --icons=always --color=always'
    alias ll='eza -la --icons=always --color=always'
    alias lt='eza --tree --level=2 --icons=always'
else
    alias ls='ls --color=auto'
    alias ll='ls -lav --ignore=..'
fi

if command -v bat >/dev/null 2>&1; then
    alias cat='bat --style=plain'
fi

alias lg='lazygit'
alias grep='grep --color=auto'
alias ip='ip -color=auto'
alias diff='diff --color=auto'
if [[ -n "${WAYLAND_DISPLAY:-}" ]] && command -v wl-copy >/dev/null 2>&1; then
    alias clip='wl-copy'
    alias clippaste='wl-paste'
else
    alias clip='xclip -selection clipboard'
    alias clippaste='xclip -selection clipboard -o'
fi

# Yazi directory-changing wrapper
y() {
    local tmp
    tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
    local cwd
    yazi "$@" --cwd-file="$tmp"
    if cwd="$(command cat -- "$tmp")" && [[ -n "$cwd" && "$cwd" != "$PWD" ]]; then
        builtin cd -- "$cwd" || return
    fi
    rm -f -- "$tmp"
}

# --- 3. Python uv Virtualenv Helper ---
venv() {
    if [[ ! -d ".venv" ]]; then
        echo "[SynapseOS] Creating isolated virtualenv at .venv via uv..."
        uv venv .venv
    fi
    # shellcheck disable=SC1091
    source .venv/bin/activate
}
alias activate='source .venv/bin/activate'

# --- 4. Synapse AI Core & LLM Quickfire Suite ---
export SYNAPSE_GATEWAY_URL="http://127.0.0.1:8000"
export SYNAPSE_CONFIG="$HOME/.synapse/config.toml"
export OBSIDIAN_AI_VAULT="$HOME/Obsidian/AI-Knowledge-Base"

alias syn-sync='synapse sync --once'
alias syn-doc='synapse doctor'
alias syn-hud='synapse hud'
alias syn-vibe='synapse vibe'
alias syn-mem='synapse mem'

alias quickfire='quickfire'
alias qf='quickfire'
alias qf-theme='quickfire-theme'
alias agy-palette='quickfire'

# --- 5. Local LLM (Ollama) Orchestration Helpers ---
ask-ollama() {
    local model="qwen2.5-coder:latest"
    local positional=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -m|--model)
                if [[ $# -lt 2 || -z "$2" ]]; then
                    echo "Error: -m/--model requires a model argument" >&2
                    return 1
                fi
                model="$2"
                shift 2
                ;;
            --)
                shift
                positional+=("$@")
                break
                ;;
            *)
                positional+=("$1")
                shift
                ;;
        esac
    done

    set -- "${positional[@]}"

    if [[ ! -t 0 ]]; then
        local stdin_data
        stdin_data="$(command cat)"
        if [[ -n "$stdin_data" && -n "$*" ]]; then
            printf "%s\n\nTask: %s\n" "$stdin_data" "$*" | ollama run "$model"
        elif [[ -n "$stdin_data" ]]; then
            printf "%s\n" "$stdin_data" | ollama run "$model"
        elif [[ -n "$*" ]]; then
            ollama run "$model" "$*"
        else
            echo "Usage: ask-ollama [-m model] [prompt] (or pipe via stdin)" >&2
            return 1
        fi
    else
        if [[ $# -gt 0 ]]; then
            ollama run "$model" "$*"
        else
            ollama run "$model"
        fi
    fi
}

alias ask-qwen='ask-ollama -m qwen2.5-coder:latest'
alias ask-llama='ask-ollama -m llama3.2:latest'
alias ask-dolphin='ask-ollama -m dolphin-mistral:latest'
alias ask-hermes='ask-ollama -m nous-hermes2:latest'
alias ask-ab='ask-ollama -m qwen-abliterated:latest'
alias '?'='ask-qwen'

alias ollama-warm='curl -s -X POST http://127.0.0.1:11434/api/generate -d '\''{"model": "qwen2.5-coder:latest"}'\'' >/dev/null 2>&1 &'

ollama-stop() {
    if [[ -n "${1:-}" ]]; then
        ollama stop "$1"
    else
        local running
        running=$(ollama ps 2>/dev/null | awk 'NR>1 {print $1}')
        if [[ -n "$running" ]]; then
            echo "Unloading resident models from RAM: $running"
            for m in $running; do
                ollama stop "$m"
            done
        else
            echo "No resident Ollama models currently loaded."
        fi
    fi
}
alias ollama-flush='ollama-stop'

# --- 6. Security & System Telemetry Shortcuts ---
alias ananicy-status='systemctl status ananicy-cpp --no-pager'
alias zram-status='zramctl'
alias syn-status='systemctl status synapse --no-pager'
alias sec-dns='resolvectl status'

# --- 7. Interactive Shell Enhancements (ble.sh, Starship, Zoxide, FZF) ---
if [[ -f /usr/share/blesh/ble.sh ]]; then
    source /usr/share/blesh/ble.sh
elif [[ -f "$HOME/.local/share/blesh/ble.sh" ]]; then
    source "$HOME/.local/share/blesh/ble.sh"
fi

if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
fi

if command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init bash)"
fi

if [[ -f /usr/share/fzf/key-bindings.bash ]]; then
    source /usr/share/fzf/key-bindings.bash
    source /usr/share/fzf/completion.bash
fi

if command -v fastfetch >/dev/null 2>&1; then
    fastfetch
fi
