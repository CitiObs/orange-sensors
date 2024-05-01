# <img src="orange_sensors/icons/main.png" alt="orange-sensors" width="30"/> Orange Sensors

This is a work-in progress repository for Orange Data Mining widgets to access data from [Smart Citizen](https://smartcitizen.me) and [STAplus]().

This repository forms part of the CitiObs project, and has received funding from the European Union. See [Funding](#funding) section.

**Note**: this project has been inspired by [MECODA-Orange](https://github.com/eosc-cos4cloud/mecoda-orange).

## <img src="orange_sensors/icons/smartcitizen_data.png" alt="smartcitizen-logo" width="30"/> Smart Citizen widgets

The first widget (Smart Citizen Search) collects data from the Smart Citizen API. It allows to select the device either via device ID (the number after https://smartcitizen.me/kits/[...]) or by searching the API by city, tags, or device type. The second widget (Smart Citizen Data) uses the data from the first one and collects timeseries tabular data from a device, with a defined `rollup` (i.e. the frequency of the readings), minimum and maximum date; as well as resample options.

## <img src="orange_sensors/icons/ogc.png" alt="staplus-logo" width="30"/> STAPlus widgets

The STAplus node requires the `secd_staplus_client` library. For now, it's only available in private mode.

## Development

Clone and install in editable mode with your environment of preference:

```
git clone git@github.com:fablabbcn/orange-sensors.git
cd orange-sensors
```

```
pip install -e .
```

Run orange canvas:

```
python -m Orange.canvas
```

## Funding

<img src="assets/eu_funded_en.jpg" alt="funded-eu" width="500"/> 

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Research Executive Agency (REA). Neither the European Union nor the granting authority can be held responsible for them.



