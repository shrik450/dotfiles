function gbgD
    set -lx LANG C

    git branch -vv | string match -r ".*: gone\].*" | string trim -l | string replace -r "^\* " "" | string replace -r ' .*$' '' | while read branch
        git branch -D $branch
    end
end
