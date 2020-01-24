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


from bokeh.models import ColumnDataSource, HoverTool, Paragraph, DataRange1d, Plot, LinearAxis, Grid
from bokeh.plotting import figure
from bokeh.palettes import all_palettes
from bokeh.layouts import column
from bokeh.models.glyphs import Line

from modules.base import BaseModule
from utils import run_query
from states import NAMES_TO_CODES
from bokeh.models.widgets import DataTable, TableColumn, NumberFormatter, Paragraph


QUERY = """
    SELECT 
      timestamp as timestamp,
      tempa as temperature
    FROM 
      [hydroponics-265005:my_dataset.gas_values] 
    LIMIT 5
"""

TITLE = 'Evolution of Air Temperature levels:'



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
        dataframe['date_readable'] = dataframe['timestamp'].apply(lambda x: x.strftime("%H-%M-%S"))
        return dataframe


# [START make_plot]
    def make_plot(self, dataframe):
        self.source = ColumnDataSource(data=dataframe)
        self.plot = Plot(title=None, plot_width=300, plot_height=300,min_border=0, toolbar_location=None)
        glyph = Line(x="timestamp", y="temperature", line_color="#f46d43", line_width=6, line_alpha=0.6)
        self.plot.add_glyph(self.source, glyph)
        xaxis = LinearAxis()
        self.plot.add_layout(xaxis, 'below')
        yaxis = LinearAxis()
        self.plot.add_layout(yaxis, 'left')
        self.title = Paragraph(text=TITLE)
        self.plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
        self.plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker)) 
        return column(self.title, self.plot)

    def update_plot(self, dataframe):
        self.source.data.update(dataframe)

    def busy(self):
        self.title.text = 'Updating...'
        self.plot.background_fill_color = "#efefef"

    def unbusy(self):
        self.title.text = TITLE
        self.plot.background_fill_color = "white"
