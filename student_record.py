n = int(input("Enter Number of Students (Minimum 5): "))

if n < 5:
    print("Please enter at least 5 students.")

else:
    students = []

    for i in range(n):
        print(f"\n--- Student {i + 1} ---")

        roll = int(input("Roll No: "))
        name = input("Name: ")

        marks = []

        for j in range(5):
            mark = int(input(f"Subject {j + 1} Marks: "))
            marks.append(mark)

        total = sum(marks)
        percentage = total / 5

        if percentage >= 90:
            grade = "A"
        elif percentage >= 80:
            grade = "B"
        elif percentage >= 70:
            grade = "C"
        elif percentage >= 60:
            grade = "D"
        else:
            grade = "F"

        student = {
            "roll": roll,
            "name": name,
            "total": total,
            "percentage": percentage,
            "grade": grade
        }

        students.append(student)

    students.sort(key=lambda student: student["total"], reverse=True)

    print("\n========== Rank List ==========")

    rank = 1

    for i, student in enumerate(students):

        if i > 0 and student["total"] != students[i - 1]["total"]:
            rank = i + 1

        print(f"\nRank: {rank}")
        print(f"Roll No: {student['roll']}")
        print(f"Name: {student['name']}")
        print(f"Total: {student['total']}")
        print(f"Percentage: {student['percentage']:.2f}%")
        print(f"Grade: {student['grade']}")