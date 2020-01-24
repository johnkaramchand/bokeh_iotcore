# Copyright Google Inc. 2017
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from modules.base import BaseModule
from utils import run_query
from states import NAMES_TO_CODES
from bokeh.layouts import column, row

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import warnings
warnings.filterwarnings('ignore')
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.palettes import Spectral11, colorblind, Inferno, BuGn, brewer
from bokeh.models import HoverTool, value, LabelSet, Legend, ColumnDataSource,LinearColorMapper,BasicTicker, PrintfTickFormatter, ColorBar, Paragraph
import datetime


QUERY = """
    SELECT 
      *
    FROM 
      [hydroponics-265005:my_dataset.gas_values] 
    LIMIT 5
"""

YEAR = 2019
TITLE = "Temperatures (C) in %s:" % YEAR


class Module(BaseModule):

    def __init__(self):
        super().__init__()
        self.source = None
        self.plot = None
        self.title = None

    def fetch_data(self, state):
        dataframe = run_query(
            QUERY ,
            cache_key=('air-%s' % NAMES_TO_CODES[state]))
        dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'])
        dataframe['day'] = dataframe.timestamp.apply(lambda x: x.day)
        dataframe['minutes'] = dataframe.timestamp.apply(lambda x: x.minute)
        dataframe['hour'] = dataframe.timestamp.apply(lambda x: x.hour)
        return dataframe

    def make_plot(self, dataframe):
        temp_df = dataframe.groupby(['hour']).mean().reset_index()
        TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom,tap"
        self.plot = figure(plot_height=350,
            title="Average Temperature by Hour",
            tools=TOOLS,
            toolbar_location='above')
        self.plot.vbar(x=temp_df.hour, top=temp_df.tempa, width=0.9)
        self.plot.y_range.start = 0
        self.plot.x_range.range_padding = 0.1
        self.plot.xgrid.grid_line_color = None
        self.plot.axis.minor_tick_line_color = None
        self.plot.outline_line_color = None
        self.plot.xaxis.axis_label = 'Hour'
        self.plot.yaxis.axis_label = 'Average Temp'
        self.plot.select_one(HoverTool).tooltips = [
            ('hour', '@x'),
            ('tempa', '@top')]           
        self.title = Paragraph(text=TITLE)
        return column(self.title, self.plot)

    def update_plot(self, dataframe):
        self.source.data.update(dataframe)

    def busy(self):
        self.title.text = 'Updating...'
        self.plot.background_fill_color = "#efefef"

    def unbusy(self):
        self.title.text = TITLE
        self.plot.background_fill_color = "white"
