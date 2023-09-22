vim.cmd([[
    autocmd FileType python set ft=python.django
    autocmd FileType html set ft=htmldjango
]])

table.insert(require('dap').configurations['python.django'], {
    type = 'python',
    request = 'attach',
    name = 'Attach remote docker',
    connect = function()
        local host = vim.fn.input('Host [127.0.0.1]: ')
        host = host ~= '' and host or '127.0.0.1'
        local port = tonumber(vim.fn.input('Port [5678]: ')) or 5678
        return { host = host, port = port }
    end,
    cwd = vim.fn.getcwd(),
    pathMappings = {
        {
            localRoot = vim.fn.getcwd(), -- Wherever your Python code lives locally.
            remoteRoot = "/home/app/{{cookiecutter.repo_name}}/{{cookiecutter.repo_name}}", -- Wherever your Python code lives in the container.
        },
    },
})
