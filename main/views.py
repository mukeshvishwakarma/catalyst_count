import re
import os
import csv
from django.shortcuts import render, redirect
from .models import DataFile, Company,User
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.views import View

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        
        try:
            user = User.objects.get(Q(username=username) & Q(password=password))
        except User.DoesNotExist:
            user = None

        if user is not None:
            return redirect('/upload')
        else:
            user_check = User.objects.create(username=username, password=password)
            if user_check:
                return redirect('/upload')
            
    return render(request, 'login.html')


def remove_special_characters(text):
    special_chars = "!@#$%^&*()_+{}[]|\\/:;.<>?`~\"'-="  # Define the special characters you want to remove
    
    # Use replace() to remove each special character
    for char in special_chars:
        text = text.replace(char, '')
    
    return text

def handle_uploaded_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        
        regex = re.compile(r'\b\w+(?: \w+)*\b')
        
        for row in reader:
            cleaned_text = remove_special_characters(row[6])  # Clean the text before applying regex
            dt = regex.findall(cleaned_text)
            print(dt)
            state, city = (dt[1], dt[0]) if len(dt) > 1 else (None, dt[0] if dt else None)

            Company.objects.create(
                name=row[1] or None,
                domain=row[2] or None,
                year_founded=int(float(row[3])) if row[3] else 0,
                industry=row[4] or None,
                size_range=row[5] or None,
                locality=row[6] or None,
                country=row[7] or None,
                linkedin_url=row[8] or None,
                state=state,
                city=city,
                current_employee_estimate=int(row[9]) if row[9] else 0,
                total_employee_estimate=int(row[10]) if row[10] else 0
            )

class ChunkedUploadView(View):
    def post(self, request, *args, **kwargs):
        chunk = request.FILES.get('file')
        file_id = request.POST.get('file_id')
        chunk_number = request.POST.get('chunk_number')
        total_chunks = request.POST.get('total_chunks')
        filename = request.POST.get('filename')

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
        file_path = os.path.join(upload_dir, f"{file_id}_{chunk_number}")

        with open(file_path, 'wb+') as destination:
            for chunk_part in chunk.chunks():
                destination.write(chunk_part)

        if int(chunk_number) == int(total_chunks):
            final_upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(final_upload_dir, exist_ok=True)  # Ensure the final upload directory exists
            final_file_path = os.path.join(final_upload_dir, filename)

            with open(final_file_path, 'wb+') as final_file:
                for i in range(1, int(total_chunks) + 1):
                    chunk_path = os.path.join(upload_dir, f"{file_id}_{i}")
                    with open(chunk_path, 'rb') as chunk_file:
                        final_file.write(chunk_file.read())
                    os.remove(chunk_path)

            handle_uploaded_file(final_file_path)  # Process the uploaded file

        return JsonResponse({'status': 'Chunk uploaded successfully'})

def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            # Create a new DataFile object and save the uploaded file
            data_file = DataFile(file=file, filename=file.name)
            data_file.save()
            
            # Process the uploaded file
            handle_uploaded_file(data_file.file.path)
            
            return redirect('upload_success')

    return render(request, 'upload.html')


def filter_data(request):
    if request.method == 'POST':
        try:
            kwargs = {}
            
            keyword = request.POST.get('Keyword')
            industry = request.POST.get('industry')
            state = request.POST.get('State')
            city = request.POST.get('City')
            year_founded = request.POST.get('year_founded')
            country = request.POST.get('Country')
            employee_from = request.POST.get('EmployeeFROM')
            employee_to = request.POST.get('EmployeeTO')

            if keyword:
                kwargs['name__icontains'] = keyword
            if industry:
                kwargs['industry__icontains'] = industry
            if state:
                kwargs['state__icontains'] = state
            if city:
                kwargs['city__icontains'] = city
            if year_founded:
                kwargs['year_founded'] = year_founded
            if country:
                kwargs['country__icontains'] = country
            if employee_from:
                kwargs['current_employee_estimate__gte'] = employee_from
            if employee_to:
                kwargs['total_employee_estimate__lte'] = employee_to
            
            results = Company.objects.filter(**kwargs).count()

            messages.success(request, f'{results} records found for the query')
            return render(request, 'results.html', {'count': results})

        except Exception:
            messages.error(request, 'An error occurred while processing your request. Please try again.')
            return render(request, 'filter.html')

    distinct_values = Company.objects.values(
        'industry', 'city', 'state', 'country', 'year_founded', 'total_employee_estimate', 'current_employee_estimate'
    )

    # Use set comprehensions to extract distinct values
    inds_comp = {item['industry'] for item in distinct_values}
    city_dt = {item['city'] for item in distinct_values}
    sts_dt = {item['state'] for item in distinct_values}
    coun_dt = {item['country'] for item in distinct_values}
    year_dt = {item['year_founded'] for item in distinct_values}
    tee_dt = {item['total_employee_estimate'] for item in distinct_values}
    cee_dt = {item['current_employee_estimate'] for item in distinct_values}
    return render(request, 'filter.html', {
        'inds_comp': sorted(inds_comp),
        'city_dt': sorted(city_dt),
        'sts_dt': sorted(sts_dt),
        'coun_dt': sorted(coun_dt),
        'year_dt': sorted(year_dt),
        'tee_dt': sorted(tee_dt),
        'cee_dt': sorted(cee_dt),
    })



def upload_success(request):
    return render(request, 'upload_success.html')


def userdata(request):  
    ren = User.objects.all().order_by('created_at').reverse()  
    return render(request,"user.html",{'ren':ren})  


def adduserdata(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            user = User.objects.get(Q(username=username))
        except User.DoesNotExist:
            user = None

        if user is not None:
            messages.error(request, 'User already exists')
        else:
            user_check = User.objects.create(username=username, password=password)
            if user_check:
                messages.success(request, 'New User Added')
                return redirect('/user')
            
    return render(request, 'adduser.html')
