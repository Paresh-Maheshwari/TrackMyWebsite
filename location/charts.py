from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from .models import UserLocation


def generate_chart(request, category):
    if category == 'browser':
        chart_data = UserLocation.objects.values('user_agent_browser_family').annotate(count=Count('id'))
        chart_title = "User Browsers"
    elif category == 'device':
        chart_data = UserLocation.objects.values('user_agent_device').annotate(count=Count('id'))
        chart_title = "User Devices"
    elif category == 'activity':
        chart_data = UserLocation.objects.values('is_mobile', 'is_tablet', 'is_pc', 'is_bot').annotate(count=Count('id'))
        chart_title = "User Activity"
    elif category == 'country':
        chart_data = UserLocation.objects.values('country').annotate(count=Count('id'))
        chart_title = "User Location by Country"
    else:
        return JsonResponse({'error': 'Invalid category'})

    labels = [item[category] for item in chart_data]
    counts = [item['count'] for item in chart_data]

    chart_data = {
        'labels': labels,
        'counts': counts,
        'title': chart_title,
    }
    return JsonResponse(chart_data)

def charts(request):
    return render(request, 'charts.html')
