import exception
from source.components.data_ingestion import DataIngestion
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import logging
import sys
from exception import CustomException

logger = logging.getLogger(__name__)
ingestion = DataIngestion()

from erp_app.models import UploadedFile

def ingest_data(request, uploaded_file, file_bytes):
    try:
        uploaded_record = UploadedFile.objects.create(
            name=uploaded_file.name,
            user=request.user,
            data=file_bytes
        )
        request.session['uploaded_file_id'] = uploaded_record.id
        return 
    except exception as e:
        raise CustomException(e, sys) #type: ignore