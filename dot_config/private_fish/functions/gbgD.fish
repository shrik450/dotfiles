function gbgD --wraps="LANG=C git branch --no-color -vv | grep \": gone\\]\" | cut -c 3- | awk '\\''{print }'\\'' | xargs git branch -D" --description "alias gbgD LANG=C git branch --no-color -vv | grep \": gone\\]\" | cut -c 3- | awk '\\''{print }'\\'' | xargs git branch -D"
    set -lx LANG C

    git branch -vv | string match -r ".*: gone\].*" | string trim -l | string replace -r "^\* " "" | string replace -r ' .*$' '' | while read branch
        git branch -D $branch
    end
end
