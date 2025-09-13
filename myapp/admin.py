from django.contrib import admin
from .models import (
    CustomUser, Destination, Activity, Tip, Notification,
    UserTravelPlan, Review, Photo, PhotoComment, Event,
    ThirdPartyService, DestinationRoute
)

# ----------------------------------------
# CustomUser Admin
# ----------------------------------------
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "mobile_no", "travel_season", "travel_type", "created_at")
    search_fields = ("first_name", "last_name", "email", "mobile_no", "city")
    list_filter = ("travel_season", "travel_type", "age_range", "budget_range")
    ordering = ("-created_at",)


# ----------------------------------------
# Destination Admin
# ----------------------------------------
class DestinationRouteInline(admin.TabularInline):
    model = DestinationRoute
    extra = 1

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "best_season", "travel_type", "created_at")
    search_fields = ("name", "city", "country")
    list_filter = ("best_season", "travel_type")
    inlines = [DestinationRouteInline]


# ----------------------------------------
# Activity Admin
# ----------------------------------------
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "destination", "activity_type", "start_date", "end_date", "created_at")
    search_fields = ("title", "destination__name")
    list_filter = ("activity_type",)
    ordering = ("-created_at",)


# ----------------------------------------
# Tip Admin
# ----------------------------------------
@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ("title", "season", "created_at")
    search_fields = ("title",)
    list_filter = ("season",)
    ordering = ("-created_at",)


# ----------------------------------------
# Notification Admin
# ----------------------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    ordering = ("-created_at",)


# ----------------------------------------
# UserTravelPlan Admin
# ----------------------------------------
@admin.register(UserTravelPlan)
class UserTravelPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "destination", "travel_dates_start", "travel_dates_end", "created_at")
    search_fields = ("user__first_name", "destination__name")
    ordering = ("-created_at",)
    filter_horizontal = ("activities",)


# ----------------------------------------
# Review Admin
# ----------------------------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "destination", "rating", "created_at")
    search_fields = ("user__first_name", "destination__name", "comment")
    list_filter = ("rating",)
    ordering = ("-created_at",)


# ----------------------------------------
# Photo Admin
# ----------------------------------------
class PhotoCommentInline(admin.TabularInline):
    model = PhotoComment
    extra = 1

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("user", "destination", "caption", "created_at")
    search_fields = ("user__first_name", "destination__name", "caption")
    ordering = ("-created_at",)
    inlines = [PhotoCommentInline]
    filter_horizontal = ("likes",)


# ----------------------------------------
# PhotoComment Admin
# ----------------------------------------
@admin.register(PhotoComment)
class PhotoCommentAdmin(admin.ModelAdmin):
    list_display = ("user", "photo", "created_at")
    search_fields = ("user__first_name", "photo__caption", "comment")
    ordering = ("-created_at",)


# ----------------------------------------
# Event Admin
# ----------------------------------------
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "date", "created_at")
    search_fields = ("title", "location__name")
    ordering = ("-created_at",)


# ----------------------------------------
# ThirdPartyService Admin
# ----------------------------------------
@admin.register(ThirdPartyService)
class ThirdPartyServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "service_type", "destination", "created_at")
    search_fields = ("name", "destination__name")
    list_filter = ("service_type",)
    ordering = ("-created_at",)


# ----------------------------------------
# DestinationRoute Admin
# ----------------------------------------
@admin.register(DestinationRoute)
class DestinationRouteAdmin(admin.ModelAdmin):
    list_display = ("destination", "latitude", "longitude", "order", "created_at")
    search_fields = ("destination__name",)
    ordering = ("destination", "order")
