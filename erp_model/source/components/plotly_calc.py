
from typing import List
import plotly.express as px
import pandas as pd
import numpy as np
import functools


def safe_plot(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f"❌ Column error: '{e.args[0]}' not found in DataFrame.")
        except ValueError as e:
            print(f"⚠️ Value Error: {e}")
        except TypeError as e:
            print(f"⚠️ Type Error: {e}")
        except Exception as e:
            print(f"🚨 Unexpected Error: {e}")
    return wrapper


class fundamental:

    #---- Select Theme ----#
    @safe_plot
    def select_theme(self, fig):
        themes = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
        print("\nSelect Theme for Plot:")
        for i, t in enumerate(themes, start=1):
            print(f"{i}: {t}")
        try:
            theme_index = int(input("\nEnter theme number: "))
            selected_theme = themes[theme_index - 1]
        except (ValueError, IndexError):
            print("⚠️ Invalid choice! Defaulting to 'default'")
            selected_theme = 'default'
        fig.update_layout(template=selected_theme)
        return selected_theme

    #---- Select One Variable ----#
    @safe_plot
    def select_onevariable(self, df: pd.DataFrame):
        print('Data columns:\n')
        for i, col in enumerate(df.columns, start=1):
            print(f"{i}: {col}")
        x = int(input('Select column number: '))
        return df.columns[x - 1]

    #---- Select Two Variable ----#
    @safe_plot
    def select_twovariable(self, df : pd.DataFrame):
        print('Data columns:\n')
        for i, col in enumerate(df.columns, start=1):
            print(f"{i}: {col}")
        x = int(input('Select column number for X: '))
        y = int(input('Select column number for Y: '))
        return [df.columns[x - 1], df.columns[y-1]]

    #---- Select N Variables ----#
    @safe_plot
    def select_n_variables(self, df: pd.DataFrame, n: int) -> List[str]:
        print('Data columns:\n')
        for i, col in enumerate(df.columns, start=1):
            print(f"{i}: {col}")
        picks = []
        for j in range(1, n+1):
            idx = int(input(f'Select column number {j}: '))
            picks.append(df.columns[idx-1])
        return picks

   

#-----------------------------------------------------------
#---- One Variable Numeric Plots ---------------------------
#-----------------------------------------------------------
class OneVariableNumeric:
    """Class is used to Plot chart on Single Numeric column"""

    def __init__(self):
        self.fundamental = fundamental()

    @safe_plot
    def histogram(self, df: pd.DataFrame, x = None):
        if not x:
            x = self.fundamental.select_onevariable(df)
        fig = px.histogram(df, x=x, nbins=20, title=f"Histogram of {x}")
        self.fundamental.select_theme(fig)
        return fig 

    @safe_plot
    def boxplot(self, df: pd.DataFrame, x = None):
        if not x:
            x = self.fundamental.select_onevariable(df)
        fig = px.box(df, y=x, title=f"Box Plot of {x}")
        self.fundamental.select_theme(fig)
        return fig 

    @safe_plot
    def violin(self, df: pd.DataFrame, x =  None):
        if not x:
            x = self.fundamental.select_onevariable(df)
        fig = px.violin(df, y=x, title=f"Violin Plot of {x}")
        self.fundamental.select_theme(fig)
        return fig 


#-----------------------------------------------------------
#---- One Variable Categorical Plots -----------------------
#-----------------------------------------------------------
class OneVariableCategorical:
    """Class is used to Plot chart on Single Categorical column"""

    def __init__(self):
        self.fundamental = fundamental()

    @safe_plot
    def bar(self, df: pd.DataFrame, x = None):
        if not x:
            x = self.fundamental.select_onevariable(df)
        counts = df[x].value_counts().reset_index()
        counts.columns = [x, "count"]
        fig = px.bar(counts, x=x, y="count", title=f"Bar Chart of {x}")
        self.fundamental.select_theme(fig)
        return fig 

    @safe_plot
    def pie(self, df: pd.DataFrame, x = None):
        if not x:
            x = self.fundamental.select_onevariable(df)
        counts = df[x].value_counts().reset_index()
        counts.columns = [x, "count"]
        fig = px.pie(counts, names=x, values="count", title=f"Pie Chart of {x}")
        self.fundamental.select_theme(fig)
        return fig 

    @safe_plot
    def donut(self, df: pd.DataFrame, x = None):
        if not x:
            x = self.fundamental.select_onevariable(df)
        counts = df[x].value_counts().reset_index()
        counts.columns = [x, "count"]
        fig = px.pie(counts, names=x, values="count", hole=0.5, title=f"Donut Chart of {x}")
        self.fundamental.select_theme(fig)
        return fig 


#-----------------------------------------------------------
#---- One Variable DateTime Plots --------------------------
#-----------------------------------------------------------
class OneVariableDateTime:
    """Class is used to Plot chart on Single DateTime column"""

    def __init__(self):
        self.fundamental = fundamental()

    @safe_plot
    def line_unsorted(self, df: pd.DataFrame, x = None):
        if not x:
            x = self.fundamental.select_onevariable(df)
        counts = df[x].value_counts().sort_index().reset_index()
        counts.columns = [x, "count"]
        fig = px.line(counts, x=x, y="count", title=f"Line Chart of {x} (Unsorted)")
        self.fundamental.select_theme(fig)
        return fig 

    @safe_plot
    def line_sorted(self, df: pd.DataFrame, x = None):
        if not x:
            x = self.fundamental.select_onevariable(df)
        df = df.sort_values(by=x)
        counts = df[x].value_counts().sort_index().reset_index()
        counts.columns = [x, "count"]
        fig = px.line(counts, x=x, y="count", title=f"Line Chart of {x} (Sorted)")
        self.fundamental.select_theme(fig)
        return fig 


#-----------------------------------------------------------
#---- Unified OneVariable Interface ------------------------
#-----------------------------------------------------------
class OneVariable(
    OneVariableNumeric,
    OneVariableCategorical,
    OneVariableDateTime):
    """Unified class to handle all types of one-variable plots"""

    def __init__(self):
        OneVariableNumeric.__init__(self)
        OneVariableCategorical.__init__(self)
        OneVariableDateTime.__init__(self)




#-----------------------------------------------------------
#------ Two Variable: X - Categorical, Y - Numeric ----------
#-----------------------------------------------------------
class TwoVariableXCatYNum:
    """Class for plotting two-variable charts where X is categorical and Y is numeric."""

    def __init__(self):
        self.fundamental = fundamental()

    @safe_plot
    def bar(self, df, x=None, y=None):
        if not x and not y:
            x, y = self.fundamental.select_twovariable(df)
        fig = px.bar(df, x=x, y=y, title=f"Bar Chart of {y} by {x}")
        self.fundamental.select_theme(fig)
        return fig 

    @safe_plot
    def column(self, df, x=None, y=None):
        if not x and not y:
            x, y = self.fundamental.select_twovariable(df)
        fig = px.bar(df, x=y, y=x, orientation='h', title=f"Column Chart of {y} by {x}")
        self.fundamental.select_theme(fig)
        return fig 

    @safe_plot
    def lollipop(self, df, x=None, y=None):
        if not x and not y:
            x, y = self.fundamental.select_twovariable(df)
        df_sorted = df.sort_values(by=y, ascending=True)
        fig = px.scatter(df_sorted, x=x, y=y, title=f"Lollipop Chart of {y} by {x}")
        fig.add_traces(px.line(df_sorted, x=x, y=y).data)
        self.fundamental.select_theme(fig)
        return fig 


#-----------------------------------------------------------
#------ Two Variable: Both Numeric --------------------------
#-----------------------------------------------------------
class TwoVariableNumeric:
    """Class for plotting charts where both X and Y are numeric."""

    def __init__(self):
        self.fundamental = fundamental()
    @safe_plot
    def correlation_heatmap(self, df: pd.DataFrame, cols : list):
        nums = df[cols]
        corr = nums.corr()
        fig = px.imshow(corr, text_auto=True, title='Correlation matrix')
        self.fundamental.select_theme(fig)
        return fig 

    @safe_plot
    def scatter(self, df, x=None, y=None):
        if not x and not y:
            x, y = self.fundamental.select_twovariable(df)
        fig = px.scatter(df, x=x, y=y, title=f"Scatter Plot of {y} vs {x}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def line(self, df, x=None, y=None):
        if not x and not y:
            x, y = self.fundamental.select_twovariable(df)
        fig = px.line(df, x=x, y=y, title=f"Line Chart of {y} vs {x}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def area(self, df, x=None, y=None):
        if not x and not y:
            x, y = self.fundamental.select_twovariable(df)
        fig = px.area(df, x=x, y=y, title=f"Area Chart of {y} vs {x}")
        self.fundamental.select_theme(fig)
        return fig


#-----------------------------------------------------------
#------ Two Variable: X - Date, Y - Numeric ----------------
#-----------------------------------------------------------
class TwoVariableXDateYNum:
    """Class for plotting charts where X is datetime and Y is numeric."""

    def __init__(self):
        self.fundamental = fundamental()

    @safe_plot
    def line(self, df, x=None, y=None):
        if not x and not y:
            x, y = self.fundamental.select_twovariable(df)
        fig = px.line(df, x=x, y=y, title=f"Line Chart of {y} over Time ({x})")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def area(self, df, x=None, y=None):
        if not x and not y:
            x, y = self.fundamental.select_twovariable(df)
        fig = px.area(df, x=x, y=y, title=f"Area Chart of {y} over Time ({x})")
        self.fundamental.select_theme(fig)
        return fig


#-----------------------------------------------------------
#------ Unified TwoVariable Interface -----------------------
#-----------------------------------------------------------
class TwoVariable(
    TwoVariableXCatYNum,
    TwoVariableNumeric,
    TwoVariableXDateYNum
):
    """Unified class that supports all two-variable chart types."""

    def __init__(self):
        TwoVariableXCatYNum.__init__(self)
        TwoVariableNumeric.__init__(self)
        TwoVariableXDateYNum.__init__(self)


# -------------------------
# Multi-column plot classes
# -------------------------

class ThreeColumns:
    """Handlers for all 3-column combinations described by the user."""
    def __init__(self):
        self.fundamental = fundamental()

    # 3 columns: Numeric + Numeric + Categorical
    @safe_plot
    def scatter_color(self, df, x=None, y=None, cat=None):
        if not x and not y and not cat:
            x, y, cat = self.fundamental.select_n_variables(df, 3)
        fig = px.scatter(df, x=x, y=y, color=cat, title=f"Scatter of {x} vs {y} colored by {cat}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def bubble(self, df, x=None, y=None, size=None):
        if not x and not y and not size:
            x, y, size = self.fundamental.select_n_variables(df, 3)
        fig = px.scatter(df, x=x, y=y, size=size, title=f"Bubble chart of {x} vs {y} sized by {size}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def box_by_cat(self, df, cat=None, num=None, color=None):
        if not cat and not num and not color:
            cat, num, color = self.fundamental.select_n_variables(df, 3)
        fig = px.box(df, x=cat, y=num, color=color, title=f"Box plot of {num} by {cat} (colored by {color})")
        self.fundamental.select_theme(fig)
        return fig

    # 3 columns: Numeric + Numeric + Numeric
    @safe_plot
    def bubble_3num(self, df, x=None, y=None, size=None):
        if not x and not y and not size:
            x, y, size = self.fundamental.select_n_variables(df, 3)
        fig = px.scatter(df, x=x, y=y, size=size, title=f"Bubble chart: {x} vs {y}, size={size}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def scatter_3d(self, df, x=None, y=None, z=None):
        if not x and not y and not z:
            x, y, z = self.fundamental.select_n_variables(df, 3)
        fig = px.scatter_3d(df, x=x, y=y, z=z, title=f"3D Scatter of {x}, {y}, {z}")
        self.fundamental.select_theme(fig)
        return fig

    # 3 columns: Categorical + Categorical + Numeric
    @safe_plot
    def grouped_bar(self, df, cat1=None, cat2=None, val=None):
        if not cat1 and not cat2 and not val:
            cat1, cat2, val = self.fundamental.select_n_variables(df, 3)
        fig = px.bar(df, x=cat1, y=val, color=cat2, barmode='group',
                     title=f"Grouped bar of {val} by {cat1} and {cat2}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def heatmap_pivot(self, df, cat1=None, cat2=None, val=None):
        if not cat1 and not cat2 and not val:
            cat1, cat2, val = self.fundamental.select_n_variables(df, 3)
        pivot = df.pivot_table(values=val, index=cat1, columns=cat2, aggfunc='mean')
        fig = px.imshow(pivot, labels=dict(x=cat2, y=cat1, color=val),
                        title=f"Heatmap (mean {val}) by {cat1} and {cat2}")
        self.fundamental.select_theme(fig)
        return fig

    # 3 columns: Datetime + Numeric + Categorical
    @safe_plot
    def line_time_group(self, df, time_col=None, val=None, cat=None):
        if not time_col and not val and not cat:
            time_col, val, cat = self.fundamental.select_n_variables(df, 3)
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        fig = px.line(df, x=time_col, y=val, color=cat, title=f"Time series of {val} by {cat}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def area_time_group(self, df, time_col=None, val=None, cat=None):
        if not time_col and not val and not cat:
            time_col, val, cat = self.fundamental.select_n_variables(df, 3)
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        fig = px.area(df, x=time_col, y=val, color=cat, title=f"Area chart of {val} by {cat} over time")
        self.fundamental.select_theme(fig)
        return fig


class FourColumns:
    """Handlers for 4-column combinations."""
    def __init__(self):
        self.fundamental = fundamental()

    @safe_plot
    def box_color_facet(self, df, num1=None, num2=None, cat1=None, cat2=None):
        if not num1 and not num2 and not cat1 and not cat2:
            num1, num2, cat1, cat2 = self.fundamental.select_n_variables(df, 4)
        fig = px.box(df, x=cat1, y=num1, color=cat2, facet_col=cat2,
                     title=f"Box plot of {num1} by {cat1} colored/faceted by {cat2}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def faceted_bar(self, df, num=None, cat1=None, cat2=None):
        if not num and not cat1 and not cat2:
            num, _, cat1, cat2 = self.fundamental.select_n_variables(df, 4)
        fig = px.bar(df, x=cat1, y=num, color=cat2, facet_col=cat2,
                     title=f"Faceted bar of {num} by {cat1} and {cat2}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def scatter_size_color(self, df, x=None, y=None, size=None, cat=None):
        if not x and not y and not size and not cat:
            x, y, size, cat = self.fundamental.select_n_variables(df, 4)
        fig = px.scatter(df, x=x, y=y, size=size, color=cat,
                         title=f"Scatter of {x} vs {y}, size={size}, color={cat}")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def parallel_coordinates(self, df, col1=None, col2=None, col3=None, col4=None):
        if not col1 and not col2 and not col3 and not col4:
            nums = self.fundamental.select_n_variables(df, 4)
        else:
            nums = [col for col in [col1, col2, col3, col4] if col]
        try:
            color_col = nums[-1]
            dims = nums[:-1]
        except Exception:
            color_col = None
            dims = nums
        fig = px.parallel_coordinates(df, dimensions=dims, color=color_col) if color_col else px.parallel_coordinates(df, dimensions=dims)
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def scatter_geo(self, df, lat=None, lon=None, cat=None, val=None):
        if not lat and not lon and not cat and not val:
            lat, lon, cat, val = self.fundamental.select_n_variables(df, 4)
        fig = px.scatter_geo(df, lat=lat, lon=lon, color=cat, size=val,
                             title=f"Geo scatter of {val} by {cat}")
        self.fundamental.select_theme(fig)
        return fig


class ManyColumns:
    """Handlers for 5+ columns and many-numeric matrix cases."""
    def __init__(self):
        self.fundamental = fundamental()

    @safe_plot
    def parallel_coords(self, df):
        print('Select numeric columns for parallel coordinates (enter numbers one by one, blank to finish):')
        for i, col in enumerate(df.columns, start=1):
            print(f"{i}: {col}")
        picks = []
        while True:
            s = input('Column number (blank to finish): ')
            if s.strip() == '':
                break
            picks.append(df.columns[int(s)-1])
        if len(picks) < 2:
            print('Need at least 2 columns for parallel coordinates')
            return
        fig = px.parallel_coordinates(df[picks])
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def scatter_matrix(self, df):
        print('Select columns for scatter matrix (enter numbers one by one, blank to finish):')
        for i, col in enumerate(df.columns, start=1):
            print(f"{i}: {col}")
        picks = []
        while True:
            s = input('Column number (blank to finish): ')
            if s.strip() == '':
                break
            picks.append(df.columns[int(s)-1])
        if len(picks) < 2:
            print('Need at least 2 columns for scatter matrix')
            return
        fig = px.scatter_matrix(df[picks], title='Scatter matrix')
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def treemap_sunburst(self, df):
        print('Select two categorical columns and one numeric (enter 3 numbers):')
        c1 = int(input('cat1 column number: '))
        c2 = int(input('cat2 column number: '))
        v = int(input('value column number: '))
        cat1 = df.columns[c1-1]
        cat2 = df.columns[c2-1]
        val = df.columns[v-1]
        fig = px.treemap(df, path=[cat1, cat2], values=val, title=f"Treemap by {cat1} and {cat2} (size={val})")
        self.fundamental.select_theme(fig)
        return fig

    @safe_plot
    def correlation_heatmap(self, df):
        nums = df.select_dtypes(include=[np.number])
        if nums.shape[1] < 2:
            print('Need at least two numeric columns for correlation matrix')
            return
        corr = nums.corr()
        fig = px.imshow(corr, text_auto=True, title='Correlation matrix')
        self.fundamental.select_theme(fig)
        return fig


# ---------------------------
# Bundle for user convenience
# ---------------------------
class MultiColumnPlots(ThreeColumns, FourColumns, ManyColumns):
    def __init__(self):
        ThreeColumns.__init__(self)
        FourColumns.__init__(self)
        ManyColumns.__init__(self)

class Regression(fundamental):
    def __init__(self):
        fundamental.__init__(self)

    def RegressionPlot(self, df : pd.DataFrame, cols): 
        fig = px.scatter(df, x=cols[0], y=cols[1], trendline='ols')
        fundamental.select_theme(self, fig)
        return fig

if __name__ == '__main__':
    print('Module loaded. Use MultiColumnPlots() to access multi-column plotting helpers.')

