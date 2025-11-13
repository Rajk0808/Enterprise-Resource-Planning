from source.components.data_analysis import BasisDataAnalysis
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import logging
import sys
from exception import CustomException

