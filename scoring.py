import os
import sys
import pandas as pd
import re
import subprocess
import signal
import filecmp
import csv

sub_proc = None
msg = None

def add_student_msg(student, msg):
    if student.get("msg", None) is None:
        student["msg"] = msg
    else:
        student["msg"] += "\\" + msg

def dummy(signum, frame):
    global sub_proc
    global msg
    if not sub_proc.poll():
        print("Too long")
        msg = "SQL query time too long stop early"
        sub_proc.kill()

def get_student(folder, students):
    for student in students:
        if folder.endswith(student["id"]):
            return student

def match_answer_file(student, files):
    files_str = " ".join(files)
    for q_num in [1,2,3]:
        rePR = "\S*[qQ]{}\.sql\S*".format(q_num)
        match = re.findall(rePR, files_str)
        if match:
            student["Q{}".format(q_num)] = match[0]
        else:
            msg = "q{}.sql not found ".format(q_num)
            add_student_msg(student, msg)

def run_sql_query(infile, outfile, tmpfile):
    global sub_proc
    signal.signal(signal.SIGALRM, dummy)
    args = ["./scoring.sh",
            infile, 
            outfile,
            tmpfile]
    sub_proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    signal.alarm(60)
    sub_proc.wait(70)
    
    signal.alarm(0)
    subprocess.run(["rm", "-f", tmpfile])

def generate_answer(folder):
    answers_query = [ans for ans in os.listdir(folder) if ans.endswith(".sql")]
    for i in range(1,4):
        infile = "{}/q{}.sql".format(folder, i)
        outfile = "{}/q{}.csv".format(folder,i)
        tmpfile = "{}/q{}.tmp".format(folder, i)
        if os.path.exists(outfile):
            continue
        run_sql_query(infile, outfile, tmpfile)

def scoring_questions(student, root_path, batch):
    global msg
    count = 0
    for q in range(1,4):
        q_num = "Q{}".format(q)
        msg = None
        TA_answer_file = "{}/q{}.csv".format(batch, q)
        if not student[q_num]:
            continue

        student_query_file = os.path.join(root_path, student[q_num])
        student_answer_file = os.path.join(root_path, "q{}.csv".format(q))
        tmp_file = os.path.join(root_path, "q{}.tmp".format(q))
        run_sql_query(student_query_file, student_answer_file, tmp_file)
        if msg:
            subprocess.run(["./clear.sh"])
            msg = "{} {}".format(q_num, msg)
            add_student_msg(student, msg)
            student[q_num] = "Too long"
        else:
            student[q_num] = match_files(TA_answer_file, student_answer_file)

        if student[q_num] is True:
            count += 1

    if count == 0:
        student["score"] = 0
    elif count == 1:
        student["score"] = 60
    elif count == 2:
        student["score"] = 80
    elif count == 3:
        student["score"] = 100
    else:
        print("Count Error {}".format(count))

def match_files(answer, student_ans):
        return filecmp.cmp(answer, student_ans)

def scoring(folder, students):
    for root, dirs, files in os.walk(folder):
        student = get_student(root, students)
        if not student:
            continue
        #if student["id"] != "0516103":
        #    continue

        print(student["id"])
        match_answer_file(student, files)
        scoring_questions(student, root, folder)
        print(student["score"])
        #print(student)

def read_student_file(file_name):
    student_ids = pd.read_csv(file_name, header=None)
    student_ids = student_ids.as_matrix()
    students = []
    for sid in student_ids:
        students.append(dict(id=sid[0],Q1=None,Q2=None,Q3=None,score=None,msg=None))

    return students

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Please provide folder name which contains SQL script")

    students = read_student_file("students.csv")
    for folder in sys.argv[1:]:
        print(folder)
        generate_answer(folder) 
        scoring(folder, students)

    with open("score.csv", "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(["Student ID", "Q1", "Q2", "Q3", "score", "msg"])
        for student in students:
            row = list()
            for field in ["id", "Q1", "Q2", "Q3", "score", "msg"]:
                if student[field] is not None:
                    row.append(student[field])
                else:
                    if field in ["Q1", "Q2", "Q3"]:
                        row.append("No submission")
            
            writer.writerow(row)
