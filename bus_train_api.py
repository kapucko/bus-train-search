from btsearch.api import app

if __name__ == '__main__':
    app.config_loader.start()
    app.run()