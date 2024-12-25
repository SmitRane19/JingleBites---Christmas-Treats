from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    authorname = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.authorname


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = RichTextField() 
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title




class Subscription(models.Model):
    PLAN_CHOICES = [
        ('Basic', 'Basic'),
        ('Standard', 'Standard'),
        ('Premium', 'Premium'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='Basic')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)]  
    )
    comment = models.TextField(blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.score} by {self.user.username} for {self.post.title}"

    class Meta:
        unique_together = ('user', 'post')  

class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_posts')
    saved_date = models.DateField()  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} saved {self.post.title} for {self.saved_date}"

    class Meta:
        unique_together = ('user', 'post', 'saved_date') 

class Download(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='downloads')
    download_date = models.DateField(auto_now_add=True)  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} downloaded {self.post.title} on {self.download_date}"

    class Meta:
        unique_together = ('user', 'post', 'download_date')  
