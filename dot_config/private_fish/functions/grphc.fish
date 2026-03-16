function grphc
    grph $argv | tee /dev/stderr | pbcopy
end
