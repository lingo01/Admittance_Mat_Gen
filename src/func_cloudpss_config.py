import os

import cloudpss


def func_inject_cloudpss_config():
    server_name = "your_server_name"
    token = "your_token"
    user_name = "your_user_name"

    cloudpss.setToken(f'{token}')
    os.environ['CLOUDPSS_API_URL'] = f'{server_name}'
    return server_name, token, user_name
