function gpf --wraps='git push --force-with-lease --force-if-includes' --description 'alias gpf git push --force-with-lease --force-if-includes'
  git push --force-with-lease --force-if-includes $argv
        
end
