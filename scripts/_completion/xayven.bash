#!/usr/bin/env bash
# Tab-completion for the `xayven` umbrella + every `xayven-*` CLI.
#
# Source from your shell rc:
#     source /path/to/xayven-ui/scripts/_completion/xayven.bash
#
# Or wire it once per machine:
#     sudo install -m 644 xayven.bash /etc/bash_completion.d/xayven
#
# What it does:
#   - On the first word after `xayven`, complete with the list of
#     subcommands (`mail`, `calendar`, ...).
#   - On subsequent words, complete with the subcommand's first-token
#     subcommands (`list`, `show`, ...) which we cache by parsing the
#     tool's own --help output. Updates lazily; refresh by running
#     `_xayven_refresh_cache`.
#   - Same completion works for the individual `xayven-foo` scripts.

_xayven_scripts_dir() {
    # Resolve the scripts/ dir from the script that sources us. We assume
    # the user sourced the file directly out of scripts/_completion/.
    local self="${BASH_SOURCE[0]}"
    while [ -L "$self" ]; do self=$(readlink "$self"); done
    cd "$(dirname "$self")/.." && pwd
}

declare -A _XAYVEN_SUBS_CACHE=()

_xayven_refresh_cache() {
    local dir="$(_xayven_scripts_dir)"
    _XAYVEN_SUBS_CACHE=()
    # Prefer the project venv's Python so deps (bcrypt, sqlalchemy, ...)
    # resolve. Falls back to system `python3` for container installs.
    local py="$dir/../venv/bin/python"
    [ -x "$py" ] || py="$(command -v python3)"
    local f
    for f in "$dir"/xayven-*; do
        [ -x "$f" ] || continue
        case "$f" in *.bak|*.pyc|*.pre-*) continue ;; esac
        local name="$(basename "$f")"
        local sub="${name#xayven-}"
        local help_out
        help_out=$("$py" "$f" --help 2>/dev/null) || continue
        local commands
        commands=$(echo "$help_out" | grep -oE '\{[a-z0-9_,-]+\}' | head -1 \
            | tr -d '{}' | tr ',' ' ')
        _XAYVEN_SUBS_CACHE[$sub]="$commands"
    done
}

_xayven_complete() {
    [ ${#_XAYVEN_SUBS_CACHE[@]} -eq 0 ] && _xayven_refresh_cache

    local cur="${COMP_WORDS[COMP_CWORD]}"
    local cmd="${COMP_WORDS[0]}"

    # `xayven <tab>` → list every subcommand
    if [ "$cmd" = "xayven" ]; then
        if [ "$COMP_CWORD" -eq 1 ]; then
            local subs="${!_XAYVEN_SUBS_CACHE[@]} help"
            COMPREPLY=($(compgen -W "$subs" -- "$cur"))
            return 0
        fi
        # `xayven foo <tab>` — complete with foo's own subcommands
        local sub="${COMP_WORDS[1]}"
        # `xayven help <tab>` lists every subcommand
        if [ "$sub" = "help" ] && [ "$COMP_CWORD" -eq 2 ]; then
            COMPREPLY=($(compgen -W "${!_XAYVEN_SUBS_CACHE[*]}" -- "$cur"))
            return 0
        fi
        if [ "$COMP_CWORD" -eq 2 ]; then
            COMPREPLY=($(compgen -W "${_XAYVEN_SUBS_CACHE[$sub]}" -- "$cur"))
            return 0
        fi
        return 0
    fi

    # Direct `xayven-foo <tab>` (no umbrella)
    local sub="${cmd#xayven-}"
    if [ "$COMP_CWORD" -eq 1 ]; then
        COMPREPLY=($(compgen -W "${_XAYVEN_SUBS_CACHE[$sub]}" -- "$cur"))
        return 0
    fi
}

# Register the completion for every xayven-* script + the umbrella.
complete -F _xayven_complete xayven
for f in "$(_xayven_scripts_dir)"/xayven-*; do
    [ -x "$f" ] || continue
    case "$f" in *.bak|*.pyc|*.pre-*) continue ;; esac
    complete -F _xayven_complete "$(basename "$f")"
done

