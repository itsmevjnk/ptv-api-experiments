# PTV Timetable API experiments

This repo contains helper functions for interacting with Public Transport Victoria (PTV)'s Timetable API using Python.

**DISCLAIMER:** Usage of the PTV Timetable API is subject to PTV regulations and restrictions; refer to [this](https://www.ptv.vic.gov.au/footer/data-and-reporting/datasets/ptv-timetable-api/) for more information. This repository and any code within is not created nor endorsed by PTV.

## Installation

Get started by cloning this repo:

```
git clone https://github.com/itsmevjnk/ptv-api-experiments
```

Then, install the modules required for this repo (`python-dotenv` and `requests`):

```
cd ptv-api-experiments
pip install -r requirements.txt
```

Finally, copy the `.env.template` file into `.env` (this file will be ignored by Git), and put your PTV Timetable API user ID and API key in the `PTV_API_ID` and `PTV_API_KEY` variables in the file. For more information regarding this, read [the PTV Timetable API documentation](https://www.ptv.vic.gov.au/footer/data-and-reporting/datasets/ptv-timetable-api/).

## Usage

The `main.py` Python script lets the user make requests to the Timetable API. More scripts will come later.

## Contributing

Contributions to this project, either via pull requests or raising issues, are welcome. 
