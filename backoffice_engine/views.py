from django.shortcuts import render,redirect
from django.contrib import messages
from backoffice_engine.models import *
from backoffice_engine.forms import register_form,UpdateProfileForm,DetectedEmotionForm
import sys
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from Moodmuse import settings
from django.core.mail import send_mail
import random
from .mood_muse_detaction_analyzer import analyze_mood_from_image
import os,json
from .mood_muse_song import generate_music, generate_music_file
from.models import Feedback



def Index(request):
    feedbacks = Feedback.objects.all()  # ✅ Make sure it's always defined

    if request.session.get("has_free_trial"):
        end_date = request.session.get("free_trial_end")
        messages.info(request, f"You have started your free trial for 15 days. It will expire on {end_date}.")

        del request.session["has_free_trial"]
        del request.session["free_trial_end"]

    return render(request, 'index.html', {"feedbacks": feedbacks})


def Login(request):
    if request.method=="POST":
        uemail=request.POST["email"]
        pwd = request.POST["password"]

        e=User.objects.filter(email=uemail,password=pwd).count()
        print(f"Total User Count : {e}")
        if e == 1:
            e=User.objects.get(email=uemail)
            request.session["id"]=e.id
            request.session["name"]=e.name
            request.session["email"]=e.email
            return redirect("/Index/")
        else:
            messages.error(request,"Invaild username or password")
            return render(request,'login.html')
    else:
        return render(request,'login.html')


def Register(request):
    if request.method == "POST":
        f = register_form(request.POST)
        print(f"Register Form Error : {f.errors}")
        if f.is_valid():
            try:
                f.save()
            except:
                print(f"Form Save Error: {sys.exc_info()}")
        return render(request,"index.html")
    else:
        f = register_form()
        return render(request,"register.html", {'f': f})
    

def user_profile(request):
    if request.session.get("id"): 
        user = User.objects.get(id=request.session["id"])  
        if request.method == 'POST':
            form = UpdateProfileForm(request.POST, instance=user)  
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('/show_profile/')
        else:
            return render(request, 'profile.html', {'user': user})
    else:
        return render(request,"login.html")


def update_profile(request, id):
    if request.session.get("id"): 
        user_object = User.objects.get(id=id)
        form = UpdateProfileForm(request.POST, instance=user_object)
        if form.is_valid():
            form.save()
            return redirect("/show_profile/")
        return render(request, 'profile.html', {'user': user_object})
    else:
        return render(request,"login.html")


def Logout(request):
    try:
        request.session.flush()
    except :
        pass
    return redirect("/Login/")

def show_profile(request):
    if request.session.get("id"):
        try:
            user_object = User.objects.get(id=request.session.get("id"))
            active_sub = Subscription.objects.filter(user=user_object, is_active=True).first()
        except User.DoesNotExist:
            return render(request, "login.html")

        return render(request, 'show_profile.html', {
            "user": user_object,
            "active_sub": active_sub
        })
    else:
        return render(request, "login.html")


@csrf_exempt
def plan_details(request):
    # Fetch all active plans
    plans = list(Plan.objects.filter(is_active=True))

    # Add Free Trial as a virtual plan
    free_trial_plan = {
        "id": "free_trial",
        "name": "Free Trial",
        "price": 0,
        "description": "Enjoy 15 days free premium access!",
        "duration_days": 15,
        "credit": 100
    }
    plans.insert(0, free_trial_plan)

    # Handle POST (plan selection)
    if request.method == "POST":
        user_id = request.session.get("id")
        if not user_id:
            messages.error(request, "Please log in to select a plan.")
            return redirect('/Login/')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found. Please log in again.")
            return redirect('/Login/')

        plan_id = request.POST.get("planid")

        if plan_id == "free_trial":
            # Check if user already used the free trial
            user_has_trial = Subscription.objects.filter(user=user, plan__name="Free Trial").exists()
            if user_has_trial:
                return render(request, "subscription.html", {
                    "plans": plans,
                    "user_has_trial": True,
                    "active_sub": Subscription.objects.filter(user=user, is_active=True).first()
                })

            # Create Free Trial Plan if not already in DB
            plan, _ = Plan.objects.get_or_create(
                name="Free Trial",
                defaults={
                    "price": 0,
                    "description": "15 days free premium access!",
                    "duration_days": 15,
                    "is_active": False,
                    "credit": 100
                }
            )

            # Create subscription
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=plan.duration_days)

            Subscription.objects.create(
                user=user,
                plan=plan,
                price=0,
                credit=100,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )

            messages.success(request, "Free Trial activated! Enjoy your premium access.")
            return redirect("/Index/")

        else:
            # Paid plan
            try:
                plan = Plan.objects.get(id=plan_id, is_active=True)
                start_date = timezone.now().date()
                end_date = start_date + timedelta(days=plan.duration_days)

                Subscription.objects.create(
                    user=user,
                    plan=plan,
                    price=plan.price,
                    credit=plan.credit,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True
                )

                messages.success(request, f"{plan.name} plan activated successfully!")
                return redirect("/Index/")
            except Plan.DoesNotExist:
                messages.error(request, "Invalid plan selected.")
                return redirect("/plan_details/")

    # Handle GET request (load plans)
    user_has_trial = False
    active_sub = None
    user = None
    user_id = request.session.get("id")

    if user_id:
        try:
            user = User.objects.get(id=user_id)
            user_has_trial = Subscription.objects.filter(user=user, plan__name="Free Trial").exists()
            active_sub = Subscription.objects.filter(user=user, is_active=True).first()
        except User.DoesNotExist:
            user = None

    return render(request, "subscription.html", {
        "plans": plans,
        "user_has_trial": user_has_trial,
        "active_sub": active_sub
    })



def Forgot(request):
    if request.method == "POST":
        otp1 = random.randint(10000, 99999)
        e = request.POST['email']
        request.session['temail']=e

        obj = User.objects.filter(email=e).count()

        if obj == 1:
            val = User.objects.filter(email = e).update(otp=otp1 , otp_used=0)
            subject = 'OTP Verification'
            message = str(otp1)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [e,]

            send_mail(subject, message, email_from, recipient_list)

            print("------------mail send---------")
            return render(request, 'Set_password.html')
        else:
            messages.error(request,"Invalid email Id")
            return render(request, 'forgot.html')
    else:
        return render(request,"forgot.html")
    
def Set_password(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        pwd = request.POST["password"]
        cpwd = request.POST["confirm-password"]
        e =  request.session['temail']

        val = User.objects.filter(email=e,otp=otp,otp_used=0).count()

        if val == 1:
            if pwd == cpwd :
                obj = User.objects.filter(email=e).update(password=pwd,otp_used=1)   
                return redirect("/Login/")
            else:
                messages.error(request,"Password and confirm password not match")
                return render(request,"set_password.html")
        else:
                 messages.error(request,"Invalid OTP")
                 return render(request,"set_password.html")
    else:
         return render(request,"set_password.html")
    


@csrf_exempt
def mood_muse_detection(request):
    # ✅ Check if user is logged in via session
    if not request.session.get("id"):
        return redirect("/Login/")

    if request.method == 'POST':
        form = DetectedEmotionForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['photos']
            image_bytes = uploaded_file.read()
            data = form.save(commit=False)
            mood_result = analyze_mood_from_image(image_bytes, uploaded_file.content_type)
            data.detected_emotion = mood_result
            data.save()
            print(f"Cleaned mood result: {mood_result}")
            return render(request, 'mood_muse_result.html', {'detected_emotion_data': data})
        else:
            messages.error(request, "Please upload a valid image.")
    else:
        form = DetectedEmotionForm()

    return render(request, 'mood_muse_detection.html', {'form': form})



def mood_muse_result(request):
    mood_data = request.session.get('mood_data')
    image_url = request.session.get('image_url')

    if not mood_data or not image_url:
        messages.error(request, "No analysis found. Please upload a photo.")
        return redirect('/mood_muse_detection/')

    song_type = "uplifting song"
    if mood_data.get("sad", 0) > 50:
        song_type = "very sad song"
    elif mood_data.get("angry", 0) > 50:
        song_type = "calm song"
    elif mood_data.get("happy", 0) > 50:
        song_type = "celebration song"

    return render(request, 'mood_muse_result.html', {
        'image_url': image_url,
        'mood_data': mood_data,
        'song_type': song_type
    })


from .models import DetectedEmotion  # make sure this import is correct
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import json

@csrf_exempt
def generate_song(request, id):
    if request.method == 'POST':
        last_emotion = DetectedEmotion.objects.get(id=id)
        preferred_song = request.POST.get('preferred_song', 'happy')
        music_file = generate_music_file(prompt_text=preferred_song)

        last_emotion.song = music_file
        last_emotion.user_song = preferred_song
        last_emotion.save()

        return render(request, 'generate_song_result.html', {"result": last_emotion})

    return redirect('/mood_muse_detection/')
   

def feedback_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        rating = request.POST.get('rating')
        description = request.POST.get('description')
        Feedback.objects.create(name=name, rating=rating, description=description)
        return redirect('index')  
    return render(request, 'feedback_form.html')



def user_history(request):
    current_user_id = request.session.get('id')

    # Ensure current_user_id is valid before querying
    if not current_user_id:
        return redirect('login')  # or handle unauthenticated case as needed

    # Get user-specific history
    all_history = DetectedEmotion.objects.filter(user=current_user_id)

    return render(request, 'user_history.html', {
        'all_history': all_history,
        'current_user_id': current_user_id,
    })
