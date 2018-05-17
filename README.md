# DB onsite exam scoring

## Requirement
1. Prepare answer SQL file in each folder which has different questions.

Like:
```
Batch1/q1.sql
Batch1/q2.sql
Batch2/q1.sql
...
```

2. Prepare students.csv contains student id in each row

3. In Each Batch folder(use different questions), the student's submission should look like:
```
Batch1/XXXXXX/q1.sql
Batch2/XXXXXX/q1.sql
```
Where XXXXXX is the student id

4. Start the mysql server container using docker. (You need to install docker first)

./run.sh

## Usage

`$ python3 scoring.py <Batch_folder> [Batch_folder ..]`

### Example

`$ python3 scoring.py Batch1 Batch2`

## Result

The result of the scoring will write into a file named `score.csv`

## TODO
* Store the scoring result, even there is some exception occurred.
* Handle the mysql shell prompt inside SQL file.
