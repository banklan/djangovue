from django.db import models
from django.contrib.auth.models import User
from django_resized import ResizedImageField
from django.dispatch.dispatcher import receiver

from django.db.models.signals import pre_delete


class Post(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=False)
    body = models.TextField()
    # image = models.ImageField(upload_to='images', default='images/no_image.png', blank=False, null=True)
    image = ResizedImageField(size=[520, 300], quality=85, upload_to='images', default='images/no_image.png', blank=False, null=True)
    is_featured = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    viewcount = models.IntegerField(default=0)
    author = models.ForeignKey(User, related_name="post", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def pub_date(self):
        pub = self.created
        mod = pub.strftime("%B %d, %Y")
        return mod

    class Meta:
        ordering = ['-created']

    def rating_average(self):
        total = 0
        reviews = Review.objects.filter(post=self)
        for review in reviews:
            total = total + review.rating
        if len(reviews) > 0:
            return int(round(total / len(reviews)))
        else:
            return 0

    def incrementViewCount(self):
        self.viewcount += 1
        self.save()

    @property
    def reviews(self):
        return self.review_set.all()


@receiver(pre_delete, sender=Post)
def Post_delete(sender, instance, **kwargs):
    instance.image.delete(False)


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    title = models.CharField(max_length=80, blank=False, null=False)
    body = models.TextField(max_length=200, blank=False, null=False)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    is_approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def pub_date(self):
        pub = self.created
        mod = pub.strftime("%B %d, %Y")
        return mod

    class Meta:
        ordering = ['-created']
