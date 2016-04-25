class Config(object):
    SECRET_KEY = '1f383c34f4d8c4795079b66fa6d2ec6f'

class ProdConfig(Config):
    pass

class DevConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:blogblog@localhost/blog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False