"""
This script is used to query the enrollment status of students in the Taiwan University.
Status:
- 放棄: Give up
- 備取: In Waiting list
- 正取: Admitted
- empty: Is waiting for student's response
"""

from scrap import get_all_enrollment_statuses

Query_List = [3001540]  # 放入你想要查詢的學號


def main():
    for exam_number in Query_List:
        print(f"Processing exam number: {exam_number}")
        results = get_all_enrollment_statuses(exam_number)
        if results:
            print(f"\nStatus for exam number {exam_number}:")
            for status in results:
                print(f"Department: {status['department']}")
                print(f"Status: {status['status']}")
                print("---")
        else:
            print(f"\nNo information found for exam number {exam_number}")


if __name__ == "__main__":
    main()
