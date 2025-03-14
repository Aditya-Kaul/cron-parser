# Cron Expression Parser

A Python utility for parsing and expanding cron expressions into human-readable time schedules.

## Overview

The Cron Expression Parser takes a standard cron expression and expands it to show you exactly when your scheduled tasks will run. This makes cron expressions easier to understand and validate, especially for complex scheduling requirements.

## Features

- Support for all standard cron expression syntax:
  - Specific values (`5`)
  - Wildcards (`*`)
  - Ranges (`1-5`)
  - Lists (`1,3,5`)
  - Step values (`*/2`, `1-10/2`)
- Expands expressions into complete lists of execution times
- Clean, tabular output format
- Robust error handling for invalid expressions

## Installation

Clone this repository and ensure you have Python 3.6+ installed:

```bash
git clone https://github.com/Aditya-Kaul/cron-parser.git
cd cron-parser
chmod +x app.py
```

## Usage

Run the application with a cron expression as a command-line argument:

```bash
./app.py "*/15 0 1,15 * 1-5 /usr/bin/find"
```

### Example Output

```
minute         0 15 30 45
hour           0
day of month   1 15
month          1 2 3 4 5 6 7 8 9 10 11 12
day of week    1 2 3 4 5
command        /usr/bin/find
```

This shows that the command `/usr/bin/find` will run:
- Every 15 minutes (0, 15, 30, 45)
- At midnight (hour 0)
- On the 1st and 15th of each month
- Every month
- Monday through Friday (days 1-5)

## Cron Expression Format

A cron expression consists of six fields, separated by spaces:

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (1-7, 1=Monday)
│ │ │ │ │ ┌───────────── command to execute
│ │ │ │ │ │
│ │ │ │ │ │
* * * * * command
```

### Special Characters

- `*`: all valid values
- `-`: range of values
- `,`: list of values
- `/`: step values

## Error Handling

The application validates expressions and provides informative error messages for problems like:
- Invalid formats
- Out-of-range values
- Reversed ranges (e.g., `5-3`)
- Negative step values

