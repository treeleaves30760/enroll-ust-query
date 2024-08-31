from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, JavascriptException
import time


def get_all_enrollment_statuses(exam_number):
    options = Options()
    # options.add_argument("-headless")  # Uncomment this line to run in headless mode
    options.set_preference("dom.disable_beforeunload", True)
    driver = webdriver.Firefox(options=options)

    try:
        driver.get("https://enroll-ust.nycu.edu.tw/")

        def wait_for_element(by, value, timeout=20):
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )

        def select_option_by_js(select_id, option_value):
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

        time.sleep(5)

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

        for index, dept in enumerate(department_options):
            print(
                f"Processing department {index + 1}/{len(department_options)}: {dept['text']}")

            if index > 0:  # Skip selection for the first department as it's already selected
                if not select_option_by_js("ddlExamList", dept['value']):
                    print(f"Failed to select department: {dept['text']}")
                    continue
                print("Department selected")
                time.sleep(1)

            try:
                table = wait_for_element(By.ID, "dgUserList")
                rows = table.find_elements(By.TAG_NAME, "tr")
                found = False
                people_ahead = []
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 0:
                        if cells[0].text.strip() == str(exam_number):
                            status = cells[3].text.strip()
                            results.append({
                                "department": dept['text'],
                                "status": status if status else '電話通知錄取中',
                                "people_ahead": people_ahead
                            })
                            found = True
                            break
                        elif cells[3].text.strip() in ["備取", ""] and cells[0].text.strip() != "考生編號":
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

    if statuses:
        print(f"\nStatus for exam number {exam_number}:")
        for status in statuses:
            print(f"Department: {status['department']}")
            print(
                f"Status: {status['status'] if status['status'] else '電話通知錄取中'}")
            print(f"People ahead: {len(status['people_ahead'])}")
            if len(status['people_ahead']):
                print("List of people ahead:")
                for person in status['people_ahead']:
                    print(
                        f"  - Exam Number: {person['exam_number']}, Name: {person['name']}, Status: {person['status']}")
            print("---")
    else:
        print(f"\nNo information found for exam number {exam_number}")
