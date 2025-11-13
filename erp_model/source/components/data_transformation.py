from re import L
import pandas as pd
from exception import CustomException
import sys

class ColumnTranformer:
    def __init__(self):
        pass
    
    def auto_correct_datatypes(self, df : pd.DataFrame , threshold = 0.05):

        """
           It automatically handles Hetrogeneous data, infers and converts data types.
           
           Parameters:
           
           df : (pd.DataFrame) : Input DataFrame.
           threshold : (float) : Maximum allowed fraction of data that can become 'NaN/NaT' 
                       during conversion before we reject the conversion. 
                       0.05 means we allow 5% of valid data to be lost to typos        
        """
        
        try:
            original_df = df.copy()
      
            for col in df.columns:
                if df[col].dtype == 'object':
                    #---- 01. Convert to Date Columns Data types ----
                    # errors='coerce' will turn incompatible values (like 'Unknown') into NaT
    
                    date_corrected = pd.to_datetime(df[col], errors = 'coerce')
    
                    #calculate NA values in the original dataframe column
                    original_missing_values = df[col].isna().sum()
    
                    #calculate NA values in the converted dataframe column
                    convereted_missing_values = df[col].isna().sum()
    
                    #check number of values that are miss convereted
                    failed_conversion = original_missing_values - convereted_missing_values
    
                    #find total number of valid values in dataframe
                    total_valid_original = len(df) - original_missing_values
    
                    #check the threshold:
                    if total_valid_original > 0 and (failed_conversion/total_valid_original) < threshold:
                        df[col] = date_corrected
                        print(f"✅ Column '{col}' converted to DATETIME.")
                        continue
    
                    #---- 02. Convert to Numerical Data Column values ----
                    # errors='coerce' will turn incompatible values (like 'Unknown') into NaN
                    numeric_corrected = pd.to_numeric(df[col], errors = 'coerce')
                    
                    #original NA values 
                    original_missing_values = original_df[col].isna().sum()
    
                    #convereted missing values
                    convereted_missing_values = numeric_corrected.isna().sum()
    
                    #failed to convert
                    failed_conversion = original_missing_values - convereted_missing_values
    
                    #find the total number of the valid points
                    total_valid_original = len(df) - original_missing_values 
    
                    if total_valid_original > 0 and ( failed_conversion / total_valid_original) < threshold:
                        df[col] = numeric_corrected
                        print(f"✅ Column '{col}' converted to Numeric.")
                    
            return [df, original_df]
        except Exception as e:
            raise CustomException(e, sys) #type: ignore


    def handle_missing(self, df : pd.DataFrame, column, mode = None):
        """
        Handle Missing Values Function handles Missing Values of Column with Different Modes such as Mean, Mode, Median

        Parameters : 
        
        df: DataFrame,

        Column: Column of DataFrame which NA values to be filled.

        mode: Mode of value tp be filled option mean, mode and median.             
        
        """
        try:
            if mode == 'mean' or mode == 'Mean':
                df[column].fillna(df[column].mean())
            
            elif mode == 'Mode' or mode == 'mode':
                df[column].fillna(df[column].mode())
            
            else:
                df[column].fillna(df[column].median())

        except Exception as e:
            raise CustomException(e, sys) #type: ignore



class DataInfo:
    def get_datatype(self, data):
        
        try:
            context = { 
                "Numeric" : [],       
                "Categorical" : [],
                "DateTime" : []
            }
            for col in data.columns:
                if data[col].dtype in ('int64', 'float64'):
                    context['Numeric'].append(col)
                elif data[col].dtype in ('object', 'str'):
                    context['Categorical'].append(col)
                else:
                    context['DateTime'].append(col)
            return context
        
        except Exception as e:
            raise CustomException(e, sys) #type: ignore
        
