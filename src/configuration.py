import toml

def read_configuration(path = r'config\config.toml'):

    return toml.load(path)