"""
URL configuration for Blog_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Blog_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about-us/', views.about_us, name='about_us'),
    path('subscription/', views.subscription, name='subscription'),
    path('signin/', views.signin, name='signin'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('logout/', views.signout, name='logout'),
    path('edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('view/<int:post_id>/', views.view_post, name='view_post'),
    path('create-post/', views.create_post, name='create_post'),
    path('payment/<str:plan_id>/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('edit-authorname/', views.edit_authorname, name='edit_authorname'),
    path('post/<int:post_id>/rate/', views.rate_post, name='rate_post'),
    path('search/', views.search_recipe, name='search_recipe'),
    path('post/<int:post_id>/', views.view_post, name='view_post'),
    path('post/<int:post_id>/save/', views.save_post, name='save_post'),
    path('saved-posts/', views.saved_posts_view, name='saved_posts'),
    path('post/<int:post_id>/download/', views.download_post, name='download_post'),
    path('error/', views.error_view, name='error_view'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)