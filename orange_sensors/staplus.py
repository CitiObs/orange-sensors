from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame

import secd_staplus_client as STAplus
from pandas import DataFrame

# Fixed stations
class STAplusWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "STA Plus"

    # Short widget description
    description = "STA Plus Things Request"

    # An icon resource file path for this widget
    icon = "icons/ogc.png"

    # Priority in the section
    priority = 3

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = True

    # Defining settings
    # TODO Add more settings and GUI elements
    thing_id = Setting("", schema_only=True)
    url = Setting("", schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Outputs:
        observationsTable = Output("Things", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        # Info banners
        self.infoa = gui.widgetLabel(info, 'No data fetched yet.')

        gui.separator(self.controlArea)

        self.searchBox = gui.widgetBox(self.controlArea, "URL")
        self.url_line = gui.lineEdit(
            self.searchBox,
            self,
            "url",
            label="URL:",
            orientation=1,
            controlWidth=200
            )

        self.searchBox = gui.widgetBox(self.controlArea, "Get data from a Thing")
        self.thing_line = gui.lineEdit(
            self.searchBox,
            self,
            "thing_id",
            label="Thing ID:",
            orientation=1,
            # callback=self.t,
            controlWidth=200
            )

        gui.separator(self.controlArea)

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Get the Thing!", callback=self.commit)

    def commit(self):
        # TODO Improve progress bar based on datastreams...
        progress = gui.ProgressBar(self, 10)
        progress.advance()

        service = STAplus.STAplusService(self.url)

        if self.thing_id != "":
            thing = service.things().find(int(self.thing_id))

            if thing is not None:
                datastreams = thing.get_datastreams().query().list()
                result_df = DataFrame()

                for datastream in datastreams:
                    data = dict()
                    # print (f'Datastream ID: {datastream.id}')
                    observations = datastream.get_observations().query().list()
                    observed_property = datastream.get_observed_property().query().item()
                    # print (observed_property.name, observed_property.id, observed_property.description)
                    timestamps = list()
                    results = list()
                    # TODO Can this be done in an better way with the actual client?
                    for b in observations:
                        # TODO Small hack for UX
                        timestamps.append(b.phenomenon_time)
                        results.append(b.result)
                        #print (b.phenomenon_time, b.result, datastream.unit_of_measurement.name)
                    data['TIME'] = timestamps
                    data[f'{observed_property.name} ({datastream.unit_of_measurement.name})'] = results
                    # TODO Improve progress bar
                    progress.advance()

                    df = DataFrame.from_dict(data).set_index('TIME')
                    result_df = result_df.combine_first(df)

                table = table_from_frame(result_df)

                progress.advance()
                self.Outputs.observationsTable.send(table)
                self.infoa.setText(f'Thing Observations {self.thing_id} gathered')
                self.info.set_output_summary(1)

            else:
                self.infoa.setText(f'Device {self.thing_id} not found. Check again')
                self.info.set_output_summary(self.info.NoOutput)

        progress.finish()

# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(STAplusWidget).run()
