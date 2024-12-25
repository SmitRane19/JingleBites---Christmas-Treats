from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Rating, Author, Subscription, SavedPost, Download
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import AuthorSignUpForm, AuthorNameForm, PostForm
import random
import datetime
import razorpay
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
from django.db.models import Q
from django.utils.timezone import now
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from datetime import date,datetime, timedelta



def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index') 
        else:
            return render(request, "signin.html", {"form": form})
    else:
        form = AuthenticationForm()
    return render(request, "signin.html", {'form': form})

def signout(request):
    logout(request)
    return redirect("index") 

def sign_up(request):
    if request.method == 'POST':
        form = AuthorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  
            login(request, user)  
            return redirect('index')  
    else:
        form = AuthorSignUpForm()

    return render(request, 'sign_up.html', {'form': form})

@login_required
def edit_authorname(request):
    if hasattr(request.user, 'author_profile'):
        author = request.user.author_profile
    else:
        author = Author(user=request.user)

    if request.method == 'POST':
        form = AuthorNameForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = AuthorNameForm(instance=author)

    return render(request, 'edit_authorname.html', {'form': form})

def index(request):
    if request.user.is_authenticated:
        user_posts = Post.objects.filter(author__user=request.user).annotate(
            average_rating=Avg('ratings__score')
        )

        other_posts = Post.objects.exclude(author__user=request.user).annotate(
            average_rating=Avg('ratings__score')
        )

        context = {
            'user_posts': user_posts,
            'other_posts': other_posts
        }

        return render(request, 'index.html', context)
    else:
        return redirect('signin')

@login_required
def rate_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        score = int(request.POST.get('score', 0))
        if 1 <= score <= 5:
            rating, created = Rating.objects.get_or_create(
                post=post, 
                user=request.user,
                defaults={'score': score}
            )
            if not created:
                rating.score = score
                rating.save()

            return redirect('index')  
        else:
        
            return redirect('view_post', post.id)  

    return redirect('index')  

def about_us(request):
    return render(request, 'about_us.html')



def search_recipe(request):
    query = request.GET.get('q')  

    if query:
        
        posts = Post.objects.exclude(author__user=request.user).filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    else:
        posts = Post.objects.exclude(author__user=request.user) 

    return render(request, 'search_recipe.html', {'posts': posts, 'query': query})


def create_post(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    
    user = request.user
    today = now().date()

    try:
        author = Author.objects.get(user=user)
    except Author.DoesNotExist:
        return redirect('edit_authorname') 

    
    subscription = Subscription.objects.filter(user=user).first()
    plan_limits = {
        'Free': 1,      
        'Basic': 3,
        'Standard': 10,
        'Premium': float('inf'),  
    }

    
    plan = subscription.plan if subscription else 'Free'
    max_posts = plan_limits[plan]
    
    
    today_posts_count = Post.objects.filter(author=author, created_at__date=today).count()

    
    if today_posts_count >= max_posts:
        return render(request, 'error.html', {
            'message': f"You have reached your daily limit of {max_posts} post(s) for your plan."
        })

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES) 
        if form.is_valid():
            post = form.save(commit=False)
            post.author = author
            post.save()
            return redirect('index')
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})




def delete_post(request, post_id):
    if not request.user.is_authenticated:
        return redirect('signin')
    post = get_object_or_404(Post, id=post_id, author__user=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('index')
    return render(request, 'delete_post.html', {'post': post})


def view_post(request, post_id):
    if not request.user.is_authenticated:
        return redirect('signin')
    post = get_object_or_404(Post, id=post_id)

    # Handle POST requests for saving posts
    if request.method == "POST" and 'save_date' in request.POST:
        save_date = request.POST.get('save_date')
        SavedPost.objects.create(user=request.user, post=post, saved_date=save_date)
        return redirect('view_post', post_id=post.id)

    # Render the template
    return render(request, 'view_post.html', {'post': post})

def save_post(request, post_id):
    if not request.user.is_authenticated:
        return redirect('signin')  
    
    post = get_object_or_404(Post, id=post_id)  
    
    if request.method == 'POST':
        saved_date = request.POST.get('save_date')  
        
        # Create the SavedPost instance and save it
        saved_post = SavedPost.objects.create(
            user=request.user, 
            post=post, 
            saved_date=saved_date  
        )
        saved_post.save()  
        
        return redirect('saved_posts')  
    
    return redirect('post_detail', post_id=post_id)  
    
    return render(request, 'save_post.html', {'post': post})


def download_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Try to get the user's subscription plan, or assign a default value if no subscription exists
    try:
        subscription = request.user.subscription  
        plan = subscription.plan
    except Subscription.DoesNotExist:
        # Assign a default plan for users without a subscription (i.e., free users)
        plan = 'Free'

    # Define download limits based on the subscription plan
    download_limits = {
        'Free': 1,  
        'Basic': 3,
        'Standard': 10,
        'Premium': float('inf') 
    }

    daily_limit = download_limits.get(plan, 0)

    # Get today's date to check the downloads
    today = date.today()

    # Check how many times the user has already downloaded the post today
    download_count_today = Download.objects.filter(
        user=request.user,
        post=post,
        download_date=today
    ).count()

    # If the user exceeds their download limit, render the error page with the message
    if download_count_today >= daily_limit:
        message = "You have reached your download limit for today."
        return render(request, 'error_pdf.html', {'message': message})

    # If the download limit is not exceeded, create a new download record
    Download.objects.create(user=request.user, post=post, download_date=today)

    # Build the absolute URL for the image
    image_url = request.build_absolute_uri(post.image.url) if post.image else None

    # Create the PDF
    template_path = 'view_post_pdf.html'
    context = {
        'post': post,
        'image_url': image_url
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{post.title}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


def error_view(request):
    # Get the error message from query parameters (default to a generic message if not found)
    message = request.GET.get('message', 'An unknown error occurred.')

    # Render the error page with the message
    return render(request, 'error_pdf.html', {'message': message})


from django.utils.timezone import make_aware

def saved_posts_view(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    
    # Get the current date (ignoring time)
    current_date = make_aware(datetime.now()).date()  

    # Find and delete saved posts that have expired
    saved_posts = SavedPost.objects.filter(user=request.user)
    
    # Loop through saved posts and delete the ones where the saved date has passed
    for saved_post in saved_posts:
        if saved_post.saved_date:
            # Compare saved_date (date only) with current_date (date only)
            if saved_post.saved_date < current_date:
                saved_post.delete()

    # Get all the saved posts after deletion
    saved_posts = SavedPost.objects.filter(user=request.user).select_related('post', 'post__author')
    
    return render(request, 'saved_posts.html', {'saved_posts': saved_posts})


def edit_post(request, post_id):
    if not request.user.is_authenticated:
        return redirect('signin')
    
    post = get_object_or_404(Post, id=post_id, author__user=request.user)
    
    if request.method == 'POST':
        
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image') 
        
        if title and content:
            post.title = title
            post.content = content
            
            
            if image:
                post.image = image
            
            post.save()  
            
            return redirect('view_post', post_id=post.id)  
    
    return render(request, 'edit_post.html', {'post': post})


def subscription(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    subscription = Subscription.objects.filter(user=user).first()
    plans = [
        {'id': 'Basic', 'name': 'Basic', 'features': '3 posts per day, 3 downloads per day', 'price': 100},
        {'id': 'Standard', 'name': 'Standard', 'features': '10 posts per day, 5 downloads per day', 'price': 500},
        {'id': 'Premium', 'name': 'Premium', 'features': 'Unlimited posts per day, Unlimited downloads per day', 'price': 1000},
    ]
    
    # Process the features into lists and trim spaces
    for plan in plans:
        plan['features'] = [feature.strip() for feature in plan['features'].split(',')]  # Trim spaces after splitting
    
    current_plan = subscription.plan if subscription else "Free"
    
    return render(request, 'subscription.html', {
        'plans': plans,
        'subscription': subscription,
        'current_plan': current_plan,
    })



def payment(request, plan_id):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    plan_prices = {
        'Basic': 100,
        'Standard': 500,
        'Premium': 1000,
    }
    if plan_id not in plan_prices:
        return render(request, 'error.html', {'message': f"Invalid plan: {plan_id}"})
    amount = plan_prices[plan_id] * 100
    order_id = f"ORDER_{random.randint(100000, 999999)}"
    client = razorpay.Client(auth=("rzp_test_n0lhpmrEfeIhGJ", "UOrbXQGnsEc2dhB1IFg0zNWZ"))
    try:
        payment_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": order_id,
        })
    except Exception as e:
        return render(request, 'error.html', {'message': f"Error creating Razorpay order: {str(e)}"})
    context = {
        "payment": payment_order,
        "plan": plan_id,
        "amount": amount // 100,
    }
    return render(request, 'pay.html', context)

def payment_success(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    payment_id = request.GET.get('payment_id', 'N/A')
    order_id = request.GET.get('order_id', 'N/A')
    plan = request.GET.get('subscription_plan', 'Basic')
    user = request.user
    subscription, _ = Subscription.objects.get_or_create(user=user)
    subscription.plan = plan
    subscription.start_date = datetime.now()  # Use datetime directly
    subscription.end_date = subscription.start_date + timedelta(days=30)  # Use timedelta directly
    subscription.save()
    send_mail(
        subject="Subscription Payment Successful",
        message=(
            f"Hi {user.username},\n\n"
            f"Thank you for subscribing to the {plan} plan!\n"
            f"Your subscription is active and valid until {subscription.end_date.date()}.\n\n"
            f"Payment ID: {payment_id}\n"
            f"Order ID: {order_id}\n\n"
            "Enjoy your subscription!\n\n"
            "Best Regards,\nYour Blog Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return render(request, 'payment_success.html', {
        'plan': plan,
        'payment_id': payment_id,
        'order_id': order_id,
    })

