import pickle
from typing import Dict, List
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.live import Live


class EnrollmentQuerySystem:
    def __init__(self, console=None):
        self.data: Dict[str, Dict] = {}
        self.last_update: datetime = datetime.min
        self.console = console if console else Console()
        self.load_data()

    def load_data(self):
        try:
            with open('enrollment_data.pkl', 'rb') as f:
                saved_data = pickle.load(f)
                self.data = saved_data['data']
                self.last_update = saved_data['last_update']
            self.console.print(
                f"[blue]Loaded existing data.[/] Last update: [cyan]{self.last_update}[/]")
        except FileNotFoundError:
            self.console.print(
                "[yellow]No existing data found. Starting with an empty dataset.[/]")

    def save_data(self):
        with open('enrollment_data.pkl', 'wb') as f:
            pickle.dump({
                'data': self.data,
                'last_update': self.last_update
            }, f)
        self.console.print("[green]Data saved successfully.[/]")

    def should_update(self) -> bool:
        return datetime.now() - self.last_update > timedelta(minutes=5)

    def fetch_all_students_status(self):
        self.console.print("[yellow]Starting data fetch process...[/]")

        options = Options()
        options.add_argument("-headless")
        options.set_preference("dom.disable_beforeunload", True)

        # Initialize the browser before creating the Progress display
        self.console.print("[yellow]Starting browser...[/]")
        driver = webdriver.Firefox(options=options)

        # Now create the Progress display for remaining tasks
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(
                "[yellow]Processing departments...", total=None)

            try:
                progress.update(
                    task, description="Navigating to enrollment website...")
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

                progress.update(task, description="Selecting exam type...")
                wait_for_element(By.ID, "ddlExamType")
                if not select_option_by_js("ddlExamType", "ab6e8d7a-9f7b-4e6c-91eb-31ebfd5c6e52"):
                    self.console.print(
                        "[bold red]Failed to select exam type[/]")
                    return

                time.sleep(5)

                progress.update(
                    task, description="Fetching department list...")
                wait_for_element(By.ID, "ddlExamList")
                department_options = driver.execute_script("""
                    var select = document.getElementById('ddlExamList');
                    return Array.from(select.options).map(option => ({
                        value: option.value,
                        text: option.text
                    }));
                """)

                total_departments = len(department_options)
                progress.update(task, total=total_departments, completed=0,
                                description=f"Processing departments (0/{total_departments})")

                for index, dept in enumerate(department_options):
                    progress.update(
                        task, description=f"Processing [cyan]{dept['text']}[/] ({index+1}/{total_departments})")

                    if index > 0:
                        if not select_option_by_js("ddlExamList", dept['value']):
                            self.console.print(
                                f"[bold red]Failed to select department: {dept['text']}[/]")
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
                    progress.update(task, completed=index+1)

                self.last_update = datetime.now()
                self.save_data()
                progress.update(
                    task, description="[bold green]Data fetching completed![/]")

            finally:
                driver.quit()

    def query_status(self, exam_number: str) -> List[Dict]:
        # Check if we need to update before querying
        need_update = self.should_update()
        if need_update:
            self.console.print(
                "[yellow]Data is outdated. Fetching new data...[/]")
            self.fetch_all_students_status()
        else:
            # Only show a status message if we're not updating
            self.console.print("[green]Using cached data...[/]")

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
        # Don't use a live display here since query_status might create one
        self.console.print("[bold blue]Querying status...[/]")
        statuses = self.query_status(exam_number)

        self.console.print(
            f"\nResults for exam number: [bold cyan]{exam_number}[/]")

        if statuses:
            for status in statuses:
                # Get the appropriate status color
                status_color = "green" if status['status'] == '正取' else \
                    "yellow" if status['status'] == '備取' else \
                    "red" if status['status'] == '放棄' else "blue"

                # Create a panel for each department result
                dept_panel = Panel(
                    f"[bold white]Status:[/] [bold {status_color}]{status['status']}[/]\n"
                    f"[bold white]Position:[/] [cyan]{status['position']}[/]\n"
                    f"[bold white]People ahead:[/] [cyan]{len(status['people_ahead'])}[/]",
                    title=f"[bold]{status['department']}[/]",
                    border_style="blue"
                )
                self.console.print(dept_panel)

                # If there are people ahead, show them in a table
                if status['people_ahead']:
                    table = Table(title="People Ahead in Queue",
                                  show_header=True, header_style="bold magenta")
                    table.add_column("Exam Number", style="cyan")
                    table.add_column("Status", style="yellow")

                    for person in status['people_ahead']:
                        person_status_color = "yellow" if person['status'] == '備取' else "blue"
                        table.add_row(
                            person['exam_number'],
                            f"[{person_status_color}]{person['status']}[/]"
                        )

                    self.console.print(table)
        else:
            self.console.print(Panel(
                f"No information found for exam number [bold red]{exam_number}[/]",
                title="Result",
                border_style="red"
            ))


def main():
    console = Console()
    query_system = EnrollmentQuerySystem(console=console)

    # Create a stylish title
    title = Text("Taiwan University Enrollment Query System",
                 style="bold blue")
    console.print(Panel(title, border_style="blue"))

    console.print(Panel("""
    Status Legend:
    - 放棄: Give up
    - 備取: In Waiting list
    - 正取: Admitted
    - empty: Is waiting for student's response
    """, title="Information", border_style="green"))

    while True:
        try:
            from rich.prompt import Prompt
            exam_number = Prompt.ask(
                "\nEnter an exam number to query (or [bold red]exit[/] to quit)")
            if exam_number.lower() == 'exit':
                break
            query_system.display_status(exam_number)
        except ValueError:
            console.print(
                "[bold red]Invalid input. Please enter a valid exam number.[/]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Exiting the program.[/]")
            break

    console.print(Panel("Thank you for using the Enrollment Query System.",
                        title="Goodbye",
                        subtitle="Made by @treeleaves30760",
                        border_style="green"))


if __name__ == "__main__":
    main()
