from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.authtoken import views
from restapi.views import CustomAuthToken

from restapi.views import (
    UserViewSets, PostViewSets, ProfileViewSet,
    ProfileView, UpdatePasswordView, MyPostsAPIView,
    PostUpdateView, PostDeleteView, UserCreateAPIView,
    ReviewCreateAPIView, RelatedPostListAPIView,
    ReviewDeleteAPIView, PostsByAuthorAPIView,
    LatestPostsAPIView, FeaturedPostsAPIView,
    PostListAPIView,
)
# from vueapi.restapi.views import

router = routers.DefaultRouter()
router.register('users', UserViewSets, basename='users')
router.register('posts', PostViewSets, basename='posts')
router.register('profile', ProfileView, basename='profile')
# router.register('password-change', UpdatePasswordView, basename='password-change')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token, name="api-token-auth"),
    path('password-change/', UpdatePasswordView.as_view(), name="password"),
    path('my-posts/', MyPostsAPIView.as_view(), name="my-posts"),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name="post-update"),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name="post-delete"),
    path('user/create/', UserCreateAPIView.as_view(), name="create-user"),
    path('review/<int:pk>/', ReviewCreateAPIView.as_view(), name="create-review"),
    path('review/<int:pk>/delete/', ReviewDeleteAPIView.as_view(), name="delete-review"),
    path('related_posts/<int:pk>/', RelatedPostListAPIView.as_view(), name="related_posts"),
    path('posts_by_author/<int:pk>/', PostsByAuthorAPIView.as_view(), name="posts-by-author"),
    path('featured_posts/', FeaturedPostsAPIView.as_view(), name="featured-posts"),
    path('latest_posts/', LatestPostsAPIView.as_view(), name="latest-posts"),
    path('posts', PostListAPIView.as_view(), name="all-posts")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# for url in router.urls:
#     print(url, '\n')
