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


from bokeh.models import ColumnDataSource, HoverTool, Paragraph
from bokeh.plotting import figure
from bokeh.palettes import all_palettes
from bokeh.layouts import column

from modules.base import BaseModule
from utils import run_query
from states import NAMES_TO_CODES
from bokeh.models.widgets import DataTable, TableColumn, NumberFormatter, Paragraph


QUERY = """
    SELECT 
      temp as temp,
      slno as slno
    FROM 
      [hydroponics-265005:my_dataset.temperature] 
    LIMIT 5
"""

TITLE = 'Evolution of air pollutant levels:'


class Module(BaseModule):

    def __init__(self):
        super().__init__()
        self.source = None
        self.plot = None
        self.title = None

    def fetch_data(self, state):
        return run_query(
            QUERY ,
            cache_key=('air-%s' % NAMES_TO_CODES[state]))

# [START make_plot]
    def make_plot(self, dataframe):
        self.source = ColumnDataSource(data=dataframe)
        print("kaka - ",dataframe) 
        self.title = Paragraph(text=TITLE)
        self.data_table = DataTable(source=self.source, width=390, height=275, columns=[
            TableColumn(field="temp", title="Temp", width=100),
            TableColumn(field="slno", title="SLNO", width=100)
        ])
        return column(self.title, self.data_table)# [END make_plot]

    def update_plot(self, dataframe):
        self.source.data.update(dataframe)

    def busy(self):
        self.title.text = 'Updating...'
        self.plot.background_fill_color = "#efefef"

    def unbusy(self):
        self.title.text = TITLE
        self.plot.background_fill_color = "white"
