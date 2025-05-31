from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from store import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),  # কাস্টম login view
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('accounts/login/', views.login_view, name='account_login'),  # Fix for login_required redirection

    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 
 