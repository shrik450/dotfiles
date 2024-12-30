function take
    if test (count $argv) -ne 1
        echo "Usage: take <directory-name>"
        return 1
    end
    
    mkdir -p $argv[1]; and cd $argv[1]
end
