from django.db import models


class CustomUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nationality = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    postal_address = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    # Dropdown values
    SEASON_CHOICES = [
        ("summer", "Summer"),
        ("winter", "Winter"),
        ("spring", "Spring"),
        ("autumn", "Autumn"),
    ]

    TRAVEL_TYPE_CHOICES = [
        ("adventure", "Adventure"),
        ("cultural", "Cultural"),
        ("leisure", "Leisure"),
        ("family", "Family"),
        ("luxury", "Luxury"),
    ]

    AGE_RANGE_CHOICES = [
        ("18-25", "18-25"),
        ("26-35", "26-35"),
        ("36-50", "36-50"),
        ("50+", "50+"),
    ]

    BUDGET_RANGE_CHOICES = [
        ("low", "Low Budget"),
        ("medium", "Medium Budget"),
        ("high", "High Budget"),
        ("luxury", "Luxury Budget"),
    ]

    travel_season = models.CharField(max_length=20, choices=SEASON_CHOICES, blank=True, null=True)
    travel_type = models.CharField(max_length=20, choices=TRAVEL_TYPE_CHOICES, blank=True, null=True)
    age_range = models.CharField(max_length=20, choices=AGE_RANGE_CHOICES, blank=True, null=True)
    budget_range = models.CharField(max_length=20, choices=BUDGET_RANGE_CHOICES, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mobile_no})"



# ----------------------------------------
# Destination Model
# ----------------------------------------
class Destination(models.Model):
    image = models.ImageField(upload_to="destinations/", blank=True, null=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    description = models.TextField()

    SEASON_CHOICES = CustomUser.SEASON_CHOICES
    TRAVEL_TYPE_CHOICES = CustomUser.TRAVEL_TYPE_CHOICES

    best_season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    travel_type = models.CharField(max_length=20, choices=TRAVEL_TYPE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}, {self.country}"


# ----------------------------------------
# Activities / Events
# ----------------------------------------
class Activity(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name="activities")
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    ACTIVITY_TYPE_CHOICES = [
        ("hiking", "Hiking"),
        ("festival", "Festival"),
        ("cultural_tour", "Cultural Tour"),
        ("local_event", "Local Event"),
        ("sports", "Sports"),
    ]

    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.destination.name}"


# ----------------------------------------
# Travel Tips
# ----------------------------------------
class Tip(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    season = models.CharField(max_length=20, choices=CustomUser.SEASON_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ----------------------------------------
# Notifications
# ----------------------------------------
class Notification(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class UserTravelPlan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="travel_plans")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name="travel_plans")
    travel_dates_start = models.DateField()
    travel_dates_end = models.DateField()
    accommodation_details = models.TextField(blank=True, null=True)
    activities = models.ManyToManyField(Activity, related_name="travel_plans", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name}'s plan for {self.destination.name}"
    

class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reviews")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.first_name} for {self.destination.name}"


class Photo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="photos")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="destination_photos/")
    caption = models.CharField(max_length=255, blank=True, null=True)
    likes = models.ManyToManyField(CustomUser, related_name="liked_photos", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.destination.name} by {self.user.first_name}"


class PhotoComment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="photo_comments")
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.first_name} on {self.photo.caption or 'Photo'}"



# Event Model
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    date = models.DateField()
    location = models.ForeignKey(Destination, on_delete=models.CASCADE)  # Linked to a Destination
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.location.name}"
		

class ThirdPartyService(models.Model):
    SERVICE_TYPE_CHOICES = [
        ("hotel", "Hotel"),
        ("flight", "Flight"),
        ("tour_operator", "Tour Operator"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    contact_url = models.URLField()
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, related_name="services")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.service_type})"


class DestinationRoute(models.Model):
    destination = models.ForeignKey(
        Destination, on_delete=models.CASCADE, related_name="routes"
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    order = models.PositiveIntegerField(default=0, help_text="Order of route points")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Route point {self.order} for {self.destination.name}"
    
		