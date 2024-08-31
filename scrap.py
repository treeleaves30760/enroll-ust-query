"""
Enrollment Status Scraper

This script scrapes enrollment statuses for students from the NYCU enrollment website.
It uses Selenium WebDriver to automate the process of navigating the website and
extracting information for a given exam number across all departments.

Usage:
1. Ensure you have the necessary dependencies installed (selenium, firefox webdriver).
2. Run the script with a valid exam number.
3. The script will output the enrollment status and queue position for the student
   in each department where they are listed.

Note: This script is designed for educational purposes and should be used responsibly
and in accordance with the website's terms of service.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, JavascriptException
import time


def get_all_enrollment_statuses(exam_number):
    """
    Scrape enrollment statuses for a given exam number across all departments.

    Args:
    exam_number (int): The exam number to search for.

    Returns:
    list: A list of dictionaries containing enrollment status information for each department.
    """
    options = Options()
    # options.add_argument("-headless")  # Uncomment this line to run in headless mode
    options.set_preference("dom.disable_beforeunload", True)
    driver = webdriver.Firefox(options=options)

    try:
        driver.get("https://enroll-ust.nycu.edu.tw/")

        def wait_for_element(by, value, timeout=20):
            """Wait for an element to be present on the page."""
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )

        def select_option_by_js(select_id, option_value):
            """Select an option in a dropdown using JavaScript."""
            js_code = f"""
            var select = document.getElementById('{select_id}');
            for(var i=0; i<select.options.length; i++) {{
                if(select.options[i].value == '{option_value}') {{
                    select.selectedIndex = i;
                    var event = new Event('change');
                    select.dispatchEvent(event);
                    return true;
                }}
            }}
            return false;
            """
            return driver.execute_script(js_code)

        # Select the correct exam type
        wait_for_element(By.ID, "ddlExamType")
        if not select_option_by_js("ddlExamType", "ab6e8d7a-9f7b-4e6c-91eb-31ebfd5c6e52"):
            print("Failed to select exam type")
            return []

        time.sleep(5)  # Wait for the page to load after selecting exam type

        results = []

        # Get all department options
        wait_for_element(By.ID, "ddlExamList")
        department_options = driver.execute_script("""
            var select = document.getElementById('ddlExamList');
            return Array.from(select.options).map(option => ({
                value: option.value,
                text: option.text
            }));
        """)

        print(f'Found {len(department_options)} departments')

        # Iterate through each department
        for index, dept in enumerate(department_options):
            print(
                f"Processing department {index + 1}/{len(department_options)}: {dept['text']}")

            # Select the department (skip for the first one as it's already selected)
            if index > 0:
                if not select_option_by_js("ddlExamList", dept['value']):
                    print(f"Failed to select department: {dept['text']}")
                    continue
                print("Department selected")
                # Wait for the page to load after selecting department
                time.sleep(1)

            try:
                # Find and process the table of students
                table = wait_for_element(By.ID, "dgUserList")
                rows = table.find_elements(By.TAG_NAME, "tr")
                found = False
                people_ahead = []

                # Process each row in the table
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 0:
                        if cells[0].text.strip() == str(exam_number):
                            # Found the target student
                            status = cells[3].text.strip()
                            results.append({
                                "department": dept['text'],
                                "status": status if status else '電話通知錄取中',
                                "people_ahead": people_ahead
                            })
                            found = True
                            break
                        elif cells[3].text.strip() in ["備取", ""] and cells[0].text.strip() != "考生編號":
                            # Found a person ahead in the queue
                            people_ahead.append({
                                "exam_number": cells[0].text.strip(),
                                "name": cells[1].text.strip(),
                                "status": cells[3].text.strip() if cells[3].text.strip() else '電話通知錄取中'
                            })

                if found:
                    print(
                        f"Found student in department {index + 1}/{len(department_options)}")
                else:
                    print(
                        f"Student not found in department {index + 1}/{len(department_options)}")
            except TimeoutException:
                print(f"Table not found for department {dept['text']}")

        return results

    except JavascriptException as e:
        print(f"JavaScript error: {e}")
        return []
    finally:
        driver.quit()


if __name__ == "__main__":
    # Example usage
    exam_number = 3001540  # Replace with the exam number you want to query
    statuses = get_all_enrollment_statuses(exam_number)

    # Display the results
    if statuses:
        print(f"\nStatus for exam number {exam_number}:")
        for status in statuses:
            print(f"Department: {status['department']}")
            print(f"Status: {status['status']}")
            print(f"People ahead: {len(status['people_ahead'])}")
            if len(status['people_ahead']):
                print("List of people ahead:")
                for person in status['people_ahead']:
                    print(
                        f"  - Exam Number: {person['exam_number']}, Name: {person['name']}, Status: {person['status']}")
            print("---")
    else:
        print(f"\nNo information found for exam number {exam_number}")
