"""

Script Author: Tanmay Bhoir

SSW 810 Homework 10

"""


import os
from collections import defaultdict
from prettytable import PrettyTable
import unittest


def file_reader(path, num_fields, expect, sep='\t'):
    try:
        fopen = open(path, "r", encoding="utf-8")
    except FileNotFoundError:
        print(" can't open:", path)
    else:
        with fopen:
            for n, line in enumerate(fopen):
                if n == 0 and line == expect:
                    continue  
                else:
                    fields = line.strip()
                    fields = fields.split(sep)
                    if len(fields) != num_fields:
                        raise ValueError("Do not match number of fields")
                    else:
                        yield fields


class University:

    def __init__(self, wdir, ptables=True):
        self._wdir = wdir
        self._students = dict()
        self._instructors = dict()

        self._majors = dict()

        self._get_instructors(os.path.join(wdir, 'instructors.txt'))
        self._get_majors(os.path.join(wdir, 'majors.txt'))
        self._get_students(os.path.join(wdir, 'students.txt'))
        self._get_grades(os.path.join(wdir, 'grades.txt'))

        if ptables:
            print("\nMajors Summary")
            self.major_table()
            print("\nStudent Summary")
            self.student_table()
            print("\nInstructors summary")
            self.instructor_table()

    def _get_students(self, path):
        try:
            for cwid, name, major in file_reader(path, 3, 'cwid\tname\tmajor'):
                if cwid in self._students:
                    print(f"Already exits {cwid}")
                else:
                    self._students[cwid] = Student(cwid, name, major, self._majors[major])
        except ValueError as err:
            print(err)

    def _get_instructors(self, path):
        try:
            for cwid, name, dept in file_reader(path, 3, 'cwid\tname\tdepartment'):
                if cwid in self._instructors:
                    print(f"Already exits {cwid}")
                else:
                    self._instructors[cwid] = Instructor(cwid, name, dept)
        except ValueError as err:
            print(err)

    def _get_grades(self, path):
        try:
            for student_cwid, course, grade, instructor_cwid in file_reader(path, 4, 'Student CWID\tCourse\tLetterGrade\tInstructor CWID'):
                if student_cwid in self._students:
                    self._students[student_cwid].add_course(course, grade)
                else:
                    print(f"Warning: student cwid {student_cwid} not exist")

                if instructor_cwid in self._instructors:
                    self._instructors[instructor_cwid].add_student(course)
                else:
                    print(f"Warning: Instructor cwid {instructor_cwid} not exist")

        except ValueError as err:
            print(err)

    def _get_majors(self, path):
        try:
            for major, flag, cours in file_reader(path, 3, 'major\tflag\tcourse'):
                if major in self._majors:
                    self._majors[major].add_course(flag, cours)
                else:
                    self._majors[major] = Major(major)
                    self._majors[major].add_course(flag, cours)
        except ValueError as err:
            print(err)

    def major_table(self):
        pt = PrettyTable(field_names=['Major', 'Required', 'Elective'])
        for major in self._majors.values():
            pt.add_row(major.pt_row())
        print(pt)

    def student_table(self):
        pt = PrettyTable(field_names=['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Required Courses', 'Remaining Elective Courses'])
        for student in self._students.values():
            pt.add_row(student.pt_row())
        print(pt)

    def instructor_table(self):
        pt = PrettyTable(field_names=['CWID', 'Name', 'Dept', 'Course', 'Students'])
        for Instructor in self._instructors.values():
            for row in Instructor.pt_row():
                pt.add_row(row)
        print(pt)


class Student:

    def __init__(self, cwid, name, major, in_major):
        self._cwid = cwid
        self._name = name
        self._major = major
        self._instr_major = in_major
        self._courses = dict()

    def add_course(self, course, grade):
        Grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
        if grade in Grades:
            self._courses[course] = grade

    def pt_row(self):
        complete_course, remaining_req_course, remaining_elective_course = self._instr_major.grade_check(self._courses)
        return[self._cwid, self._name, self._major, sorted(list(complete_course)), remaining_req_course, remaining_elective_course]


class Instructor:

    def __init__(self, cwid, name, dept):
        self._cwid = cwid
        self._name = name
        self._dept = dept
        self._courses = defaultdict(int)

    def add_student(self, course):
        self._courses[course] += 1

    def pt_row(self):
        for course, students in self._courses.items():
            yield[self._cwid, self._name, self._dept, course, students]


class Major:

    def __init__(self, major, passing=None):
        self._major = major
        self._required = set()
        self._elective = set()
        if passing is None:
            self._grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}
        else:
            self._grades = passing

    def add_course(self, flag, course):

        if flag == 'R':
            self._required.add(course)
        elif flag == 'E':
            self._elective.add(course)
        else:
            raise ValueError(f"Unexcepted flag {flag}")

    def grade_check(self, courses):
        completed_course = {course for course, grade in courses.items() if grade in self._grades}
        if completed_course == "{}":
            return[completed_course, self._required, self._elective]
        else:
            remaining_req_course = self._required - completed_course
            if self._elective.intersection(completed_course):
                remaining_elective_course = None
            else:
                remaining_elective_course = self._elective
            return[completed_course, remaining_req_course, remaining_elective_course]

    def pt_row(self):
        return[self._major, self._required, self._elective]


def main():
    wdir = 'G:/Python/PythonWork/SSW 810/Stevens'
    Stevens = University(wdir)


class UniversityTest(unittest.TestCase):
    def test_univ(self):
        wdir = 'G:/Python/PythonWork/SSW 810/Stevens'
        stevens = University(wdir, False)
        
        Student = [["10103", "Baldwin, C", "SFEN", ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687'], {'SSW 555', 'SSW 540'}, None],
                        ["10115", "Wyatt, X", "SFEN", ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687'], {'SSW 555', 'SSW 540'}, None],
                        ["10172", "Forbes, I", "SFEN", ['SSW 555', 'SSW 567'], {'SSW 564', 'SSW 540'}, {'CS 545', 'CS 501', 'CS 513'}],
                        ["10175", "Erickson, D", "SFEN", ['SSW 564', 'SSW 567', 'SSW 687'], {'SSW 555', 'SSW 540'}, {'CS 545', 'CS 501', 'CS 513'}],
                        ["10183", "Chapman, O", "SFEN", ['SSW 689'], {'SSW 567', 'SSW 555', 'SSW 564', 'SSW 540'}, {'CS 545', 'CS 501', 'CS 513'}],
                        ["11399", "Cordova, I", "SYEN", ['SSW 540'], {'SYS 612', 'SYS 800', 'SYS 671'}, None],
                        ["11461", "Wright, U", "SYEN", ['SYS 611', 'SYS 750', 'SYS 800'], {'SYS 671', 'SYS 612'}, {'SSW 565', 'SSW 540', 'SSW 810'}],
                        ["11658", "Kelly, P", "SYEN", [], {'SYS 800', 'SYS 612', 'SYS 671'}, {'SSW 565', 'SSW 540', 'SSW 810'}],
                        ["11714", "Morton, A", "SYEN", ['SYS 611', 'SYS 645'], {'SYS 671', 'SYS 612', 'SYS 800'}, {'SSW 565', 'SSW 540', 'SSW 810'}],
                        ["11788", "Fuller, E", "SYEN", ['SSW 540'], {'SYS 671', 'SYS 612', 'SYS 800'}, None]]

        Instructor = [["98765", "Einstein, A", "SFEN", "SSW 567", 4],
        ["98765", "Einstein, A", "SFEN", "SSW 540", 3],
         ["98764", "Feynman, R", "SFEN", "SSW 564", 3],
         ["98764", "Feynman, R", "SFEN", "SSW 687", 3],
         ["98764", "Feynman, R", "SFEN", "CS 501", 1],
         ["98764", "Feynman, R", "SFEN", "CS 545", 1],
         ["98763", "Newton, I", "SFEN", "SSW 555", 1],
         ["98763", "Newton, I", "SFEN", "SSW 689", 1],
         ["98760", "Darwin, C", "SYEN", "SYS 800", 1],
         ["98760", "Darwin, C", "SYEN", "SYS 750", 1],
         ["98760", "Darwin, C", "SYEN", "SYS 611", 2],
         ["98760", "Darwin, C", "SYEN", "SYS 645", 1]]

        Major = [["SFEN", {'SSW 540', 'SSW 564', 'SSW 567', 'SSW 555'}, {'CS 545', 'CS 501', 'CS 513'}], ["SYEN", {'SYS 612', 'SYS 800', 'SYS 671'}, {'SSW 810', 'SSW 565', 'SSW 540'}]]

        Test_Student = [s.pt_row() for s in stevens._students.values()]
        Test_Instructor = [row for Instructor in stevens._instructors.values() for row in Instructor.pt_row()]
        Test_Major = [m.pt_row() for m in stevens._majors.values()]

        self.assertEqual(Test_Student, Student)
        self.assertEqual(Test_Instructor, Instructor)
        self.assertEqual(Test_Major, Major)


if __name__ == '__main__':
    main()
    unittest.main(exit=False, verbosity=2)