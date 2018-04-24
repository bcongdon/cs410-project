# cs410-project

## Background

// TODO

## Installation

Download the source:

```
git clone https://github.com/bcongdon/cs410-project
```

Install the dependencies:

```
# If you are using Pipenv:
pipenv install
pipenv shell

# If you are using "normal" Pip:
pip install -r requirements.txt
```

## Implementation Details

### Application Architecture

![architecture](img/architecture.svg)

There are 3 main steps to setting up and running a working instance of the server:

1. **Scraper**: The scraper pulls messages from the Python mailing list into a local sqlite database. This is the first step towards creating the backend data that the application serves. Running the scraper should be done fairly regularly (i.e. once per week) to make sure the data stays up-to-date. There are options in the scraper to only scrape recent messages to make this process faster.
1. **Indexer**: The indexer transforms the data in the sqlite database into a searchable index. This process must be redone after every run of the Scraper, so that new data is searchable in the frontend.
1. **Application** (Frontend) The frontend reads from the constructed index. It allows the user to search for messages and view message threads.

### Data Models

// TODO

## Usage

### Scraper

For both of the bellow options, messages are incrementally saved to the local SQLite database. You do not have to wait for the entire scrape to finish to have locally scraped data.

**Full History Scraping:**

To scrape the entire history of the Python mailing list, run the following command:
```
python manage.py scrape
```

Note that this may take upwards of 1-2 days, as there are over 1 million messages in the history of the mailing list and the scraper has to scrape pages relatively slowly to remain "polite".

**Incremental Scraping:**

To scrape just the last month of messages, run the following command:
```
python manage.py scrape --update
```

You can also use the `--start_at` flag to start the scraping at a specific mailing list topic (topics are scraped incrementally).

An "update" scraping session will last on the order of 30 minutes.

### Indexer

To run the indexer, execute the below command:
```
python manage.py index --index_dir INDEX_DIR --db DB_FILE
```

You will have to substitute `INDEX_DIR` and `DB_FILE` for their appropriate locations. By default, the following values should work:

```
python manage.py index --index_dir ./index/ --db ./scraper.db
```

There is a progress bar displayed while the indexer is running that will tell you how long the process is expected to take. Note that you might notice that the indexer "freezes" towards the end. This is when the indexer is actually writing the index to disk, so you may have to be a bit patient.

### Application

```
python manage.py run --index_dir INDEX_DIR
```

Again, you need to substitute `INDEX_DIR` for the directory in which the index is stored. If you followed the instructions above, you can run the following command:

```
python manage.py run --index_dir ./index
```

If everything worked correctly, you'll see something similar to this in your console:

```
INFO:werkzeug: * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
INFO:werkzeug: * Restarting with stat
```

You can then visit `http://127.0.0.1:5000/` in your browser on your local machine to view the frontend.