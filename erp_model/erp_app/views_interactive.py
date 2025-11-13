import base64
import logging
import sys
import os
import pickle
import pandas as pd

from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest

import source.components.data_analysis as da 
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
