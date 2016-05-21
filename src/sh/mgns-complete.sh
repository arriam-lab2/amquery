_mgns_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _MGNS_COMPLETE=complete $1 ) )
    return 0
}

complete -F _mgns_completion -o default mgns;
