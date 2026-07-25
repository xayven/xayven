#compdef xayven xayven-backup xayven-calendar xayven-contacts xayven-cookbook xayven-docs xayven-gallery xayven-mail xayven-mcp xayven-memory xayven-notes xayven-personal xayven-preset xayven-research xayven-sessions xayven-signature xayven-skills xayven-tasks xayven-theme xayven-webhook
# Zsh tab-completion for the xayven umbrella + sub-CLIs.
#
# Drop in any directory on $fpath, e.g.:
#     fpath=(/path/to/xayven-ui/scripts/_completion $fpath)
#     autoload -U compinit; compinit
#
# Then `xayven <tab>` completes subcommands; `xayven mail <tab>`
# completes mail subcommands; `xayven-mail <tab>` works the same.

_xayven_scripts_dir() {
    local self="${(%):-%x}"
    while [[ -L "$self" ]]; do self="$(readlink "$self")"; done
    cd "${self:h}/.." && pwd
}

typeset -gA _xayven_subs

_xayven_refresh() {
    _xayven_subs=()
    local dir="$(_xayven_scripts_dir)"
    local py="$dir/../venv/bin/python"
    [[ -x "$py" ]] || py="$(command -v python3)"
    local f sub help_out commands
    for f in "$dir"/xayven-*; do
        [[ -x "$f" ]] || continue
        case "$f" in
            *.bak|*.pyc|*.pre-*) continue ;;
        esac
        sub="${${f:t}#xayven-}"
        help_out=$("$py" "$f" --help 2>/dev/null) || continue
        commands=$(echo "$help_out" | grep -oE '\{[a-z0-9_,-]+\}' | head -1 \
            | tr -d '{}' | tr ',' ' ')
        _xayven_subs[$sub]="$commands"
    done
}

_xayven() {
    [[ ${#_xayven_subs} -eq 0 ]] && _xayven_refresh

    local cmd="${words[1]}"

    if [[ "$cmd" == "xayven" ]]; then
        if (( CURRENT == 2 )); then
            local -a subs=(${(k)_xayven_subs} help)
            _describe 'subcommand' subs
            return
        fi
        local sub="${words[2]}"
        if [[ "$sub" == "help" ]] && (( CURRENT == 3 )); then
            local -a subs=(${(k)_xayven_subs})
            _describe 'subcommand' subs
            return
        fi
        if (( CURRENT == 3 )); then
            local -a sc=(${(s/ /)_xayven_subs[$sub]})
            _describe 'command' sc
            return
        fi
        return
    fi

    # xayven-foo <tab>
    local sub="${cmd#xayven-}"
    if (( CURRENT == 2 )); then
        local -a sc=(${(s/ /)_xayven_subs[$sub]})
        _describe 'command' sc
        return
    fi
}

_xayven "$@"

