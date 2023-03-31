import django
django.setup()
from datetime import datetime, timedelta
from sm_api.models import Store, BusinessHours, StoreStatus
import pytz
import csv


def populate_store_table(csv_file):
    with open(csv_file) as f:
        reader = csv.reader(f)
        # First skip the header of the csv
        next(reader)
        for row in reader:
            store_id, timezone_str = row
            timezone_str = timezone_str if timezone_str else 'America/Chicago'
            store = Store.objects.create(store_id=int(
                store_id), timezone_str=timezone_str)
            store.save()


def populate_business_hours_table(input_file_path):

    existing_rows = set()

    rows = []

    # Load the data from the input CSV file
    with open(input_file_path, 'r') as input_file:
        csv_reader = csv.reader(input_file)
        # Skip the header row
        next(csv_reader)
        for row in csv_reader:
            store_id, day, start_time_local, end_time_local = row

            # Get the store's timezone from the Django model
            store, created = Store.objects.get_or_create(store_id=store_id)
            tz = pytz.timezone(store.timezone_str)

            # Localize the start and end times
            start_time_local = datetime.strptime(start_time_local, '%H:%M:%S')
            start_time_local = tz.localize(start_time_local)
            end_time_local = datetime.strptime(end_time_local, '%H:%M:%S')
            end_time_local = tz.localize(end_time_local)
            start_time_local += timedelta(days=int(day))
            end_time_local += timedelta(days=int(day))

            # Localize to original timezone
            new_tz_utc = pytz.timezone('utc')
            start_time_utc = start_time_local.astimezone(new_tz_utc)
            end_time_utc = end_time_local.astimezone(new_tz_utc)

            # Check if the start and end times have different weekday integers
            if start_time_local.weekday() != end_time_local.weekday():
                # Add two rows: one for the first day and another for the second day
                row1 = [store_id, start_time_local.weekday(), start_time_utc.time(
                ), datetime.strptime('23:59:59', '%H:%M:%S').time()]
                row2 = [store_id, end_time_local.weekday(), datetime.strptime(
                    '00:00:00', '%H:%M:%S').time(), end_time_utc.time()]
                # Add the rows to the list of rows if they don't already exist
                if (store_id, row1[1]) not in existing_rows:
                    rows.append(row1)
                    existing_rows.add((store_id, row1[1]))
                    BusinessHours.objects.get_or_create(store=store, day_of_week=int(
                        row1[1]), start_time_utc=row1[2], end_time_utc=row1[3])

                if (store_id, row2[1]) not in existing_rows:
                    rows.append(row2)
                    existing_rows.add((store_id, row2[1]))
                    BusinessHours.objects.get_or_create(store=store, day_of_week=int(
                        row2[1]), start_time_utc=row2[2], end_time_utc=row2[3])
            else:
                # Add one row for the current day
                row = [store_id, start_time_local.weekday(
                ), start_time_utc.time(), end_time_utc.time()]
                # Add the row to the list of rows if it doesn't already exist
                if (store_id, row[1]) not in existing_rows:
                    rows.append(row)
                    existing_rows.add((store_id, row[1]))
                    BusinessHours.objects.get_or_create(store=store, day_of_week=int(
                        row[1]), start_time_utc=row[2], end_time_utc=row[3])



def populate_store_status_table(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        index = 0
        already_in_db = StoreStatus.objects.all().count()
        if already_in_db:
            for i in range(already_in_db): 
                next(reader)
        # for i in range():
        #     next(reader)
        
        store_status_list = []
        for row in reader:

            store_id = row[0]
            status = row[1]
            timestamp_str = row[2]

            # Get the Store object for this store_id
            store, created = Store.objects.get_or_create(store_id=int(store_id))
            
            # Convert the timestamp string to a datetime object
            try:
                timestamp_utc = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f %Z')
            except ValueError:         
                timestamp_utc = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S %Z')
            timestamp_utc = pytz.utc.localize(timestamp_utc)
           
            store_status_list.append(StoreStatus(store=store, timestamp_utc=timestamp_utc, status=status))
            
            index += 1
            if index % 1000 == 0:
                print(index)
                StoreStatus.objects.bulk_create(store_status_list)
                store_status_list = []
        if store_status_list:
            StoreStatus.objects.bulk_create(store_status_list)
