from django.contrib import admin
from .models import Author, Post, Subscription, Rating, SavedPost, Download
from django.utils.html import strip_tags


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('authorname', 'user') 


from django.utils.html import format_html

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_authorname', 'plain_content', 'created_at', 'get_average_rating', 'show_image')
    list_filter = ('author', 'created_at') 
    search_fields = ('title', 'plain_content') 


    def plain_content(self, obj):
        return strip_tags(obj.content)
    plain_content.short_description = 'Content (Plain Text)'


    def get_authorname(self, obj):
        return obj.author.authorname

    get_authorname.admin_order_field = 'author__authorname'
    get_authorname.short_description = 'Author Name'

    def get_average_rating(self, obj):
        # Calculate average rating manually
        ratings = obj.ratings.all()
        if ratings.exists():
            total_score = sum([rating.score for rating in ratings])
            return total_score / ratings.count()
        return "No ratings yet"
    get_average_rating.short_description = 'Average Rating'

    def show_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;"/>', obj.image.url)
        return "No image"
    show_image.short_description = 'Image'




class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'score', 'comment', 'created_at')
    list_filter = ('score', 'created_at')  
    search_fields = ('user__username', 'post__title', 'comment')  


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'saved_date', 'created_at')  
    search_fields = ('user__username', 'post__title')  
    list_filter = ('saved_date',)  
    ordering = ('-created_at',)  


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'download_date', 'created_at') 
    search_fields = ('user__username', 'post__title') 
    list_filter = ('download_date',)  
    ordering = ('-created_at',) 

admin.site.register(Author, AuthorAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Subscription)
admin.site.register(Rating, RatingAdmin)
