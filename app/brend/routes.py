from app.brend import views
from app.settings import APP_STATIC_PATH


def setup_routes(app):
    app.router.add_static('/static/', path=APP_STATIC_PATH, name='static')
    app.router.add_view('/', views.MainPage)
    app.router.add_view('/send_view', views.MainPage)
    app.router.add_view('/file', views.ViewFile)