import random 
import string
import os
import qrcode
import requests
import json
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponse
from user_agents import parse 
from django.db.models import Q , Count
from folium import Map, Marker, Popup
from collections import Counter
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError


@login_required
def create_short_url(request):
    form = ShortURLForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        extension = form.cleaned_data['extension']
        custom_short_code = form.cleaned_data['custom_short_code']
        expiry_date = form.cleaned_data['expiry_date']
        password = form.cleaned_data['password']
        custom_note = form.cleaned_data['custom_note']
        accurate_location_tracking = form.cleaned_data['accurate_location_tracking']  
        
        if custom_short_code and ShortURL.objects.filter(short_code=custom_short_code).exists():
            form.add_error('custom_short_code', 'This shortcode is already taken.')
        else:
            chars = string.ascii_letters + string.digits
            random_short_code = ''.join(random.choice(chars) for _ in range(8))
            short_code = custom_short_code or random_short_code
        
        if extension:
            short_code += extension
        
        short_url = ShortURL(
            user=request.user,
            original_url=form.cleaned_data['original_url'],
            short_code=short_code,
            expiry_date=expiry_date,
            password=password,
            custom_note=custom_note,
            accurate_location_tracking=accurate_location_tracking 
        )
        
        try:
            short_url.save()
            messages.success(request, 'Short URL created successfully.')
            return redirect('short_url_list')
        except IntegrityError:
            messages.error(request, 'An error occurred while saving the URL.')

    context = {'form': form}
    return render(request, 'short_link/create_short_url.html', context)



# views.py
@login_required
def edit_short_url(request, short_code):
    short_url = get_object_or_404(ShortURL, short_code=short_code, user=request.user)

    if request.method == 'POST':
        form = ShortURLForm(request.POST, instance=short_url)
        if form.is_valid():
            form.save()
            messages.success(request, 'Short URL updated successfully.')
            return redirect('short_url_list')
    else:
        form = ShortURLForm(instance=short_url)

    context = {'form': form, 'short_url': short_url}
    return render(request, 'short_link/edit_short_url.html', context)

@login_required
def short_url_list(request):
    search_query = request.GET.get('search_query')
    short_urls = ShortURL.objects.filter(user=request.user).order_by('-created_at')
    
    if search_query:
        short_urls = short_urls.filter(
            Q(short_code__icontains=search_query) | Q(original_url__icontains=search_query)
        )

    paginator = Paginator(short_urls, 5)  # Show 10 URLs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    server_address = os.environ.get("SERVER_ADDRESS") # Get server address from environment variable
    context = {
        'short_urls': short_urls,
        'page_obj': page_obj,
        'server_address': server_address,
        'search_query': search_query,
    }

    return render(request, 'short_link/short_url_list.html', context)

def redirect_short_url(request, short_code):
    short_url = get_object_or_404(ShortURL, short_code=short_code)

    
    if short_url.accurate_location_tracking:  # Check if accurate location tracking is enabled
        return render(request, 'short_link/permission_request.html', {'short_url': short_url})


    if short_url.expiry_date and short_url.expiry_date < timezone.now():
        return render(request, 'short_link/link_expired.html')
    send_location(request, short_url)
    
    if short_url.password:
        if request.method == 'POST':
            entered_password = request.POST.get('password', '')
            if entered_password == short_url.password:
                return redirect(short_url.original_url)
            else:
                messages.error(request, 'Incorrect password.')
        return render(request, 'short_link/enter_password.html', {'short_url': short_url})
    
    return redirect(short_url.original_url)

@login_required
def deactivate_short_url(request, short_code):
    short_url = get_object_or_404(ShortURL, short_code=short_code, user=request.user)

    if request.method == 'POST':
        short_url.delete()
        messages.success(request, 'Short URL deactivated successfully.')
        return redirect('short_url_list')

    return render(request, 'short_link/deactivate_short_url.html', {'short_url': short_url})

@login_required
def generate_qr_code(request, short_code):
    short_url = get_object_or_404(ShortURL, short_code=short_code)
    
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    server_address = os.environ.get("SERVER_ADDRESS") # Get server address from environment variable
    qr_url = f"{server_address}/{short_url.short_code}"
    
    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


def send_location(request, short_code):

    short_url = get_object_or_404(ShortURL, short_code=short_code)
    # Check if the user is authenticated or anonymous
    if isinstance(request.user, User):  # User is authenticated
        author = request.user
    else:
        # Handle anonymous user case, for example, set author to None or a default user
        author = None

    # Use the 'ip-api.com' API to get the user's location based on IP address
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
    if ip is not None:
        ip = ip.split(",")[0]

    ip_url = f"http://ip-api.com/json/{ip}?fields=continent,country,region,regionName,city,district,zip,lat,lon,timezone,isp,org,as,asname,mobile,proxy,hosting,query"
    ip_response = requests.get(ip_url)
    ip_data = json.loads(ip_response.text)
    
    if 'latitude' in request.POST and 'longitude' in request.POST:
        # If latitude and longitude are provided in the POST request, use accurate location
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
    else:
        latitude = ip_data.get("lat", 0)
        longitude = ip_data.get("lon", 0)

    # Parse the user agent string
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)


    user_location = UserLocation(
        short_url=short_url,
        author=author,
        latitude=latitude,
        longitude=longitude,
        continent=ip_data.get("continent", ""),
        country=ip_data.get("country", ""),
        region=ip_data.get("region", ""),
        region_name=ip_data.get("regionName", ""),
        city=ip_data.get("city", ""),
        district=ip_data.get("district", ""),
        zip_code=ip_data.get("zip", ""),
        timezone=ip_data.get("timezone", ""),
        isp=ip_data.get("isp", ""),
        org=ip_data.get("org", ""),
        as_number=ip_data.get("as", ""),
        as_name=ip_data.get("asname", ""),
        mobile=ip_data.get("mobile", False),
        proxy=ip_data.get("proxy", False),
        hosting=ip_data.get("hosting", False),
        ip_address=ip_data.get("query", ""),
        map_link=f"https://www.google.com/maps/@{latitude},{longitude}",
        user_agent=user_agent_string,
        user_agent_browser_family=user_agent.browser.family,
        user_agent_browser_version=user_agent.browser.version_string,
        user_agent_os=user_agent.os.family,
        user_agent_device=user_agent.device.family,
        is_mobile=user_agent.is_mobile,
        is_tablet=user_agent.is_tablet,
        is_pc=user_agent.is_pc,
        is_bot=user_agent.is_bot,
    )

    user_location.save()
    if short_url.password:
        if request.method == 'POST':
            entered_password = request.POST.get('password', '')
            if entered_password == short_url.password:
                return redirect(short_url.original_url)
            else:
                messages.error(request, 'Incorrect password.')
        return render(request, 'short_link/enter_password.html', {'short_url': short_url})
    else:
        return redirect(short_url.original_url)

@login_required
def user_location_list(request, short_code):
    short_url = get_object_or_404(ShortURL, short_code=short_code)
    user_locations = UserLocation.objects.filter(short_url=short_url).order_by('-date', '-time')
    # Search functionality
    
    # Number of items per page
    items_per_page = 5

    # Create a Paginator instance
    paginator = Paginator(user_locations, items_per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the Page object for the current page number
    page_obj = paginator.get_page(page_number)
    
    m = Map(location=[0, 0], zoom_start=10)  # Default location
    
    if user_locations:  # Check if the list is not empty
        m = Map(location=[user_locations[0].latitude, user_locations[0].longitude], zoom_start=10)
    
        for user_location in user_locations:
            Marker(
                location=[user_location.latitude, user_location.longitude],
                popup=Popup(f"{user_location.city}, {user_location.country}"),
                icon=None,  # You can customize the icon if needed
            ).add_to(m)

    map_html = m._repr_html_()

    context = {
        'short_url': short_url,
        'user_locations': user_locations,
        'map_html': map_html,
        'page_obj': page_obj,
        
    }
    
    return render(request, 'short_link/user_location_list.html', context)


@login_required
def copy_to_clipboard(request, short_code, location_id):
    user_location = get_object_or_404(UserLocation, id=location_id)

    data = f"""
Country: {user_location.country}
City: {user_location.city}
Region: {user_location.region}
Region Name: {user_location.region_name}
District: {user_location.district}
Zip Code: {user_location.zip_code}
Timezone: {user_location.timezone}
AS Number: {user_location.as_number}
AS Name: {user_location.as_name}
IP Address: {user_location.ip_address}
ISP: {user_location.isp}
Organization: {user_location.org}
Mobile: {user_location.mobile}
Proxy: {user_location.proxy}
Hosting: {user_location.hosting}
Date: {user_location.date}
Time: {user_location.time}
User Agent: {user_location.user_agent}
Browser Family: {user_location.user_agent_browser_family}
Browser Version: {user_location.user_agent_browser_version}
Operating System: {user_location.user_agent_os}
Device: {user_location.user_agent_device}
Mobile Device: {user_location.is_mobile}
Tablet Device: {user_location.is_tablet}
PC: {user_location.is_pc}
Bot: {user_location.is_bot}
"""

    response = HttpResponse(data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=location_info.txt'
    return response




@login_required
def analysis_view(request, short_code):
    short_url = get_object_or_404(ShortURL, short_code=short_code, user=request.user)
    user_locations = UserLocation.objects.filter(short_url=short_url)

    # Count total clicks per day
    date_counts = user_locations.annotate(click_date=TruncDate('date')).values('click_date').annotate(total=Count('id')).order_by('click_date')
    
    # Convert date objects to string representations
    date_labels = [date_obj['click_date'].strftime('%Y-%m-%d') for date_obj in date_counts]
    date_counts = [date_obj['total'] for date_obj in date_counts]

    countries_counter = Counter(location.country for location in user_locations)
    browsers_counter = Counter(location.user_agent_browser_family for location in user_locations)
    platforms_counter = Counter(location.user_agent_os for location in user_locations)

    countries = dict(countries_counter)
    browsers = dict(browsers_counter)
    platforms = dict(platforms_counter)

    context = {
        'short_url': short_url,
        'countries': countries,
        'browsers': browsers,
        'platforms': platforms,
        'date_labels': date_labels,
        'date_counts': date_counts,
    }

    return render(request, 'short_link/analysis.html', context)






