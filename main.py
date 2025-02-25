"""
This script is used to query the enrollment status of students in the Taiwan University.
Status:
- 放棄: Give up
- 備取: In Waiting list
- 正取: Admitted
- empty: Is waiting for student's response
"""

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

from scrapy_whole import EnrollmentQuerySystem


def main():
    console = Console()

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

    query_system = EnrollmentQuerySystem(console=console)

    while True:
        try:
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
