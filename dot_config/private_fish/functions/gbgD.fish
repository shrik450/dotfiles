function gbgD --description "Delete local branches whose upstream branch is gone"
    set -l deletable
    set -l blocked

    for line in (git for-each-ref --format='%(refname:short)%09%(upstream:track)%09%(worktreepath)' refs/heads)
        set -l fields (string split \t -- $line)
        test "$fields[2]" = '[gone]'; or continue

        if test -z "$fields[3]"
            set -a deletable $fields[1]
        else
            set -a blocked (string join \t -- $fields[1] $fields[3])
        end
    end

    for entry in $blocked
        set -l fields (string split \t -- $entry)
        echo "Cannot delete $fields[1]: it is checked out in the worktree $fields[2]" >&2
        echo "Check out another branch there, or remove the worktree, then run gbgD again." >&2
    end

    if test (count $deletable) -gt 0
        git branch -D $deletable
    end
end
