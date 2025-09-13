from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from .models import CustomUser

from django.shortcuts import render
from .models import *

from django.shortcuts import render
from .models import Destination, Tip, DestinationRoute

def index(request):
    # Fetch all destinations
    destinations = Destination.objects.all().order_by("-created_at")
    
    # Fetch latest 3 tips
    tips = Tip.objects.all().order_by("-created_at")[:3]

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
        "destinations": destinations,
        "tips": tips,
        "route_data": route_data,  # pass to template
    }

    return render(request, "index.html", context)


# Register
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        captcha = request.POST.get("captcha")
        captcha_input = request.POST.get("captcha_input")

        if captcha != captcha_input:
            messages.error(request, "Captcha verification failed!")
        elif form.is_valid():
            user = form.save(commit=False)
            # save password as plain text for now (better to hash)
            user.password = form.cleaned_data["password"]
            user.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# Login
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            mobile_no = form.cleaned_data["mobile_no"]
            password = form.cleaned_data["password"]

            try:
                user = CustomUser.objects.get(mobile_no=mobile_no, password=password)
                request.session["user_id"] = user.id
                request.session["user_name"] = user.first_name
                return redirect("dashboard")
            except CustomUser.DoesNotExist:
                messages.error(request, "Invalid credentials!")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


# Dashboard
from django.shortcuts import render, redirect
from .models import CustomUser, Destination, Activity, Tip, Notification, DestinationRoute

def dashboard(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = CustomUser.objects.get(id=request.session["user_id"])

    # Suggested Destinations (based on season & travel type)
    suggested_destinations = Destination.objects.filter(
        best_season=user.travel_season,
        travel_type=user.travel_type
    ).prefetch_related("routes")  # preload routes for each destination

    # Suggested Activities
    suggested_activities = Activity.objects.filter(
        destination__in=suggested_destinations
    ).select_related("destination")

    # Suggested Tips
    suggested_tips = Tip.objects.filter(season=user.travel_season)

    # Latest Notifications
    notifications = Notification.objects.order_by("-created_at")[:5]

    # Collect route data for map
    route_data = []
    for dest in suggested_destinations:
        points = [
            {"lat": r.latitude, "lng": r.longitude, "order": r.order}
            for r in dest.routes.all()
        ]
        if points:
            route_data.append({
                "destination": dest.name,
                "country": dest.country,
                "points": points
            })

    context = {
        "user": user,
        "suggested_destinations": suggested_destinations,
        "suggested_activities": suggested_activities,
        "suggested_tips": suggested_tips,
        "notifications": notifications,
        "route_data": route_data,  # pass route data to template for Leaflet
    }
    return render(request, "dashboard.html", context)


# Logout
def logout_view(request):
    request.session.flush()
    return redirect("login")


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser

def profile_update(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")  # redirect if not logged in

    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.nationality = request.POST.get("nationality")
        user.city = request.POST.get("city")
        user.postal_address = request.POST.get("postal_address")
        user.mobile_no = request.POST.get("mobile_no")
        user.email = request.POST.get("email")
        user.travel_season = request.POST.get("travel_season")
        user.travel_type = request.POST.get("travel_type")
        user.age_range = request.POST.get("age_range")
        user.budget_range = request.POST.get("budget_range")
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("dashboard")

    return render(request, "profile_update.html", {"user": user})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Destination, Review, CustomUser

# List view
def destination_list(request):
    destinations = Destination.objects.all().order_by("-created_at")
    return render(request, "destinations.html", {"destinations": destinations})

# Detail + reviews + events
def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    reviews = destination.reviews.all().order_by("-created_at")
    events = destination.event_set.all().order_by("date")  # related events

    # Handle review post
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            messages.error(request, "You must be logged in to post a review.")
            return redirect("login")

        user = CustomUser.objects.get(pk=user_id)
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            Review.objects.create(
                user=user,
                destination=destination,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Your review has been posted.")
            return redirect("destination_detail", pk=destination.pk)
        else:
            messages.error(request, "Both rating and comment are required.")

    return render(request, "destination_detail.html", {
        "destination": destination,
        "reviews": reviews,
        "events": events,   # send events to template
    })



from django.shortcuts import render
from .models import Tip

def tips_list(request):
    tips = Tip.objects.all().order_by("-created_at")
    return render(request, "tips.html", {"tips": tips})



from django.shortcuts import render, redirect, get_object_or_404
from .models import UserTravelPlan, CustomUser
from .forms import UserTravelPlanForm

# List user travel plans
def travelplan_list(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = CustomUser.objects.get(id=user_id)
    plans = UserTravelPlan.objects.filter(user=user)
    return render(request, "travelplans/travelplan_list.html", {"plans": plans})

# Create new travel plan
def travelplan_create(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST":
        form = UserTravelPlanForm(request.POST)
        if form.is_valid():
            travel_plan = form.save(commit=False)
            travel_plan.user = user
            travel_plan.save()
            form.save_m2m()
            return redirect("travelplan_list")
    else:
        form = UserTravelPlanForm()

    return render(request, "travelplans/travelplan_form.html", {"form": form, "title": "Create Travel Plan"})

# Update travel plan (uses same form as create)
def travelplan_update(request, pk):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = CustomUser.objects.get(id=user_id)
    plan = get_object_or_404(UserTravelPlan, pk=pk, user=user)

    if request.method == "POST":
        form = UserTravelPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect("travelplan_list")
    else:
        form = UserTravelPlanForm(instance=plan)

    return render(request, "travelplans/travelplan_form.html", {"form": form, "title": "Update Travel Plan"})

# Delete plan (directly, no confirm page)
def travelplan_delete(request, pk):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = CustomUser.objects.get(id=user_id)
    plan = get_object_or_404(UserTravelPlan, pk=pk, user=user)
    plan.delete()
    return redirect("travelplan_list")



def gallery(request):
    photos = Photo.objects.all().order_by("-created_at")
    user_id = request.session.get("user_id")

    for p in photos:
        if user_id:
            p.is_liked = p.likes.filter(id=user_id).exists()
        else:
            p.is_liked = False

    # Handle photo upload
    if request.method == "POST" and "upload_photo" in request.POST:
        if not user_id:
            messages.error(request, "You must be logged in to upload a photo.")
            return redirect("login")

        user = CustomUser.objects.get(pk=user_id)
        destination_id = request.POST.get("destination")
        destination = get_object_or_404(Destination, pk=destination_id)
        image = request.FILES.get("image")
        caption = request.POST.get("caption")

        if image:
            Photo.objects.create(user=user, destination=destination, image=image, caption=caption)
            messages.success(request, "Photo uploaded successfully.")
            return redirect("gallery")

    # Handle comment
    if request.method == "POST" and "add_comment" in request.POST:
        if not user_id:
            messages.error(request, "You must be logged in to comment.")
            return redirect("login")

        user = CustomUser.objects.get(pk=user_id)
        photo_id = request.POST.get("photo_id")
        photo = get_object_or_404(Photo, pk=photo_id)
        comment = request.POST.get("comment")

        if comment:
            PhotoComment.objects.create(user=user, photo=photo, comment=comment)
            messages.success(request, "Comment added.")
            return redirect("gallery")

    # Handle like/unlike
    if request.method == "POST" and "like_photo" in request.POST:
        if not user_id:
            messages.error(request, "You must be logged in to like photos.")
            return redirect("login")

        user = CustomUser.objects.get(pk=user_id)
        photo_id = request.POST.get("photo_id")
        photo = get_object_or_404(Photo, pk=photo_id)

        if photo.likes.filter(id=user.id).exists():
            photo.likes.remove(user)
        else:
            photo.likes.add(user)

        return redirect("gallery")

    return render(
        request,
        "gallery.html",
        {
            "photos": photos,
            "destinations": Destination.objects.all(),
        },
    )



# -------- Service List --------
def service_list(request):
    services = ThirdPartyService.objects.all().order_by("-created_at")
    return render(request, "services/service_list.html", {"services": services})


# -------- Service Create --------
def service_create(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "You must be logged in to add a service.")
        return redirect("login")

    if request.method == "POST":
        form = ThirdPartyServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service added successfully.")
            return redirect("service_list")
    else:
        form = ThirdPartyServiceForm()

    return render(request, "services/service_form.html", {"form": form, "action": "Create"})


# -------- Service Update --------
def service_update(request, pk):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "You must be logged in to update a service.")
        return redirect("login")

    service = get_object_or_404(ThirdPartyService, pk=pk)
    if request.method == "POST":
        form = ThirdPartyServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully.")
            return redirect("service_list")
    else:
        form = ThirdPartyServiceForm(instance=service)

    return render(request, "services/service_form.html", {"form": form, "action": "Update"})


# -------- Service Delete --------
def service_delete(request, pk):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "You must be logged in to delete a service.")
        return redirect("login")

    service = get_object_or_404(ThirdPartyService, pk=pk)
    service.delete()
    messages.success(request, "Service deleted successfully.")
    return redirect("service_list")