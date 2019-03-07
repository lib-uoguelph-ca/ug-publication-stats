# UG Publication Stats

Generate repeatable, consistent statistics to measure the adoption of Open Access in the University of Guelph research community.

## Usage
1. Clone this repo
2. Run `pip install -r requirements.txt`
3. Copy `secrets.template.py` to `secrets.py`
4. \[Optional\] Update `secrets.py` with your secret information (usernames, passwords, etc.)
5. Run `ugps.py --fetch` to collect data
6. Run `ugpy.py --report list` to list all available reports.
7. Run `ugps.py --report all` to run all reports or specify an individual report by name: `ugps.py --report "Author Report"`

If you don't populate secrets.py, you'll have to use the command line arguments below to specify them when you run --fetch

### Command Line Arguments
```
usage: ugps.py [-h] [--fetch] [--email EMAIL] [--wosuser WOSUSER]
               [--wospass WOSPASS] [--in_file IN_FILE] [-v] [-vv]
               [--report [REPORT]] [--output OUTPUT]

Fetch UG OA data and run reports.

optional arguments:
  -h, --help            show this help message and exit
  --fetch               Fetch data from data sources.
  --email EMAIL, -e EMAIL   Email used to communicate with the Unpaywall API.
  --wosuser WOSUSER     Web of Science user ID
  --wospass WOSPASS     Web of Science password
  --in_file IN_FILE, -i IN_FILE     Input file (exported from web of science search)
  -v
  -vv
  --report [REPORT]     Name of report to run.
  --output OUTPUT, -o OUTPUT     Directory in which to write reports.
 ```

## Adding Reports
Reports are automatically loaded if the report class has been imported and it inherits from the Report base class. 

In simple terms, the easiest way to add your own report is to:

1. Add a new python file that contains your class to `report/reports`
2. Make sure your class inherits from `report.reporting.Report`
3. Implement the `run` function in your class.

I recommend just duplicating, renaming, and modifying `BasicReport.py`

You can interface with the database in one of two ways:
* Via the Peewee ORM - Models are defined in models.py. See `BasicReport.py` for an example of this.
* Via sqlite3. See `AuthorReport.py` for an example of this.

The Report base class provides some convenience functions to implement reports. Namely:

* `get_values(record)`: Automatically fetch values using the column mapping provided in the class. The mapping can define a callable function to extract the value from a record, an property to access in the record object, or None to create an empty column. See the Report class for more details.
* `get_value(record, key): Fetch a single value from the column mapping, following the logic outlined in `get_values()`.
* `make_file_name()`: Using a report's name, produce a sanitized version usable as a file name. 


