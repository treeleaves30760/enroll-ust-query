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


if __name__ == "__main__":
    main()
