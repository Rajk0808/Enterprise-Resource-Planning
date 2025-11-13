# erp_app/views.py

import logging
import sys
import os
import io
import pandas as pd
import pickle
import base64
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponseRedirect
from exception import CustomException
from source.pipeline import data_ingestion_pipeline
from source.components.data_analysis import (
    BasisDataAnalysis,
    DataQualityCheck,
    UniVariate,
    BiVariateNumerical,
    BiVariateCategorical,
    MultiVariate
)

# Initialize objects
analysis_basic = BasisDataAnalysis()
quality_check = DataQualityCheck()
univariate = UniVariate()
bivariate_num = BiVariateNumerical()
bivariate_cat = BiVariateCategorical()
multivariate = MultiVariate()
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# HOME & AUTHENTICATION VIEWS
# -------------------------------------------------------------------------

def home(request):
    logger.info("Home page accessed by user: %s", request.user)
    return render(request, 'home.html')


@login_required
def upload_file(request):
    try:
        if request.method == "POST":
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                messages.error(request, "No file selected.")
                return redirect('home')

            file_bytes = uploaded_file.read()
            df = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8', on_bad_lines='skip')
            df_json = df.to_json(orient='records')

            # Save JSON string to session
            request.session['df_json'] = df_json
            request.session['step'] = 'overview'
            messages.success(request, "File uploaded successfully!")
            return redirect('analysis')

        return render(request, 'home.html')
    except Exception as e:
        raise CustomException(e, sys) #type: ignore


@login_required
def analysis(request):
    try:
        file_id = request.session.get('uploaded_file_id')
        base = BasisDataAnalysis()
        result = base.generate_summary(request, file_id)
        if isinstance(result, HttpResponseRedirect):
            return result
        return render(request, 'analysis.html', result) #type: ignore
    except Exception as e:
        raise CustomException(e, sys) #type: ignore


def final_report(request):
    try:
        logger.info("Final Report page opened by user: %s", request.user)
        return render(request, 'final_report.html')
    except Exception as e:
        raise CustomException(e, sys) #type: ignore


def contact(request):
    try:
        logger.info("Contact page opened by user: %s", request.user)
        return render(request, 'contact.html')
    except Exception as e:
        raise CustomException(e, sys) #type: ignore


def user_login(request):
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    logger.info(f"✅ User '{username}' logged in successfully.")
                    return redirect('home')
            messages.error(request, "Invalid credentials.")
        else:
            form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})
    except Exception as e:
        raise CustomException(e, sys) #type: ignore


def user_register(request):
    try:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                logger.info(f"🆕 New user registered: {user.username}")
                return redirect('home')
            messages.error(request, "Registration failed. Try again.")
        else:
            form = UserCreationForm()
        return render(request, 'register.html', {'form': form})
    except Exception as e:
        raise CustomException(e, sys) #type: ignore


@login_required
def user_logout(request):
    try:
        logger.info(f"🚪 User '{request.user.username}' logged out.")
        logout(request)
        return redirect('login')
    except Exception as e:
        raise CustomException(e, sys) #type: ignore

# -------------------------------------------------------------------------
# INTERACTIVE ANALYSIS LOGIC
# -------------------------------------------------------------------------

SESSION_KEY = 'interactive_df_b64'
STEP_KEY = 'interactive_step'
ANALYSIS_RESULT_KEY = 'interactive_analysis_result'


# Helpers
def _save_df_to_session(request, df: pd.DataFrame):
    """Serialize DataFrame and store in Django session safely."""
    pickled = pickle.dumps(df)
    encoded = base64.b64encode(pickled).decode('utf-8')
    request.session['dataframe'] = encoded

def _load_df_from_session(request):
    df_json = request.session.get('df_json', None)
    if not df_json:
        return None
    return pd.read_json(io.StringIO(df_json))


def _clear_session(request):
    for key in ['df_json', 'step']:
        if key in request.session:
            del request.session[key]


# -------------------------------------------------------------------------
# MAIN RECURSIVE VIEW
# -------------------------------------------------------------------------

@login_required  #type: ignore
def interactive_analysis(request):
    """
    Handles the interactive analysis process after data upload & base summary.
    The dataset is already stored in session by the previous 'analysis' view.
    """

    try:
        df = _load_df_from_session(request)
        if df is None:
            messages.error(request, "No dataset found in session. Please upload a file first.")
            return redirect('upload_file')

        step = request.session.get('step', 'overview')
        # STEP 0️⃣: Overview screen
        if step == 'overview':
            if request.method == 'POST':
                next_step = request.POST.get('next_step')
                if next_step:
                    request.session['step'] = next_step
                    return redirect('interactive_analysis')

            df_shape = df.shape
            df_dtypes = df.dtypes.astype(str).to_dict()
            df_summary = df.describe(include='all').to_html(classes='table table-striped', border=0)

            return render(request, 'interactive_analysis.html', {
                'step': step,
                'df_shape': df_shape,
                'df_dtypes': df_dtypes,
                'df_summary': df_summary,
            })

        # STEP 1️⃣: Ask what transformation or analysis user wants
        if step == 'transform_choice':
            if request.method == 'POST':
                choice = request.POST.get('choice')
                if choice == 'heterogeneous':
                    request.session['step'] = 'heterogeneous'
                elif choice == 'missing':
                    request.session['step'] = 'missing'
                elif choice == 'duplicate':
                    request.session['step'] = 'duplicate'
                elif choice == 'outlier':
                    request.session['step'] = 'outlier'
                elif choice == 'skip':
                    request.session['step'] = 'analysis'
                return redirect('interactive_analysis')
            return render(request, 'interactive_analysis.html', {'step': step})

        # STEP 2️⃣: Heterogeneous data detection
        elif step == 'heterogeneous':
            # 👉 TODO: Call your pipeline function to detect and display heterogeneous columns
            # Example: hetero_cols = data_pipeline.detect_heterogeneous(df)
            hetero_cols = []  # placeholder
            if request.method == 'POST':
                # 👉 TODO: Call your base class method to handle transformation
                # Example: df = data_pipeline.handle_heterogeneous(df)
                _save_df_to_session(request, df)
                messages.success(request, "Handled heterogeneous columns successfully.")
                request.session['step'] = 'transform_choice'
                return redirect('interactive_analysis')
            return render(request, 'interactive_analysis.html', {'step': step, 'columns': hetero_cols})

        # STEP 3️⃣: Missing value check
        elif step == 'missing':
            # 👉 TODO: Use your own method to detect columns with missing data
            missing_cols = []  # placeholder
            if request.method == 'POST':
                column = request.POST.get('column')
                method = request.POST.get('method')
                if column and method:
                    # 👉 TODO: Replace with your missing value handler
                    # Example: df = data_pipeline.handle_missing(df, column, method)
                    _save_df_to_session(request, df)
                    messages.success(request, f"Missing values in '{column}' handled using {method}.")
                    request.session['step'] = 'transform_choice'
                    return redirect('interactive_analysis')
            return render(request, 'interactive_analysis.html', {'step': step, 'columns': missing_cols})

        # STEP 4️⃣: Duplicate check
        elif step == 'duplicate':
            # 👉 TODO: Use your own method to detect duplicates
            dup_count = 0  # placeholder
            if request.method == 'POST':
                # 👉 TODO: Replace with your duplicate handler
                # Example: df = data_pipeline.remove_duplicates(df)
                _save_df_to_session(request, df)
                messages.success(request, f"Removed {dup_count} duplicate rows.")
                request.session['step'] = 'transform_choice'
                return redirect('interactive_analysis')
            return render(request, 'interactive_analysis.html', {'step': step, 'duplicates': dup_count})

        # STEP 5️⃣: Outlier check
        elif step == 'outlier':
            # 👉 TODO: Detect numeric columns or use your own detection pipeline
            num_cols = []  # placeholder
            if request.method == 'POST':
                column = request.POST.get('column')
                if column:
                    # 👉 TODO: Replace with your outlier handling pipeline
                    # Example: df = data_pipeline.handle_outliers(df, column)
                    _save_df_to_session(request, df)
                    messages.success(request, f"Outliers handled for '{column}'.")
                    request.session['step'] = 'transform_choice'
                    return redirect('interactive_analysis')
            return render(request, 'interactive_analysis.html', {'step': step, 'columns': num_cols})

        # STEP 6️⃣: Perform Analysis
        elif step == 'analysis':
            if request.method == 'POST':
                analysis_type = request.POST.get('type')
                columns = request.POST.getlist('columns')

                # 👉 TODO: Replace these placeholders with your own plotting pipeline calls
                # Example:
                # if analysis_type == 'univariate':
                #     plot_html = data_pipeline.univariate_analysis(df, columns)
                # elif analysis_type == 'bivariate':
                #     plot_html = data_pipeline.bivariate_analysis(df, columns)
                # elif analysis_type == 'multivariate':
                #     plot_html = data_pipeline.multivariate_analysis(df, columns)

                plot_html = None  # placeholder
                return render(request, 'interactive_analysis.html', {
                    'step': 'done',
                    'plot_html': plot_html
                })

            return render(request, 'interactive_analysis.html', {'step': step, 'columns': df.columns})

        # STEP 7️⃣: Done — End of interactive process
        elif step == 'done':
            if request.method == 'POST' and 'restart' in request.POST:
                _clear_session(request)
                return redirect('analysis')
            return render(request, 'interactive_analysis.html', {'step': step})
        # ✅ FINAL FALLBACK RETURN (ensures HttpResponse always returned)
        return render(request, 'interactive_analysis.html', {
            'step': step,
            'message': "Unknown step or unhandled state. Restarting process."
        })

    except Exception as e:
        raise CustomException(e, sys) #type: ignore
