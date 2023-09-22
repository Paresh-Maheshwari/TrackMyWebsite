import os
import secrets
from django.shortcuts import redirect,render
from .forms import UserCreateForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from .models import *
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth import get_user_model

#######################  Login  start   ############################
@login_required
def logoutaccount(request):
    logout(request)
    return redirect('home')


def login_view(request):
    if request.method == 'GET':
        return render(request, 'registration/login.html', {'form': AuthenticationForm})

    # Get the username or email and password from the form
    username_or_email = request.POST['username_or_email']
    password = request.POST['password']

    # Look up the user by username or email
    user = User.objects.filter(Q(username=username_or_email) | Q(email=username_or_email)).first()

    if user is None:
        # If the user does not exist, display an error message
        return render(request, 'registration/login.html', {'form': AuthenticationForm(), 'error': 'The username or email is not registered. Please sign up.'})

    if not user.is_active:
        return render(request, 'registration/login.html', {'form': AuthenticationForm(), 'error': 'Your account is not verified. Please check your email and follow the verification link.'})

    # Authenticate the user using their username or email and password
    user = authenticate(request, username=user.username, password=password)

    if user is None:
        return render(request, 'registration/login.html', {'form': AuthenticationForm(), 'error': 'Username or email and password do not match'})

    login(request, user)
    return redirect('home')


#######################  Login  stop   ############################

#######################  Register start ############################
@receiver(models.signals.pre_save, sender=TokenSummary)
def generate_link(sender, instance, **kwargs):
    # Get the server address from the environment variable
    server_address = os.environ.get("SERVER_ADDRESS")

    # If the server address is not set, use a default value
    if not server_address:
        server_address = "localhost"

    token = instance.token
    slug = slugify(token)
    link = f"{server_address}/location/{slug}"
    instance.link = link


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_verification_email(request, user):
    # Generate a random verification code
    verification_code = secrets.token_hex(16)
    
    # Save the verification code to the database
    VerificationCode.objects.create(
        user=user,
        code=verification_code,
        expires_at=timezone.now() + timezone.timedelta(hours=24)
    )
    server_address = os.environ.get("SERVER_ADDRESS")
    
    # Render the verification email template
    context = {
        'user': user,
        'verification_link': f"{server_address}/verify/{verification_code}"
    }
    html_message = render_to_string('registration/verification_email.html', context)
    text_message = strip_tags(html_message)
    
    # Construct the verification email subject and recipient list
    subject = 'Email Verification'
    recipient_list = [user.email]
    from_email = 'noreply@example.com'
    
    # Create an EmailMultiAlternatives object
    email = EmailMultiAlternatives(subject, text_message, from_email, recipient_list)
    email.attach_alternative(html_message, "text/html")
    
    # Send the email
    email.send()


def resend_verification(request):
    if request.method == 'GET':
        return render(request, 'registration/resend_verification.html')
    
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            return render(request, 'registration/resend_verification.html', {'error': 'No inactive user found with this email.'})
        
        send_verification_email(request, user)
        return render(request, 'registration/resend_verification.html', {'success': 'Verification email sent. Please check your email.'})


def verify(request, code):
    # Look up the verification code in the database
    try:
        ver_code = VerificationCode.objects.get(code=code)
    except VerificationCode.DoesNotExist:
        # If the code is invalid, display an error message
        return render(request, 'registration/verify.html', {'error': 'Invalid verification code'})

    # Check if the verification code has expired
    if timezone.now() > ver_code.expires_at:
        # If the code has expired, display an error message
        return render(request, 'registration/verify.html', {'error': 'Verification code has expired'})

    # Activate the user's account
    user = ver_code.user
    user.is_active = True
    user.save()

    #after verification delete the code
    ver_code.delete()
    
    # Display a success message
    return render(request, 'registration/verify.html', {'success': 'Your account has been verified'}) 
    
def register(request):  
    if request.method == "GET":
        return render(request, "registration/register.html", {"form": UserCreateForm})

    if request.POST["password1"] != request.POST["password2"]:
        # If the passwords do not match, display an error message
        return render(
            request,
            "registration/register.html", 
            {"form": UserCreateForm, "error": "Passwords do not match"},
        )

    # Check if the provided email already exists in the database
    if User.objects.filter(email=request.POST["email"]).exists():
        # If the email already exists, display an error message
        return render(
            request,
            "registration/register.html",
            {"form": UserCreateForm, "error": "Email already taken. Choose new email."},
        )

    # Check if the provided username already exists in the database
    if User.objects.filter(username=request.POST["username"]).exists():
        # If the username already exists, display an error message
        return render(
            request,
            "registration/register.html",
            {"form": UserCreateForm, "error": "Username already taken. Choose a different username."},
        )

    try:
        # Create a new user using the provided email, username, and password
        author = User.objects.create_user(
            username=request.POST["username"],
            email=request.POST["email"], 
            password=request.POST["password1"]
        )
        # Set the user's is_active field to False to prevent login until the email is verified
        author.is_active = False
        author.save()

        # Generate a random token with 64 characters
        token = secrets.token_hex(8)

        # Check if the token already exists in the database
        if TokenSummary.objects.filter(token=token).exists():
            # If the token already exists, generate a new token
            token = secrets.token_hex(8)
    
        # Create a new TokenSummary object using the form data
        token_summary = TokenSummary.objects.create(
            author=author, token=token
        )

        # Generate the unique link for the user using the generate_link function
        generate_link(sender=TokenSummary, instance=token_summary) 
        # Send the email verification code
        send_verification_email(request, author)
        
        # Display a message indicating that the email has been sent
        return render(
            request,
            "registration/register.html",
            {"form": UserCreateForm, "success": "Verification email sent. Please check your email."},
        )
    except Exception as e:
        # If there was an error creating the user, display an error message
        return render(
            request,
            "registration/register.html",
            {"form": UserCreateForm, "error": str(e)},
        )

#########################  Register end  ##############################


###################### Reset Password start  ##################################

def send_reset_email(request, user):
    # Generate a random reset code
    reset_code = secrets.token_hex(16)
    
    # Save the reset code to the database
    ResetCode.objects.create(
        user=user,
        code=reset_code,
        expires_at=timezone.now() + timezone.timedelta(hours=24)
    )
    server_address = os.environ.get("SERVER_ADDRESS")
    
    # Render the password reset email template
    context = {
        'user': user,
        'reset_link': f"{server_address}/reset/{reset_code}"
    }
    html_message = render_to_string('registration/password_reset_email.html', context)
    text_message = strip_tags(html_message)
    
    # Construct the reset email subject and recipient list
    subject = 'Password Reset'
    recipient_list = [user.email]
    from_email = 'noreply@example.com'
    
    # Create an EmailMultiAlternatives object
    email = EmailMultiAlternatives(subject, text_message, from_email, recipient_list)
    email.attach_alternative(html_message, "text/html")
    
    # Send the email
    email.send()




def forgot_password(request):
    #check if the request is a GET or POST
    if request.method == 'GET':
        return render(request, 'registration/forgot_password.html')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            UserModel = get_user_model()
            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                user = None
            if user is not None:
                send_reset_email(request, user)
                return render(request, 'registration/forgot_password_done.html')
    else:
        form = ForgotPasswordForm()
    return render(request, 'registration/forgot_password.html', {'error': 'The email is not registered. Please sign up.'})

def reset_password(request, reset_code):
    # Get the reset code from the database
    try:
        reset_code_obj = ResetCode.objects.get(code=reset_code)
    except ResetCode.DoesNotExist:
        # Return an error if the reset code is not found
        return render(request, 'registration/reset_password_invalid.html')
    
    # Check if the reset code is expired
    if timezone.now() > reset_code_obj.expires_at:
        # If the code has expired, display an error message
        return render(request, 'registration/reset_password_invalid.html', {'error': 'This token is expired. Click here to resend.'})
    
    # The reset code is valid, so allow the user to reset their password
    if request.method == 'POST':
        # Process the form data to reset the password
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            # Update the user's password
            user = reset_code_obj.user
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Delete the reset code from the database
            reset_code_obj.delete()
            
            # Redirect to the password reset successful page
            return render(request, 'registration/reset_password_done.html')
    else:
        # Display the password reset form
        form = ResetPasswordForm()
    return render(request, 'registration/reset_password.html', {'form': form})

########################## Reset Password end  ##################################