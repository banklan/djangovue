# from datetime import timezone
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import UpdateAPIView, ListAPIView, DestroyAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post, Review
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from .serializers import UserSerializer, PostSerializer, ChangePasswordSerializer, UserRegistrationSerializer, \
    ReviewSerializer
from .pagination import PostListPagination


class UserViewSets(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostViewSets(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'pk'
    parser_classes = (MultiPartParser, FormParser)
    # pagination_class = PageNumberPagination
    # page_size = 4

    def create(self, request, *args, **kwargs):
        title = request.data['title']
        slug = slugify(title)
        body = request.data['body']
        author = self.request.user
        image = request.data.get('image', None)
        post = Post.objects.create(title=title, body=body, author=author, slug=slug, image=image)
        ser_context = {
            'request': request
        }
        serialized = self.serializer_class(post, context=ser_context)
        response = {'message': 'Post created', 'result': serialized.data}
        return Response(response, status=status.HTTP_201_CREATED)

    # for view counts of objects
    def get_object(self):
        item = super(PostViewSets, self).get_object()
        # item = Post.objects.get(id=)
        item.incrementViewCount()
        # author = item.author
        # author_posts = self.get_queryset().filter(author=author)
        return item


class PostListAPIView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination
    page_size = 4
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'body', 'author__username', 'author__last_name', 'author__first_name')


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_queryset(self):
        serializer = UserSerializer(self.request.user)
        user_id = self.request.user
        print(user_id)
        return super(ProfileViewSet, self).get_queryset()


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.instance.id
        token = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': user,
            # 'email': user.email
        })


class ProfileView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        me = self.request.user
        serializer = User.objects.filter(id=self.request.user.id)
        ser = UserSerializer(me)
        # print(serializer)
        return serializer


class UpdatePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # check old password
            if not instance.check_password(serializer.data.get('password')):
                return Response({'status': 'failed', 'message': 'Invalid Password'}, status=status.HTTP_400_BAD_REQUEST)

            if request.data.get('confirm_password') != request.data.get('new_password'):
                raise serializer.ValidationError({'password': 'New password and Confirm password must match'})

            # if everything is ok
            instance.set_password(request.data.get('new_password'))
            instance.save()
            update_session_auth_hash(request, instance)
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully'
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyPostsAPIView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        queryset = Post.objects.filter(author=self.request.user)[:5]
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)


class PostUpdateView(UpdateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        title = request.data['title']
        instance.slug = slugify(title)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PostDeleteView(DestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # if serializer.is_valid():
        serializer.save()
        # headers = self.get_success_headers(serializer.data)
        response = {
            'status': 'success',
            'message': 'User has been created successfully.',
            'resp': status.HTTP_201_CREATED
        }
        return Response(response)


class ReviewCreateAPIView(CreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        post_id = kwargs.get('pk')
        serializer.is_valid(raise_exception=True)
        post = Post.objects.get(pk=post_id)
        serializer.save(author=self.request.user, post=post, created=timezone.now())
        response = {
            'status': 'success',
            'message': 'Review has been submitted.',
            'resp': status.HTTP_201_CREATED,
            'data': serializer.data
        }
        return Response(response)


class ReviewDeleteAPIView(DestroyAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]


class RelatedPostListAPIView(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        post = Post.objects.get(id=self.kwargs['pk'])
        queryset = Post.objects.filter(author=post.author).exclude(id=self.kwargs['pk'])[:5]
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)


class PostsByAuthorAPIView(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def list(self, request, *args, **kwargs):
        author = User.objects.get(id=self.kwargs['pk'])
        queryset = self.get_queryset().filter(author=author)
        serialized = PostSerializer(queryset, many=True)
        return Response(serialized.data)


class LatestPostsAPIView(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by('-created')[:5]
        serialized = PostSerializer(queryset, many=True)
        return Response(serialized.data)


class FeaturedPostsAPIView(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(is_featured=True).order_by('-created')[:5]
        serialized = PostSerializer(queryset, many=True)
        return Response(serialized.data)
