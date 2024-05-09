import json

class Config:
    def __init__(self, config_file):
        self.config_file = config_file

    def load(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def save(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def update(self, key, value):
        config = self.load()
        config[key] = value
        self.save(config)