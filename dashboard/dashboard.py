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


import logging
import concurrent
import time

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Select, Paragraph

import modules.air
import modules.temperature
import modules.population
import modules.precipitation
from states import NAMES
from bokeh.models.widgets import Button
from google.oauth2 import service_account

from google.cloud import iot_v1

import logging
import os
import sys
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account-key.json"

#print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

credentials = service_account.Credentials.from_service_account_file('service-account-key.json',)

client = iot_v1.DeviceManagerClient(credentials=credentials)

name = client.device_path('hydroponics-265005', 'asia-east1', 'my-registry', 'my-device')


# Hide some noisy warnings
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

modules = [modules.air.Module(),modules.temperature.Module(),modules.population.Module(),modules.precipitation.Module()]

state = 'California'

# [START fetch_data]
def fetch_data(state):
    """
    Fetch data from BigQuery for the given US state by running
    the queries for all dashboard modules in parallel.
    """
    t0 = time.time()
    # Collect fetch methods for all dashboard modules
    fetch_methods = {module.id: getattr(module, 'fetch_data') for module in modules}
    # Create a thread pool: one separate thread for each dashboard module
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(fetch_methods)) as executor:
        # Prepare the thread tasks
        tasks = {}
        for key, fetch_method in fetch_methods.items():
            task = executor.submit(fetch_method, state)
            tasks[task] = key
        # Run the tasks and collect results as they arrive
        results = {}
        for task in concurrent.futures.as_completed(tasks):
            key = tasks[task]
            results[key] = task.result()
    # Return results once all tasks have been completed
    t1 = time.time()
    timer.text = '(Execution time: %s seconds)' % round(t1 - t0, 4)
    return results
# [END fetch_data]


def update(attrname, old, new):
    timer.text = '(Executing %s queries...)' % len(modules)
    for module in modules:
        getattr(module, 'busy')()

    results = fetch_data(new)

    for module in modules:
        getattr(module, 'update_plot')(results[module.id])

    for module in modules:
        getattr(module, 'unbusy')()



def buttonClicked():
    response = client.modify_cloud_to_device_config(name, b"Hello Dina !!")
    print(response)
    print("Button Clicked !")




button = Button(label="Douse nutrients", button_type="success")
button.on_click(buttonClicked)
timer = Paragraph()

results = fetch_data(state)

blocks = {}
for module in modules:
    block = getattr(module, 'make_plot')(results[module.id])
    blocks[module.id] = block

curdoc().add_root(
    column(
        row(timer, button),
        row(
            column(blocks['modules.air'],blocks['modules.temperature']),
        ),
        row(column(blocks['modules.population'],blocks['modules.precipitation']))
    )
)
curdoc().title = "Groot Dashboard"