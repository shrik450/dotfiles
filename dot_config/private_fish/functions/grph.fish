function grph --wraps='git rev-parse HEAD' --description 'alias grph git rev-parse HEAD'
    git rev-parse HEAD $argv
end
