# OS-CPU-Scheduling-Team5
# CPU Scheduling Simulator

A terminal-based Python simulator for five classic CPU scheduling algorithms. Enter processes manually or use built-in sample data, then view a Gantt chart alongside per-process and average metrics.

---

## Algorithms

| # | Algorithm | Type |
|---|-----------|------|
| 1 | **FCFS** – First Come First Served | Non-preemptive |
| 2 | **SJF** – Shortest Job First | Non-preemptive |
| 3 | **SRT** – Shortest Remaining Time | Preemptive |
| 4 | **RR** – Round Robin | Preemptive |
| 5 | **MLFQ** – Multi-Level Feedback Queue | Preemptive |

---

## Requirements

- Python **3.7+**
- No third-party libraries — standard library only (`collections`, `copy`)

---

## Usage

```bash
python scheduler.py
```

You will be presented with a menu:

```
===== CPU Scheduling Simulator =====
1. Use Sample Data
2. Enter Manually
0. Exit
```

### Option 1 — Sample Data
Runs a preset of four processes (P1–P4) so you can immediately try any algorithm.

### Option 2 — Manual Input
Enter each process one at a time:

```
Number of processes: 3
  P1 PID     : P1
  P1 Arrival : 0
  P1 Burst   : 5
  P2 PID     : P2
  ...
```

After entering processes, select an algorithm:

```
Select Algorithm:
  1. FCFS
  2. SJF  (Non-preemptive)
  3. SRT  (Preemptive)
  4. Round Robin
  5. MLFQ
  0. Back
```

For **Round Robin**, you will also be prompted for a time quantum:
```
Time Quantum: 2
```

---

## Output

```
Gantt Chart:
  P1 [0-5] | P2 [5-8] | P4 [8-14] | P3 [14-22] |

PID     WT   TAT    RT
----------------------
P1       0     5     0
P2       4     7     4
P3      12    20    12
P4       5    11     5

Average WT  : 5.25
Average TAT : 10.75
Average RT  : 5.25
```

**Metrics defined:**

| Metric | Formula |
|--------|---------|
| **WT** – Waiting Time | Turnaround − Burst |
| **TAT** – Turnaround Time | Finish − Arrival |
| **RT** – Response Time | First CPU access − Arrival |

---

## Algorithm Details

### FCFS
Processes are served strictly in arrival order. Simple but can suffer from the *convoy effect* where short jobs wait behind long ones.

### SJF
At each scheduling point, the process with the shortest burst time among all arrived processes is selected. Optimal average waiting time for non-preemptive scheduling, but requires knowing burst times in advance.

### SRT
Preemptive version of SJF. At every clock tick, the process with the least remaining time runs. A newly arrived process can preempt the current one if its remaining time is shorter. The Gantt chart reflects each preemption as a separate segment.

### Round Robin
Each process gets a fixed time quantum in a cyclic order. Processes that arrive during a quantum are enqueued after the current quantum finishes. Preempted processes are placed at the back of the queue behind any new arrivals — giving new jobs a fair first shot.

### MLFQ (Multi-Level Feedback Queue)
Three queues with decreasing priority:

| Queue | Scheduling | Quantum |
|-------|-----------|---------|
| Q0 (high) | Round Robin | 2 |
| Q1 (mid)  | Round Robin | 4 |
| Q2 (low)  | FCFS        | until finish |

- New processes enter **Q0**.
- A process that uses its full quantum is **demoted** to the next lower queue.
- Processes waiting too long in Q1/Q2 are **promoted** back to Q0 (aging threshold: 10 ticks), preventing starvation.

---

## Project Structure

```
scheduler.py       # Single-file implementation
README.md          # This file
```

---

## Extending the Simulator

To add a new algorithm:

1. Define a function `my_algo(processes) -> (done_list, gantt_list)` following the same signature as the existing ones.
2. Add a menu entry in `main()`.
3. Call `show_result(p, g)` with the returned values.

The `Process` class fields available to you:

```python
p.pid         # Process identifier
p.arrival     # Arrival time
p.burst       # Original burst time
p.remaining   # Remaining burst (for preemptive algorithms)
p.start       # Time first scheduled (-1 if not yet run)
p.finish      # Completion time
p.waiting     # Waiting time (set after completion)
p.turnaround  # Turnaround time (set after completion)
p.response    # Response time (set on first scheduling)
```

---

## License

MIT — free to use, modify, and distribute.