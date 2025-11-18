"""
Core Views for Travel & Tourism Web Application
Features: User Auth, Dashboard, Destinations, Tips, Gallery, Travel Plans, Services
All views include appropriate flash messages for user feedback.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date


# Import models
from .models import (
    CustomUser, Destination, Tip, Activity, Notification,
    DestinationRoute, Review, Event, UserTravelPlan,
    Photo, PhotoComment, ThirdPartyService
)

# Import forms
from .forms import (
    RegisterForm, LoginForm, UserTravelPlanForm, ThirdPartyServiceForm
)


# ================================
# Public Views
# ================================


def index(request):
    """
    Homepage: Displays latest destinations, travel tips, and map routes,
    plus activities and partner services.
    """
    # 1. Main Content
    destinations = Destination.objects.all().order_by("-created_at")
    tips = Tip.objects.all().order_by("-created_at")[:6] # Showing more tips
    
    # 2. Additional Content
    # Get recent/upcoming activities (e.g., in the future or recent past)
    activities = Activity.objects.filter(end_date__gte=date.today()).order_by("start_date")[:4]

    # Get a selection of partner services
    services = ThirdPartyService.objects.select_related("destination").order_by("-created_at")[:4]

    # 3. Map Route Data (Keep original logic)
    route_data = []
    for destination in destinations:
        # Use select_related/prefetch_related if possible, but basic values works here
        routes = destination.routes.all().values("latitude", "longitude", "order")
        points = [
            {"lat": r["latitude"], "lng": r["longitude"], "order": r["order"]}
            for r in routes
        ]
        if points:
            route_data.append({
                "destination": destination.name,
                "country": destination.country,
                "points": points
            })
    
    # 4. Context for Template
    context = {
        "destinations": destinations,
        "tips": tips,
        "activities": activities,  # New
        "services": services,      # New
        "route_data": route_data,
        
        # Pass model choices for filter dropdowns
        "Destination": {
            "SEASON_CHOICES": Destination.SEASON_CHOICES,
            "TRAVEL_TYPE_CHOICES": Destination.TRAVEL_TYPE_CHOICES,
        }
    }
    return render(request, "index.html", context)

def destination_list(request):
    """List all available travel destinations."""
    destinations = Destination.objects.all().order_by("-created_at")
    messages.info(request, f"Showing {destinations.count()} beautiful destinations!")
    return render(request, "destinations.html", {"destinations": destinations})


from datetime import date

def destination_detail(request, pk):
    """
    Show destination details, reviews, events, and allow logged-in users to post reviews.
    """
    destination = get_object_or_404(Destination, pk=pk)
    reviews = destination.reviews.all().order_by("-created_at")
    events = destination.event_set.all().order_by("date")

    if request.method == "POST":
        if "user_id" not in request.session:
            messages.error(request, "Please log in to leave a review.")
            return redirect("login")

        user = CustomUser.objects.get(id=request.session["user_id"])
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if not rating or not comment:
            messages.error(request, "Rating and comment are required.")
        else:
            Review.objects.create(
                user=user,
                destination=destination,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Thank you! Your review has been posted.")
        return redirect("destination_detail", pk=pk)

    return render(request, "destination_detail.html", {
        "destination": destination,
        "reviews": reviews,
        "events": events,
        "today": date.today(),  # Add this for the upcoming badge
    })

def tips_list(request):
    """Display all travel tips."""
    tips = Tip.objects.all().order_by("-created_at")
    messages.info(request, f"{tips.count()} helpful travel tips available!")
    return render(request, "tips.html", {"tips": tips})


# ================================
# Authentication Views
# ================================

def register(request):
    """
    User registration with CAPTCHA verification.
    WARNING: Password stored in plain text — MUST be replaced with proper hashing!
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        captcha = request.POST.get("captcha")
        captcha_input = request.POST.get("captcha_input")

        if captcha != captcha_input:
            messages.error(request, "CAPTCHA verification failed. Please try again.")
        elif form.is_valid():
            user = form.save(commit=False)
            user.password = form.cleaned_data["password"]  # WARNING: Plain text! Use set_password()
            user.save()
            messages.success(request, "Account created successfully! Welcome aboard.")
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    """Handle user login using mobile number and password."""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            mobile_no = form.cleaned_data["mobile_no"]
            password = form.cleaned_data["password"]

            try:
                user = CustomUser.objects.get(mobile_no=mobile_no, password=password)
                request.session["user_id"] = user.id
                request.session["user_name"] = user.first_name
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect("dashboard")
            except CustomUser.DoesNotExist:
                messages.error(request, "Invalid mobile number or password.")
        else:
            messages.error(request, "Please fix the login form errors.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    """Log out the user and clear session."""
    if "user_id" in request.session:
        name = request.session.get("user_name", "Traveler")
        request.session.flush()
        messages.success(request, f"Goodbye, {name}! See you soon.")
    else:
        messages.info(request, "You were not logged in.")
    return redirect("login")


import json
from django.db.models import Count

def dashboard(request):
    if "user_id" not in request.session:
        messages.warning(request, "Please log in to access your dashboard.")
        return redirect("login")

    user = CustomUser.objects.get(id=request.session["user_id"])

    # Existing logic (unchanged)
    suggested_destinations = Destination.objects.filter(
        best_season=user.travel_season,
        travel_type=user.travel_type
    ).prefetch_related("routes")

    suggested_activities = Activity.objects.filter(destination__in=suggested_destinations)
    suggested_tips = Tip.objects.filter(season=user.travel_season)
    notifications = Notification.objects.order_by("-created_at")[:5]

    # NEW: All destinations + stats
    all_destinations = Destination.objects.all().order_by('-created_at')
    destinations = Destination.objects.all().order_by("-created_at")

    # For map: get center points (average or first route point)
    all_destinations_json = json.dumps([
        {
            "name": d.name,
            "country": d.country,
            "latitude": d.routes.first().latitude if d.routes.exists() else 0,
            "longitude": d.routes.first().longitude if d.routes.exists() else 0,
        } for d in all_destinations if d.routes.exists()
    ])

    # Stats for charts
    season_stats = dict(Destination.objects.values('best_season')
                        .annotate(count=Count('id'))
                        .values_list('best_season', 'count'))
    season_stats = {
        'summer': season_stats.get('summer', 0),
        'winter': season_stats.get('winter', 0),
        'spring': season_stats.get('spring', 0),
        'autumn': season_stats.get('autumn', 0),
    }

    type_stats = dict(Destination.objects.values('travel_type')
                      .annotate(count=Count('id'))
                      .values_list('travel_type', 'count'))
    type_stats = {
        'adventure': type_stats.get('adventure', 0),
        'cultural': type_stats.get('cultural', 0),
        'leisure': type_stats.get('leisure', 0),
        'family': type_stats.get('family', 0),
        'luxury': type_stats.get('luxury', 0),
    }

     # Prepare route data for Leaflet map
    route_data = []
    for d in destinations:
        routes = d.routes.all().values("latitude", "longitude", "order")
        points = [{"lat": r["latitude"], "lng": r["longitude"], "order": r["order"]} for r in routes]
        route_data.append({
            "destination": d.name,
            "country": d.country,
            "points": points
        })

    context = {
        "user": user,
        "suggested_destinations": suggested_destinations,
        "suggested_activities": suggested_activities,
        "suggested_tips": suggested_tips,
        "notifications": notifications,
        "route_data": route_data,
        "all_destinations": all_destinations,
        "all_destinations_json": all_destinations_json,
        "season_stats": season_stats,
        "type_stats": type_stats,
    }
    messages.info(request, f"Welcome back, {user.first_name}! Here's your personalized feed.")
    return render(request, "dashboard.html", context)


def profile_update(request):
    """Allow users to update their profile information."""
    user_id = request.session.get("user_id")
    if not user_id:
        messages.warning(request, "You need to log in to update your profile.")
        return redirect("login")

    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST":
        # Manual field update (could be improved with ModelForm)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.nationality = request.POST.get("nationality", user.nationality)
        user.city = request.POST.get("city", user.city)
        user.postal_address = request.POST.get("postal_address", user.postal_address)
        user.mobile_no = request.POST.get("mobile_no", user.mobile_no)
        user.email = request.POST.get("email", user.email)
        user.travel_season = request.POST.get("travel_season", user.travel_season)
        user.travel_type = request.POST.get("travel_type", user.travel_type)
        user.age_range = request.POST.get("age_range", user.age_range)
        user.budget_range = request.POST.get("budget_range", user.budget_range)
        user.save()

        messages.success(request, "Your profile has been updated successfully!")
        return redirect("dashboard")

    messages.info(request, "Update your personal information below.")
    return render(request, "profile_update.html", {"user": user})


# ================================
# Travel Plan Management
# ================================

def travelplan_list(request):
    """List all travel plans created by the logged-in user."""
    if "user_id" not in request.session:
        messages.warning(request, "Log in to view your travel plans.")
        return redirect("login")

    user = CustomUser.objects.get(id=request.session["user_id"])
    plans = UserTravelPlan.objects.filter(user=user).order_by("-created_at")

    if not plans:
        messages.info(request, "You haven't created any travel plans yet.")
    else:
        messages.info(request, f"You have {plans.count()} saved travel plan(s).")

    return render(request, "travelplans/travelplan_list.html", {"plans": plans})


def travelplan_create(request):
    """Create a new travel plan."""
    if "user_id" not in request.session:
        messages.error(request, "Please log in to create a travel plan.")
        return redirect("login")

    user = CustomUser.objects.get(id=request.session["user_id"])

    if request.method == "POST":
        form = UserTravelPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = user
            plan.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "New travel plan created successfully!")
            return redirect("travelplan_list")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = UserTravelPlanForm()

    return render(request, "travelplans/travelplan_form.html", {
        "form": form,
        "title": "Create New Travel Plan"
    })


def travelplan_update(request, pk):
    """Update an existing travel plan."""
    if "user_id" not in request.session:
        messages.error(request, "Login required to edit travel plans.")
        return redirect("login")

    user = CustomUser.objects.get(id=request.session["user_id"])
    plan = get_object_or_404(UserTravelPlan, pk=pk, user=user)

    if request.method == "POST":
        form = UserTravelPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Travel plan updated successfully!")
            return redirect("travelplan_list")
        else:
            messages.error(request, "Please fix the form errors.")
    else:
        form = UserTravelPlanForm(instance=plan)

    return render(request, "travelplans/travelplan_form.html", {
        "form": form,
        "title": "Update Travel Plan"
    })


def travelplan_delete(request, pk):
    """Delete a travel plan."""
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in.")
        return redirect("login")

    user = CustomUser.objects.get(id=request.session["user_id"])
    plan = get_object_or_404(UserTravelPlan, pk=pk, user=user)
    plan.delete()
    messages.success(request, "Travel plan deleted successfully.")
    return redirect("travelplan_list")


# ================================
# Gallery (Photos, Likes, Comments)
# ================================

def gallery(request):
    """
    Community photo gallery with upload, like, and comment features.
    """
    photos = Photo.objects.all().order_by("-created_at")
    user_id = request.session.get("user_id")

    # Attach like status to each photo
    for photo in photos:
        photo.is_liked = user_id and photo.likes.filter(id=user_id).exists()

    # Handle photo upload
    if request.method == "POST" and "upload_photo" in request.POST:
        if not user_id:
            messages.error(request, "You must log in to upload photos.")
            return redirect("login")

        user = CustomUser.objects.get(id=user_id)
        destination_id = request.POST.get("destination")
        image = request.FILES.get("image")
        caption = request.POST.get("caption", "")

        if not destination_id or not image:
            messages.error(request, "Destination and image are required.")
        else:
            destination = get_object_or_404(Destination, pk=destination_id)
            Photo.objects.create(user=user, destination=destination, image=image, caption=caption)
            messages.success(request, "Your photo was uploaded successfully!")

        return redirect("gallery")

    # Handle comment
    if request.method == "POST" and "add_comment" in request.POST:
        if not user_id:
            messages.error(request, "Login to comment on photos.")
            return redirect("login")

        user = CustomUser.objects.get(id=user_id)
        photo_id = request.POST.get("photo_id")
        comment_text = request.POST.get("comment", "").strip()

        if not comment_text:
            messages.error(request, "Comment cannot be empty.")
        else:
            photo = get_object_or_404(Photo, pk=photo_id)
            PhotoComment.objects.create(user=user, photo=photo, comment=comment_text)
            messages.success(request, "Comment added!")

        return redirect("gallery")

    # Handle like/unlike
    if request.method == "POST" and "like_photo" in request.POST:
        if not user_id:
            messages.error(request, "Login to like photos.")
            return redirect("login")

        user = CustomUser.objects.get(id=user_id)
        photo_id = request.POST.get("photo_id")
        photo = get_object_or_404(Photo, pk=photo_id)

        if photo.likes.filter(id=user.id).exists():
            photo.likes.remove(user)
            messages.success(request, "Photo unliked.")
        else:
            photo.likes.add(user)
            messages.success(request, "Photo liked!")

        return redirect("gallery")

    messages.info(request, f"Explore {photos.count()} amazing photos from travelers!")
    return render(request, "gallery.html", {
        "photos": photos,
        "destinations": Destination.objects.all(),
    })


# ================================
# Third-Party Services (CRUD)
# ================================

def service_list(request):
    """List all third-party travel services."""
    services = ThirdPartyService.objects.all().order_by("-created_at")
    messages.info(request, f"{services.count()} partner services available.")
    return render(request, "services/service_list.html", {"services": services})


def service_create(request):
    """Create a new third-party service (admin/staff only recommended)."""
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in to add services.")
        return redirect("login")

    if request.method == "POST":
        form = ThirdPartyServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New service added successfully!")
            return redirect("service_list")
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = ThirdPartyServiceForm()

    return render(request, "services/service_form.html", {
        "form": form,
        "action": "Add New Service"
    })


def service_update(request, pk):
    """Update an existing third-party service."""
    if "user_id" not in request.session:
        messages.error(request, "Login required.")
        return redirect("login")

    service = get_object_or_404(ThirdPartyService, pk=pk)

    if request.method == "POST":
        form = ThirdPartyServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully!")
            return redirect("service_list")
        else:
            messages.error(request, "Please fix the errors.")
    else:
        form = ThirdPartyServiceForm(instance=service)

    return render(request, "services/service_form.html", {
        "form": form,
        "action": "Update Service"
    })


def service_delete(request, pk):
    """Delete a third-party service."""
    if "user_id" not in request.session:
        messages.error(request, "Login required.")
        return redirect("login")

    service = get_object_or_404(ThirdPartyService, pk=pk)
    service.delete()
    messages.success(request, "Service removed successfully.")
    return redirect("service_list")