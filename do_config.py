import json

def config(app):
    with open('app_config.json') as config_file:
        config = json.load(config_file)
        app_settings = config['app_config']
        db_settings = config['db_config']
        app.config.update(app_settings)
        app.config.update(db_settings)   
        app.secret_key = bytes(app.secret_key, 'utf-8') 