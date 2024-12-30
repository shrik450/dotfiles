function gcan! --wraps='git commit --verbose --all --no-edit --amend' --description 'alias gcan! git commit --verbose --all --no-edit --amend'
  git commit --verbose --all --no-edit --amend $argv
        
end
