from aiohttp import web
import jinja2
import aiohttp_jinja2
from app.settings import APP_TEMPLATES_PATH, APP_STATIC_PATH, APP_HOST, APP_PORT
import ssl


def setup_routes(application):
    from app.brend.routes import setup_routes as setup_brend_routes
    setup_brend_routes(application)

def setup_external_libraries(application: web.Application) -> None:
    aiohttp_jinja2.setup(application, loader=jinja2.FileSystemLoader(APP_TEMPLATES_PATH))

def setup_app(application):
    setup_routes(application)
    setup_external_libraries(application)


ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
app = web.Application()
app['static_root_url'] = APP_STATIC_PATH


if __name__ == '__main__':
    setup_app(app)
    web.run_app(app, host=APP_HOST, port=APP_PORT)