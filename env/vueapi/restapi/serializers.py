from abc import ABC

from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.fields import SerializerMethodField
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from .models import Post, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


def required(value):
    if value is None:
        raise serializers.ValidationError('This field is required')


class UserRegistrationSerializer(serializers.ModelSerializer):
    c_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'c_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        username = self.validated_data['username']
        password = self.validated_data['password']
        c_password = self.validated_data['c_password']

        if len(password) < 6 or len(password) > 20:
            raise serializers.ValidationError({'password': 'Password must be between 6 and 20 characters.'})

        if password != c_password:
            raise serializers.ValidationError({'password': 'Password and confirm password must match!'})

        user = User(first_name=first_name, last_name=last_name, email=email, username=username)
        user.set_password(password)
        user.save()
        Token.objects.create(user=user)


class ReviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    created = serializers.DateField(source="pub_date", read_only=True)
    title = serializers.CharField(validators=[required], allow_blank=False)
    body = serializers.CharField(validators=[required], allow_blank=False)
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, validators=[required])

    class Meta:
        model = Review
        fields = ['id', 'title', 'body', 'rating', 'is_approved', 'created', 'author']
        depth = 2


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    reviews = ReviewSerializer(many=True, read_only=True)
    date = serializers.DateField(source="pub_date")
    ratings = serializers.DecimalField(max_digits=2, decimal_places=1, source="rating_average")
    image = serializers.ImageField(max_length=None)
    # author_posts = serializers.SerializerMethodField('get_author_posts')

    class Meta:
        model = Post
        fields = ['id', 'slug', 'title', 'body', 'author', 'is_featured', 'date', 'ratings', 'reviews', 'viewcount', 'is_verified', 'image']
        # depth=1


class TokenSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Token
        fields = ('key', 'user')


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']
