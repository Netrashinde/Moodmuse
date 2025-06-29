from django.db import models

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_used = models.BooleanField(default=False)
    contact = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='backoffice_engine/user_photos')
    
    class Meta:
        db_table = "User"

    def __str__(self):                                                                                             
        return self.name


class DetectedEmotion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    song = models.FileField(upload_to='backoffice_engine/songs', null=True, blank=True)
    user_song = models.TextField(null=True, blank=True)
    detected_emotion = models.CharField(max_length=255, null=True, blank=True)
    photos = models.ImageField(upload_to='backoffice_engine/user_upload_photo')

    def __str__(self):
        return f"{self.user} - {self.song} - {self.detected_emotion}"
    
class Plan(BaseModel):
    name = models.CharField(max_length=100)                                          
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    is_active = models.BooleanField(default=True)
    duration_days = models.IntegerField(help_text="Duration of the plan in days")
    credit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Subscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    
    
    def __str__(self):
        return f"{self.user.name}  {self.plan} (Active: {self.is_active})"
    
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    rating = models.IntegerField()
    description = models.TextField()     

    def __str__(self):
        return f"{self.name} - {self.rating} stars"