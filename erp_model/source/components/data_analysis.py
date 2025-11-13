from exception import CustomException
import io
import logging
import sys
import pandas as pd
from scipy.stats import chi2_contingency
import plotly.express as px

from django.shortcuts import redirect
from erp_app.models import UploadedFile
from django.contrib import messages

from source.components import data_transformation, plotly_calc

#obejcts Creation
logger = logging.getLogger(__name__)
datainfo = data_transformation.DataInfo()
onevariable = plotly_calc.OneVariable()
twovariable = plotly_calc.TwoVariable()
regression = plotly_calc.Regression()


class BasisDataAnalysis:
    def generate_summary(self, request, file_id=None):
        if not file_id:
            messages.error(request, "No file uploaded yet.")
            return redirect('home')

        try:
            file_record = UploadedFile.objects.get(id=file_id, user=request.user)
        except UploadedFile.DoesNotExist:
            messages.error(request, "File not found.")
            return redirect('home')

        file_stream = io.BytesIO(file_record.data)
        df = None

        try:
            if file_record.name.endswith('.csv'):
                df = pd.read_csv(file_stream, encoding='utf-8', on_bad_lines='skip')
            else:
                df = pd.read_excel(file_stream)
        except pd.errors.EmptyDataError:
            messages.error(request, "Uploaded file is empty or invalid CSV format.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error reading file: {e}")
            return redirect('home')

        if df is None or df.empty:
            messages.error(request, "The file contains no readable data.")
            return redirect('home')

        # Continue processing...
        summary_html = df.head(5).to_html(classes='table table-dark table-striped')
        column_data_info = datainfo.get_datatype(df)

        context = {
            'file_name': file_record.name,
            'rows': len(df),
            'numeric_columns': column_data_info['Numeric'],
            'categorical_columns': column_data_info['Categorical'],
            'datetime_columns': column_data_info['DateTime'],
            'summary': summary_html
        }

        return context

class DataQualityCheck:
    def check_missing(self,df, column):
        try:
            pass
        except Exception as e:
            raise CustomException(e, sys) #type: ignore
    def handle_missing(self,df, column):
        try:
            df[column].fillna(df[column].mean()) 

        
        except Exception as e:
            raise CustomException(e, sys) #type: ignore
        
    def duplicate_values(self,df : pd.DataFrame , request, column):
        try:
            logger.info(f'Duplicate Values checked by user {request.user}')
            duplicate_value = {}

            for col in df.columns:
                duplicate_value[col] = df[col].duplicated().sum()
            return duplicate_value
        except Exception as e:
            raise CustomException(e, sys) #type: ignore
            
    def outlier_boxplot(self,request, df: pd.DataFrame , column : str):
        try:
            logger.info(f'Outlier Boxplot Accessed by user : {request.user}')
            return onevariable.boxplot(df)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore
    
    def outlier_statstical(self, request,df: pd.DataFrame, column):
        try:
            logger.info(f'Outlier Statistical accessed by user {request.user}')
            data = df[column]
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)

            IQR = Q3 -Q1

            LOWERBOUND = Q1 - (1.5 * IQR)
            UPPERBOUND = Q3 - (1.5 * IQR)

            context = {
                'Q1' : Q1,
                'Q3' : Q3,
                'IQR' : IQR,
                'LOWERBOUND' : LOWERBOUND,
                'UPPERBOUND' : UPPERBOUND,
                'NumOfOutlier' : len(data[(data < LOWERBOUND | data > UPPERBOUND)]) 
            }

            return context

        except Exception as e:
            raise CustomException(e, sys) #type: ignore    
        
    def inconsistency(self,request, df : pd.DataFrame, column : str):
        try:
            logger.info(f'inconsistency func is accessed by {request.user}')
            return {
                'Unique Values' : df[column].unique(),
                'Numer of Unique' : len(df[column].unique())
            }
        
        except Exception as e:
            raise CustomException(e, sys) #type: ignore
        
class UniVariate:
    def mean(self, request, df: pd.DataFrame, column : str):
        try:
            logger.info(f'Mean function accessed by {request.user}')
            return df[column].mean()
        except Exception as e:
            raise CustomException(e, sys) #type: ignore 
        
    def mode(self, request, df: pd.DataFrame, column : str):
        try:
            logger.info(f'Mode function accessed by {request.user}')
            return df[column].mode()
        except Exception as e:
            raise CustomException(e, sys) #type: ignore 
        
    def median(self, request, df: pd.DataFrame, column : str):
        try:
            logger.info(f'Median function accessed by {request.user}')
            return df[column].median()
        except Exception as e:
            raise CustomException(e, sys) #type: ignore 
        
    def range(self, request, df: pd.DataFrame, column : str):
        try:
            logger.info(f'Range function accessed by {request.user}')
            return df[column].max() - df[column].min()
        except Exception as e:
            raise CustomException(e, sys) #type: ignore 
        
    def variance(self, request, df: pd.DataFrame, column : str):
        try:
            logger.info(f'Variance function accessed by {request.user}')
            return df[column].var()
        except Exception as e:
            raise CustomException(e, sys) #type: ignore 
        
    def standard_deviation(self, request, df: pd.DataFrame, column : str):
        try:
            logger.info(f'Std. Variance function accessed by {request.user}')
            return df[column].std()
        except Exception as e:
            raise CustomException(e, sys) #type: ignore 
        
    def Visualization(self, request, df : pd.DataFrame, column : str, visual : str):
        try:
            logger.info(f'Visualization function accessed by {request.user}')
            if visual == 'Histogram':
                return onevariable.histogram(df,column)

            elif visual == 'Boxplot':
                return onevariable.boxplot(df,column)
            
            elif visual == 'Violin':
                return onevariable.violin(df,column)
            
            elif visual == 'Bar':
                return onevariable.bar(df,column)
            
            elif visual == 'Pie':
                return onevariable.pie(df,column)    
            
            elif visual == 'Donut':
                return onevariable.donut(df,column)
            
            elif visual == 'Line_unsorted':
                return onevariable.line_unsorted(df,column)
            
            elif visual == 'Line_sorted':
                return onevariable.line_sorted(df,column)      

        except Exception as e:
            raise CustomException(e, sys) #type: ignore 
        
class BiVariateNumerical:
    def Visualization(self, df : pd.DataFrame,visual : str, column1, column2):
        try:
            if visual == 'Scatter':
                return twovariable.scatter(df, x = column1,y = column2)
            
            elif visual == 'Line':
                return twovariable.line(df, x = column1, y = column2)

            elif visual == 'Area':
                return twovariable.area(df, x = column1, y = column2)

        except Exception as e:
            raise CustomException(e, sys) #type: ignore
    
    def correlation_heatmap(self, df: pd.DataFrame, cols: list):
        try:
            return twovariable.correlation_heatmap(df, cols)

        except Exception as e:
            raise CustomException(e, sys) #type: ignore
    
    def regression_analysis(self, df : pd.DataFrame , cols):
        try:
            return regression.RegressionPlot(df, cols=cols)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

   
        
class BiVariateCategorical:
    """Handles bivariate analysis where both variables are categorical or a mix of categorical + numeric."""

    def chisquaretest(self, df: pd.DataFrame, cols: list):
        """Performs Chi-square test for independence between two categorical variables."""
        try:
            contingency_table = pd.crosstab(df[cols[0]], df[cols[1]])
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)

            return {
                "Chi-Square Statistic": chi2,
                "P-value": p_value,
                "Degrees of Freedom": dof,
                "Expected Frequencies": expected
            }

        except Exception as e:
            raise CustomException(e, sys)  # type: ignore


    def Visualization(self, df: pd.DataFrame, cols: list, dtypes: list, visual: str):
        """
        Creates visualizations depending on the datatype of columns.
        Supports:
        - (Categorical + Numeric)
        - (Categorical + Categorical)
        - (Numeric + Numeric)
        """
        try:
            # Case 1: Categorical + Numeric
            if (dtypes == ['int64', 'object'] or dtypes == ['float64', 'object'] or
                dtypes == ['object', 'int64'] or dtypes == ['object', 'float64']):
                
                if visual == 'Bar':
                    return twovariable.bar(df, x=cols[0], y=cols[1])
                elif visual == 'Column':
                    return twovariable.column(df, x=cols[0], y=cols[1])
                elif visual == 'Lollipop':
                    return twovariable.lollipop(df, x=cols[0], y=cols[1])
            
            # Case 2: Numeric + Numeric
            elif (dtypes == ['int64', 'int64'] or dtypes == ['float64', 'float64'] or
                  dtypes == ['int64', 'float64'] or dtypes == ['float64', 'int64']):
                
                if visual == 'Scatter':
                    return twovariable.scatter(df, x=cols[0], y=cols[1])
                elif visual == 'Line':
                    return twovariable.line(df, x=cols[0], y=cols[1])
                elif visual == 'Area':
                    return twovariable.area(df, x=cols[0], y=cols[1])
                elif visual == 'CorrelationHeatmap':
                    return twovariable.correlation_heatmap(df, cols)
            
            # Case 3: Categorical + Categorical
            elif dtypes == ['object', 'object']:
                if visual == 'Stacked Bar':
                    fig = px.bar(df, x=cols[0], color=cols[1], title=f"Stacked Bar of {cols[1]} by {cols[0]}")
                    fig.update_layout(barmode='stack')
                    return fig
                elif visual == 'Grouped Bar':
                    fig = px.bar(df, x=cols[0], color=cols[1], title=f"Grouped Bar of {cols[1]} by {cols[0]}")
                    fig.update_layout(barmode='group')
                    return fig
            
            else:
                raise ValueError("Unsupported combination of datatypes for visualization.")
        
        except Exception as e:
            raise CustomException(e, sys)  # type: ignore




class MultiVariate:
    """
    Handles multivariate analysis (3 or more columns).
    Uses MultiColumnPlots from plotly_calc for 3–5+ column visualizations.
    """

    def __init__(self):
        # lazy import to avoid circular dependency
        self.multiplot = plotly_calc.MultiColumnPlots()

    # -------------------------------
    # 3-column combinations
    # -------------------------------

    def scatter_color(self, request, df, x=None, y=None, cat=None):
        """
        3-column: Numeric + Numeric + Categorical → scatter plot colored by category
        """
        try:
            logger.info(f"3-Col scatter_color accessed by {request.user}")
            return self.multiplot.scatter_color(df, x, y, cat)
        except Exception as e:
            raise CustomException(e, sys)#type: ignore

    def bubble(self, request, df, x=None, y=None, size=None):
        """
        3-column: Numeric + Numeric + Numeric → bubble chart
        """
        try:
            logger.info(f"3-Col bubble accessed by {request.user}")
            return self.multiplot.bubble(df, x, y, size)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def box_by_cat(self, request, df, cat=None, num=None, color=None):
        """
        3-column: Box plot by category, colored by another categorical variable
        """
        try:
            logger.info(f"3-Col box_by_cat accessed by {request.user}")
            return self.multiplot.box_by_cat(df, cat, num, color)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def line_time_group(self, request, df, time_col=None, val=None, cat=None):
        """
        3-column: Datetime + Numeric + Categorical → time series by category
        """
        try:
            logger.info(f"3-Col line_time_group accessed by {request.user}")
            return self.multiplot.line_time_group(df, time_col, val, cat)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def area_time_group(self, request, df, time_col=None, val=None, cat=None):
        """
        3-column: Datetime + Numeric + Categorical → area chart by category
        """
        try:
            logger.info(f"3-Col area_time_group accessed by {request.user}")
            return self.multiplot.area_time_group(df, time_col, val, cat)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def grouped_bar(self, request, df, cat1=None, cat2=None, val=None):
        """
        3-column: Categorical + Categorical + Numeric → grouped bar
        """
        try:
            logger.info(f"3-Col grouped_bar accessed by {request.user}")
            return self.multiplot.grouped_bar(df, cat1, cat2, val)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def heatmap_pivot(self, request, df, cat1=None, cat2=None, val=None):
        """
        3-column: Categorical + Categorical + Numeric → heatmap (pivoted mean)
        """
        try:
            logger.info(f"3-Col heatmap_pivot accessed by {request.user}")
            return self.multiplot.heatmap_pivot(df, cat1, cat2, val)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    # -------------------------------
    # 4-column combinations
    # -------------------------------

    def box_color_facet(self, request, df, num1=None, num2=None, cat1=None, cat2=None):
        """
        4-column: Two numerics + two categoricals → faceted box plot
        """
        try:
            logger.info(f"4-Col box_color_facet accessed by {request.user}")
            return self.multiplot.box_color_facet(df, num1, num2, cat1, cat2)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def faceted_bar(self, request, df, num=None, cat1=None, cat2=None):
        """
        4-column: Numeric + two categoricals → faceted bar chart
        """
        try:
            logger.info(f"4-Col faceted_bar accessed by {request.user}")
            return self.multiplot.faceted_bar(df, num, cat1, cat2)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def scatter_size_color(self, request, df, x=None, y=None, size=None, cat=None):
        """
        4-column: Numeric + Numeric + Numeric + Categorical → scatter with color and size encoding
        """
        try:
            logger.info(f"4-Col scatter_size_color accessed by {request.user}")
            return self.multiplot.scatter_size_color(df, x, y, size, cat)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def parallel_coordinates(self, request, df, col1=None, col2=None, col3=None, col4=None):
        """
        4-column: Parallel coordinates plot
        """
        try:
            logger.info(f"4-Col parallel_coordinates accessed by {request.user}")
            return self.multiplot.parallel_coordinates(df, col1, col2, col3, col4)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def scatter_geo(self, request, df, lat=None, lon=None, cat=None, val=None):
        """
        4-column: Geo scatter → latitude, longitude, color, size
        """
        try:
            logger.info(f"4-Col scatter_geo accessed by {request.user}")
            return self.multiplot.scatter_geo(df, lat, lon, cat, val)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    # -------------------------------
    # Many-column combinations (5+)
    # -------------------------------

    def parallel_coords(self, request, df):
        """
        5+ columns: Parallel coordinate matrix
        """
        try:
            logger.info(f"Many-Col parallel_coords accessed by {request.user}")
            return self.multiplot.parallel_coords(df)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def scatter_matrix(self, request, df):
        """
        5+ columns: Scatter matrix for pairwise relationships
        """
        try:
            logger.info(f"Many-Col scatter_matrix accessed by {request.user}")
            return self.multiplot.scatter_matrix(df)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def treemap_sunburst(self, request, df):
        """
        5+ columns: Treemap / sunburst for categorical hierarchy + numeric value
        """
        try:
            logger.info(f"Many-Col treemap_sunburst accessed by {request.user}")
            return self.multiplot.treemap_sunburst(df)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore

    def correlation_heatmap(self, request, df):
        """
        5+ columns: Correlation heatmap of numeric variables
        """
        try:
            logger.info(f"Many-Col correlation_heatmap accessed by {request.user}")
            return self.multiplot.correlation_heatmap(df)
        except Exception as e:
            raise CustomException(e, sys) #type: ignore
