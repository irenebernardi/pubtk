import os
'''

def check_shell():
    os.environ.get('SHELL', 'Unknown')
    envs_dict = {key:value for key,value in os.environ.items()}
    return envs_dict

result = check_shell()
print(result)

def assertions():
    print(f'assert #!/usr/bin/'{value}) for key, value in envs_dict'''



def check_shell():
    os.environ.get('SHELL', 'Unknown')
    envs_dict = {key: value for key, value in os.environ.items()}
    return envs_dict

result = check_shell()
print(result)

def assertions():
    shell_assertions = {
        '/sh': '#!/usr/bin/env sh',
        '/zsh': 'source ~/.zshrc',
        # Add more mappings as needed
    }

    for key, value in result.items():
        assertion = shell_assertions.get(value.rsplit('/', 1)[-1], '#!/usr/bin/env sh')
        assert assertion in script

assertions()
