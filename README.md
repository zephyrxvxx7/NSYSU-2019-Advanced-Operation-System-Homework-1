# Advanced Operating Systems - Homework 1

Page Replacement Algorithms and Evaluation

## Motivation

You have learned several page replacement algorithms in class. Homework 1 asks you to
implement some of these algorithms, propose your own idea, and evaluate their system
performance

## Specification

1. Reference string: 1~500
2. Number of memory references: At least 100,000 times
3. Number of frames in the physical memory: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
4. Three test reference strings:
    - Random: Arbitrarily pick one number for each reference.
    - Locality: Simulate function calls. Each function call may refer a subset of 1/20~1/ 10
       string (the length of string can be random).
    - Your own reference string (not same to the above two settings). However, you should
       discuss why you choose such a reference string in the report.
5. You can use both reference and dirty bits.

## Requirements

1. You need to implement THREE algorithms for comparison:
    (1) FIFO algorithm
    (2) Optimal algorithm
    (3) Enhanced second-chance algorithm
2. In addition, you should develop your own algorithm (not in the textbook). Your algorithm
    is expected to at least win the FIFO one (in terms of the page-fault rate or cost), where the
    cost is defined by the number of interrupts required and the number of pages needed to be
    written back to the disk. Recall that every time when you invoke the OS to do something,
    interrupt is always necessary.
3. For each algorithm and reference string, your report should present the following three
    figures:
    - The relationship between page faults and the number of frames.
    - The relationship between the number of interrupts and the number of frames.
    - The relationship between the number of disk writes (in pages) and the number of frames.

    In addition, your report should give some discussions about the behaviors of these algorithms.

4. You need to demonstrate your program to TAs and submit your report in class.

## Due Day

2019/10/ 31

## Grading Policy

Programming 65% (including 5% for comments)
Report 35%
__Note__ If you do NOT demonstrate your program to TAs, you will get zero point in this
homework even though you submit your code and report.
