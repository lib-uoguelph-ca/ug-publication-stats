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
