function upt --wraps='uv run -m pytest' --description 'alias upt uv run -m pytest'
    uv run -m pytest $argv
end
