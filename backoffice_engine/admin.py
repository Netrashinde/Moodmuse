from django.contrib import admin
from .models import User, DetectedEmotion, Plan, Subscription, Feedback

admin.site.register(User)
admin.site.register(DetectedEmotion)
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(Feedback)

