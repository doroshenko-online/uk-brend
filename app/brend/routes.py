from app.brend import views


def setup_routes(app):
    app.router.add_static('/static/', path='static/', name='static')
    app.router.add_view('/', views.MainPage)
    app.router.add_view('/send_view', views.MainPage)