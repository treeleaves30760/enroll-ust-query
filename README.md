# UST Enrollment Status Scraper

This project is a web scraper designed to query the enrollment status of students in the Taiwan University System. It automates the process of checking admission results across multiple departments for specified student exam numbers.

## Features

- Queries enrollment status for multiple student exam numbers
- Checks status across all departments
- Handles dynamic web content and JavaScript-based interactions
- Provides detailed output of results

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or higher
- Firefox browser installed
- Geckodriver installed and in your system PATH

## Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/nycu-enrollment-scraper.git
   cd nycu-enrollment-scraper
   ```

2. Install the required Python packages:

   ```bash
   pip install selenium
   ```

3. Ensure Geckodriver is installed and in your system PATH.

## Usage

1. Run the script:

   ```bash
   python main.py
   ```

2. The script will process each exam number and display the results, showing the status for each department where the student is found.

## File Structure

- `main.py`: The main script to run the queries
- `scrapy_whole.py`: Contains the web scraping logic and functions
- `README.md`: This file, containing project information and instructions

## Status Meanings

- 放棄: Give up
- 備取: In Waiting list
- 正取: Admitted
- empty: Is waiting for student's response

## Notes

- The script uses Firefox in normal mode by default. To run in headless mode, uncomment the relevant line in `scrapy_whole.py`.
- Ensure you have a stable internet connection when running the script.
- The script may take some time to complete, depending on the number of departments and exam numbers being queried.

## Contributing

Contributions to this project are welcome. Please feel free to submit a Pull Request.

## License

This project is open source and available under the [License](LICENSE).
