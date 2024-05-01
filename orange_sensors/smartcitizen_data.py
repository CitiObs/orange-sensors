from orangewidget.widget import OWBaseWidget, Output, Input
from AnyQt.QtWidgets import QCheckBox
from orangewidget.settings import Setting
from Orange.widgets.settings import DomainContextHandler, ContextSetting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame

from smartcitizen_connector import SCDevice
from smartcitizen_connector.tools import freq_2_rollup_lut, localise_date
import nest_asyncio
import asyncio

loop = asyncio.new_event_loop()
nest_asyncio.apply(loop)
asyncio.set_event_loop(loop)

# Fixed stations
class SmartcitizenSensorDataWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "Smart Citizen Data"

    # Short widget description
    description = "Get data from environmental devices from the Smart Citizen API"

    # An icon resource file path for this widget
    icon = "icons/smartcitizen_data.png"

    # Priority in the section
    priority = 2

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = True

    # Defining settings
    device = Setting("", schema_only=True)
    rollup_number = Setting("10", schema_only=True)
    rollup_text = Setting("Min", schema_only=True)
    resample = Setting(True, schema_only=True)
    min_date_text = Setting("", schema_only=True)
    max_date_text = Setting("", schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Inputs:
        devices = Input("Devices", Orange.data.Table, auto_summary = False)

    class Outputs:
        readings = Output("readings", Orange.data.Table, auto_summary = False)

    metadata = None
    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        # Info banners
        self.infoa = gui.widgetLabel(info, 'No data fetched yet.')

        gui.separator(self.controlArea)

        self.rollupBox = gui.widgetBox(self.controlArea,  "Get data at a specific frequency")

        self.rollup_number_line = gui.lineEdit(
            self.rollupBox,
            self,
            "rollup_number",
            label="Rollup:",
            orientation=1,
            controlWidth=140,
            callback=self.rollup_check
        )

        self.rollup_text_line = gui.comboBox(
            self.rollupBox,
            self,
            "rollup_text",
            label="Rollup units:",
            items=tuple([item[0] for item in freq_2_rollup_lut]),
            sendSelectedValue=True,
            emptyString=False,
            editable=False,
            contentsLength=None,
            searchable=True,
            orientation=1
        )

        self.dateBox = gui.widgetBox(self.controlArea,
            "Filter by date (YYYY-MM-DD)"
        )

        self.date_init_line = gui.lineEdit(
            self.dateBox,
            self,
            "min_date_text",
            label="Initial Date:",
            orientation=1,
            controlWidth=140,
            callback=self.date_check
        )

        self.date_end_line = gui.lineEdit(
            self.dateBox,
            self,
            "max_date_text",
            label="End Date:",
            orientation=1,
            controlWidth=140,
            callback=self.date_check
        )

        self.resampleBox = gui.checkBox(
            self.controlArea,
            self,
            "resample",
            label="Resample data"
            )

        gui.separator(self.controlArea)

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Get data", callback=self.commit)

        self.device = None

    @Inputs.devices
    def set_data(self, dataset):

        if dataset is not None:

            self.metadata = table_to_frame(dataset, include_metas = True)

            if (self.metadata.shape[0] > 1):

                self.infoa.setText("Select one device first!")
                return
            else:

                if 'device_id' in self.metadata.columns:
                    col = 'device_id'
                elif 'id' in self.metadata.columns:
                    col = 'id'
                else:
                    self.infoa.setText('Error with input data')
                    return

                self.device = self.metadata[col].values[0]

                name = self.metadata['name'].values[0]
                city = self.metadata['city'].values[0]
                country = self.metadata['country_code'].values[0]
                owner = self.metadata['owner_username'].values[0]

                self.infoa.setText(f"Device: {self.device}"+ \
                    f"\nName: {name}" + \
                    f"\nCity: {city} ({country})" + \
                    f"\nBy: {owner}"
                )
            # Info banners
            self.infosettings = gui.widgetLabel(self.rollupBox, '')

            self.rollup_check()
            self.date_check()

            gui.separator(self.controlArea)

        else:
            self.device = None
            self.infoa.setText("No data on input yet, waiting to get something.")

    def device_id_edit(self):
        if self.device != "":
            index = self.metadata.loc[self.metadata['id'] == int(self.device)].index.tolist()[0]
            name = self.metadata.loc[index, 'name']
            city = self.metadata.loc[index, 'city']
            country = self.metadata.loc[index, 'country_code']
            owner = self.metadata.loc[index, 'owner_username']

            self.infoa.setText(f"Device: {self.device}"+ \
                f"\nName: {name}" + \
                f"\nCity: {city} ({country})" + \
                f"\nBy: {owner}"
            )

        else:
            self.infoa.setText("Select one device to see it's info")
            self.device = None

    def rollup_check(self):
        if self.rollup_number.isnumeric():
            self.rollup = self.rollup_number + str(self.rollup_text)
        else:
            self.infosettings.setText("Rollup needs to be an integer")
            self.rollup = None

    def date_check(self):
        self.min_date = None
        self.max_date = None

        if self.min_date_text != "":
            self.min_date = self.min_date_text

        if self.max_date_text != "":
            self.max_date = self.max_date_text

    def commit(self):

        if self.device is not None:

            if (self.metadata.shape[0] > 1):
                self.infoa.setText(f'Select a device first.')
                self.info.set_output_summary(self.info.NoOutput)
                return

            if self.rollup is None:
                self.infoa.setText(f'Input a valid rollup.')
                self.info.set_output_summary(self.info.NoOutput)
                return

            d = SCDevice(self.device)
            timezone = d.timezone
            progress = gui.ProgressBar(self, 4)
            progress.advance()

            # loop = asyncio.get_event_loop()
            loop.run_until_complete(d.get_data(
                        min_date = localise_date(self.min_date, timezone),
                        max_date = localise_date(self.max_date, timezone),
                        frequency = self.rollup,
                        clean_na = None,
                        resample = self.resample
                    )
                )

            data = d.data
            progress.advance()

            if data is not None:
                table = table_from_frame(data)
                progress.advance()
                self.Outputs.readings.send(table)
                progress.advance()
                self.infoa.setText(f'Device {self.device} data downloaded!')
                self.info.set_output_summary(1)

            else:
                self.infoa.setText(f'Nothing found.')
                self.info.set_output_summary(self.info.NoOutput)

            progress.finish()

        else:
            self.infoa.setText(f'Select a device first.')
            self.info.set_output_summary(self.info.NoOutput)

        return

# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(SmartcitizenSensorDataWidget).run()
