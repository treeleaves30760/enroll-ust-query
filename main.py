"""
This script is used to query the enrollment status of students in the Taiwan University.
Status:
- 放棄: Give up
- 備取: In Waiting list
- 正取: Admitted
- empty: Is waiting for student's response
"""

from scrapy_whole import EnrollmentQuerySystem


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
