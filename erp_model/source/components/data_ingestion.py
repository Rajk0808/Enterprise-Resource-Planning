#base library
import pandas as pd
import numpy as np

#django library
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

#app Modules
from erp_app.models import UploadedFile
from exception import CustomException
import logging

logger = logging.getLogger(__name__)

class DataIngestion:
    def ingest_data(self, request, uploaded_file = None):
        if not uploaded_file:
                    messages.error(request, "Please upload a file.")
                    return redirect('home')
    
        if not (uploaded_file.name.endswith('.csv') or uploaded_file.name.endswith('.xlsx')):
            messages.error(request, "Only CSV and Excel files are allowed.")
            return redirect('home')
        
        file_data = uploaded_file.read()
        uploaded_instance = UploadedFile.objects.create(
            user=request.user,
            name=uploaded_file.name,
            data=file_data)
        
        request.session['uploaded_file_id'] = uploaded_instance.id #type: ignore
        request.session.modified = True
        request.session.save() 
        print("SESSION FILE ID:", request.session['uploaded_file_id'])
        messages.success(request, f"✅ File '{uploaded_instance.name}' uploaded successfully!")
        return redirect('analysis')