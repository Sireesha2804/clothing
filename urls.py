from django.urls import path
from .views import login_view,basic,cloth,signup,CustomLoginView
urlpatterns = [
    path('login/', login_view, name='login'),
path('signup/', signup, name='signup'),
path("login/", CustomLoginView.as_view(), name="login"),
    path('basic/', basic, name='basic'),
    path('cloth/', cloth, name='cloth'),
    #     path("api/load-cart/", load_cart, name="load-cart"),
    # path("api/place-order/", place_order, name="place-order"),

]



