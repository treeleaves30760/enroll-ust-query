import pickle
from typing import Dict, List
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time


class EnrollmentQuerySystem:
    def __init__(self):
        self.data: Dict[str, Dict] = {}
        self.last_update: datetime = datetime.min
        self.load_data()

    def load_data(self):
        try:
            with open('enrollment_data.pkl', 'rb') as f:
                saved_data = pickle.load(f)
                self.data = saved_data['data']
                self.last_update = saved_data['last_update']
            print(f"Loaded existing data. Last update: {self.last_update}")
        except FileNotFoundError:
            print("No existing data found. Starting with an empty dataset.")

    def save_data(self):
        with open('enrollment_data.pkl', 'wb') as f:
            pickle.dump({
                'data': self.data,
                'last_update': self.last_update
            }, f)
        print("Data saved successfully.")

    def should_update(self) -> bool:
        return datetime.now() - self.last_update > timedelta(minutes=5)

    def fetch_all_students_status(self):
        options = Options()
        options.add_argument("-headless")
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

            wait_for_element(By.ID, "ddlExamType")
            if not select_option_by_js("ddlExamType", "ab6e8d7a-9f7b-4e6c-91eb-31ebfd5c6e52"):
                print("Failed to select exam type")
                return

            time.sleep(5)

            wait_for_element(By.ID, "ddlExamList")
            department_options = driver.execute_script("""
                var select = document.getElementById('ddlExamList');
                return Array.from(select.options).map(option => ({
                    value: option.value,
                    text: option.text
                }));
            """)

            for index, dept in enumerate(department_options):
                print(
                    f"Processing department {index + 1}/{len(department_options)}: {dept['text']}")

                if index > 0:
                    if not select_option_by_js("ddlExamList", dept['value']):
                        print(f"Failed to select department: {dept['text']}")
                        continue
                    time.sleep(1)

                table = wait_for_element(By.ID, "dgUserList")
                rows = table.find_elements(By.TAG_NAME, "tr")

                department_data = []
                for row in rows[1:]:  # Skip header row
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 0:
                        exam_number = cells[0].text.strip()
                        name = cells[1].text.strip()
                        status = cells[3].text.strip(
                        ) if cells[3].text.strip() else '電話通知錄取中'
                        department_data.append({
                            "exam_number": exam_number,
                            "name": name,
                            "status": status
                        })

                self.data[dept['text']] = department_data

            self.last_update = datetime.now()
            self.save_data()
            print("All data fetched and saved successfully.")

        finally:
            driver.quit()

    def query_status(self, exam_number: str) -> List[Dict]:
        if self.should_update():
            print("Data is outdated. Fetching new data...")
            self.fetch_all_students_status()

        results = []
        for dept, students in self.data.items():
            people_ahead = []
            for i, student in enumerate(students):
                if student['exam_number'] == exam_number:
                    results.append({
                        "department": dept,
                        "status": student['status'],
                        "name": student['name'],
                        "people_ahead": people_ahead,
                        "position": i + 1
                    })
                    break
                elif student['status'] in ["備取", "電話通知錄取中"]:
                    people_ahead.append(student)
        return results

    def display_status(self, exam_number: str):
        statuses = self.query_status(exam_number)
        if statuses:
            print(f"\nStatus for exam number {exam_number}:")
            for status in statuses:
                print(f"Department: {status['department']}")
                print(f"Status: {status['status']}")
                print(f"Position in queue: {status['position']}")
                print(f"People ahead: {len(status['people_ahead'])}")
                if status['people_ahead']:
                    print("List of people ahead:")
                    for person in status['people_ahead']:
                        print(f"  - Exam Number: {person['exam_number']}, "
                              f"Status: {person['status']}")
                print("---")
        else:
            print(f"\nNo information found for exam number {exam_number}")


def main():
    query_system = EnrollmentQuerySystem()

    while True:
        try:
            exam_number = input(
                "Enter an exam number to query (or 'exit' to quit): ")
            if exam_number.lower() == 'exit':
                break
            query_system.display_status(exam_number)
        except ValueError:
            print("Invalid input. Please enter a valid exam number.")
        except KeyboardInterrupt:
            print("\nExiting the program.")
            break

    print("Thank you for using the Enrollment Query System.\nThis is made by @treeleaves30760.")


if __name__ == "__main__":
    main()
