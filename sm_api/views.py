import string
import threading
import traceback
from io import StringIO
from django.core.files import File

# Create your views here.



from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
import pytz
from .models import BusinessHours, Report, StoreStatus, Store



def generate_report(report_id):
    tz = pytz.timezone('UTC')

    dt = datetime(2023, 1, 25)

    now = datetime.now(tz).time()

    current_time = datetime.combine(dt, now, tzinfo=tz)
    last_week = current_time - timedelta(days=7)
    store_statuses = StoreStatus.objects.filter(timestamp_utc__gte=last_week).order_by('timestamp_utc')
    # Create a dictionary to store the store IDs and their status information
    store_info = {}

    # Calculate the current time and time 24 hours ago
    time_24_hours_ago = current_time - timedelta(hours=24)

    # Calculate the time 1 hour ago
    time_1_hour_ago = current_time - timedelta(hours=1)

    # Get the business hours for all stores
    business_hours = BusinessHours.objects.all()

    # Loop through each store status object and update the store_info dictionary
    for status in store_statuses:
        try:
            length_store_statuses -= 1
            store_id = status.store
            # Check if the store ID is already in the store_info dictionary
            if store_id in store_info:
                store_data = store_info[store_id]
            else:
                store_data = {
                    'uptime_last_hour': 0,
                    'uptime_last_day': 0,
                    'uptime_last_week': 0,
                    'downtime_last_hour': 0,
                    'downtime_last_day': 0,
                    'downtime_last_week': 0,
                }

            # Calculate the time difference between the status timestamp and the current time
            # Check if the status was recorded during business hours
            business_hour = business_hours.filter(store_id=store_id, day_of_week=status.timestamp_utc.weekday()).first()
            if business_hour:
                start_time = datetime.combine(status.timestamp_utc.date(), business_hour.start_time_utc, tzinfo=tz)
                end_time = datetime.combine(status.timestamp_utc.date(), business_hour.end_time_utc, tzinfo=tz )
                
                if start_time <= status.timestamp_utc <= end_time:

                    time_diff = status.timestamp_utc - start_time
                    time_diff_1_hr, time_diff_24_hr = time_diff, time_diff

                    previous_observations = store_statuses.filter(store= store_id, timestamp_utc__gte=start_time, timestamp_utc__lt = status.timestamp_utc).order_by('timestamp_utc')

                    if previous_observations:
                        previous_observation = previous_observations.last()
                        time_diff = status.timestamp_utc - previous_observation.timestamp_utc


                        if previous_observation.timestamp_utc < time_24_hours_ago < status.timestamp_utc:
                            time_diff_24_hr = status.timestamp_utc - time_24_hours_ago


                        if previous_observation.timestamp_utc < time_1_hour_ago < status.timestamp_utc:
                            time_diff_1_hr = status.timestamp_utc - time_1_hour_ago

                    
                    if start_time < time_24_hours_ago < status.timestamp_utc:
                        time_diff_24_hr = status.timestamp_utc - time_24_hours_ago

                    if status.timestamp_utc < time_24_hours_ago:       
                        time_diff_24_hr =  0


                    if start_time < time_1_hour_ago < status.timestamp_utc:
                        time_diff_1_hr = status.timestamp_utc - time_1_hour_ago

                    if status.timestamp_utc < time_1_hour_ago:       
                        time_diff_1_hr =  0

                    if status.status == 'active':
                        store_data['uptime_last_week'] += time_diff.seconds // 3600
                        if time_diff_24_hr:
                            store_data['uptime_last_day'] += time_diff_24_hr.seconds // 3600
                        if time_diff_1_hr:
                            store_data['uptime_last_hour'] += time_diff_1_hr.seconds // 60
                                
                    else:
                        store_data['downtime_last_week'] += time_diff.seconds // 3600
                        if time_diff_24_hr:
                            store_data['downtime_last_day'] += time_diff_24_hr.seconds // 3600
                        if time_diff_1_hr:
                            store_data['downtime_last_hour'] += time_diff_1_hr.seconds // 60
                    next_observations = store_statuses.filter(store= store_id, timestamp_utc__gt = status.timestamp_utc, timestamp_utc__lte = current_time)

                    if len(next_observations) == 0:
                        time_diff = end_time - status.timestamp_utc
                        time_diff_1_hr = 0
                        if current_time.date() == status.timestamp_utc.date():
                            if status.timestamp_utc < current_time < end_time:
                                time_diff_1_hr  = current_time - time_1_hour_ago
                            elif status.timestamp_utc < end_time < current_time:
                                time_diff_1_hr = end_time - status.timestamp_utc
                            if status.status == 'active':
                                store_data['downtime_last_week'] += time_diff.seconds // 3600
                                store_data['downtime_last_day'] += time_diff.seconds // 3600
                                if time_diff_1_hr:
                                    print(time_diff_1_hr)
                                    store_data['downtime_last_hour'] += time_diff_1_hr.seconds // 60
                            else:
                                store_data['uptime_last_week'] += time_diff.seconds // 3600
                                store_data['uptime_last_day'] += time_diff.seconds // 3600
                                if time_diff_1_hr:
                                    store_data['uptime_last_hour'] += time_diff_1_hr.seconds // 60
        

                    store_info[store_id] = store_data
        
        except Exception as e:

            print(e)
            print(traceback.print_exc())

    csv_data = StringIO()

    csv_data.write('store_id, uptime_last_hour, uptime_last_day, update_last_week, downtime_last_hour, downtime_last_day, downtime_last_week\n')


    for i in store_info:
        csv_data.write(f"{i.store_id}, {store_info[i]['uptime_last_hour']}, {store_info[i]['uptime_last_day']}, {store_info[i]['uptime_last_week']}, {store_info[i]['downtime_last_hour']}, {store_info[i]['downtime_last_day']}, {store_info[i]['downtime_last_week']}\n")


    report = Report.objects.get(name=report_id)
    report.report_file.save(f'{report}', File(csv_data))
    report.status = 'complete'
    report.save()

@csrf_exempt
def trigger_report(request):
    report_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    report = Report.objects.create(name=report_id)
    threading.Thread(target=generate_report, args=(report_id,)).start()
    return JsonResponse({'report_id': report_id})


def get_report(request):
    report_id = request.GET.get('report_id')
    report = get_object_or_404(Report, name=report_id)
    if report.status == 'complete':
        report_data = open(report.report_file.path, 'r').read()
        response = HttpResponse(report_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report.name}.csv"'
        return response
    else:
        return JsonResponse({'status': report.status})