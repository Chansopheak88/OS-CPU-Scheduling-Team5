"""
Simple CPU Scheduling Simulator
Algorithms: FCFS, SJF, SRT, Round Robin, MLFQ
"""

from collections import deque
from copy import deepcopy

# ─────────────────────────────
# Process Class
# ─────────────────────────────
class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst

        self.start = -1
        self.finish = 0
        self.waiting = 0
        self.turnaround = 0
        self.response = -1


# ─────────────────────────────
# FCFS
# ─────────────────────────────
def fcfs(processes):
    procs = sorted(deepcopy(processes), key=lambda x: x.arrival)
    time = 0
    gantt = []

    for p in procs:
        if time < p.arrival:
            time = p.arrival

        p.start = time
        p.response = time - p.arrival
        time += p.burst
        p.finish = time

        p.turnaround = p.finish - p.arrival
        p.waiting = p.turnaround - p.burst

        gantt.append((p.pid, p.start, p.finish))

    return procs, gantt


# ─────────────────────────────
# SJF (Non-preemptive)
# ─────────────────────────────
def sjf(processes):
    procs = deepcopy(processes)
    time = 0
    done = []
    gantt = []

    while procs:
        ready = [p for p in procs if p.arrival <= time]

        if not ready:
            time += 1
            continue

        p = min(ready, key=lambda x: x.burst)
        procs.remove(p)

        p.start = time
        p.response = time - p.arrival
        time += p.burst
        p.finish = time

        p.turnaround = p.finish - p.arrival
        p.waiting = p.turnaround - p.burst

        gantt.append((p.pid, p.start, p.finish))
        done.append(p)

    return done, gantt


# ─────────────────────────────
# SRT (Preemptive)
# ─────────────────────────────
def srt(processes):
    procs = deepcopy(processes)
    n = len(procs)
    time = 0
    completed = []
    gantt = []
    last_pid = None
    seg_start = 0

    while len(completed) < n:
        ready = [p for p in procs if p.arrival <= time and p not in completed]

        if not ready:
            time += 1
            continue

        p = min(ready, key=lambda x: x.remaining)

        if p.start == -1:
            p.start = time
            p.response = time - p.arrival

        # Track Gantt segments by preemption
        if p.pid != last_pid:
            if last_pid is not None:
                gantt.append((last_pid, seg_start, time))
            seg_start = time
            last_pid = p.pid

        p.remaining -= 1
        time += 1

        if p.remaining == 0:
            p.finish = time
            p.turnaround = p.finish - p.arrival
            p.waiting = p.turnaround - p.burst
            completed.append(p)
            gantt.append((p.pid, seg_start, time))
            last_pid = None

    return completed, gantt


# ─────────────────────────────
# Round Robin
# ─────────────────────────────
def rr(processes, q=2):
    procs = sorted(deepcopy(processes), key=lambda x: x.arrival)
    queue = deque()
    time = 0
    gantt = []
    done = []
    in_queue = set()   # track which pids are already queued

    # Seed with processes that arrive at time 0
    for p in procs:
        if p.arrival <= time:
            queue.append(p)
            in_queue.add(p.pid)

    while len(done) < len(procs):
        if not queue:
            # CPU idle — advance to next arrival
            future = [p for p in procs if p.pid not in in_queue and p not in done]
            if future:
                time = min(future, key=lambda x: x.arrival).arrival
                for p in future:
                    if p.arrival <= time:
                        queue.append(p)
                        in_queue.add(p.pid)
            continue

        p = queue.popleft()

        if p.start == -1:
            p.start = time
            p.response = time - p.arrival

        run = min(q, p.remaining)
        start_t = time
        time += run
        p.remaining -= run

        gantt.append((p.pid, start_t, time))

        # Add processes that arrived during this quantum (before re-queuing current)
        for x in procs:
            if x.pid not in in_queue and x not in done and x.arrival <= time:
                queue.append(x)
                in_queue.add(x.pid)

        if p.remaining > 0:
            queue.append(p)          # re-queue after new arrivals
        else:
            p.finish = time
            p.turnaround = p.finish - p.arrival
            p.waiting = p.turnaround - p.burst
            done.append(p)
            in_queue.discard(p.pid)

    return done, gantt


# ─────────────────────────────
# Simple MLFQ (3 queues)
# ─────────────────────────────
def mlfq(processes, q0_q=2, q1_q=4, aging_limit=10):
    procs = sorted(deepcopy(processes), key=lambda x: x.arrival)

    q0 = deque()
    q1 = deque()
    q2 = deque()

    time = 0
    gantt = []
    done = []
    in_queue = set()
    wait_time = {p.pid: 0 for p in procs}

    def enqueue_arrivals(up_to_time):
        for p in procs:
            if p.pid not in in_queue and p not in done and p.arrival <= up_to_time:
                q0.append(p)
                in_queue.add(p.pid)

    enqueue_arrivals(time)

    while len(done) < len(procs):

        enqueue_arrivals(time)

        # ─── Aging (promotion from q1/q2 → q0) ───
        for queue in [q1, q2]:
            for p in list(queue):
                wait_time[p.pid] += 1
                if wait_time[p.pid] >= aging_limit:
                    queue.remove(p)
                    q0.appendleft(p)
                    wait_time[p.pid] = 0

        # ─── If all queues empty → advance time ───
        if not q0 and not q1 and not q2:
            future = [p for p in procs if p.pid not in in_queue and p not in done]
            if future:
                time = min(future, key=lambda x: x.arrival).arrival
                enqueue_arrivals(time)
            continue

        # ─── Select process ───
        if q0:
            p = q0.popleft()
            quantum = q0_q
            level = 0
        elif q1:
            p = q1.popleft()
            quantum = q1_q
            level = 1
        else:
            p = q2.popleft()
            quantum = p.remaining   # FCFS
            level = 2

        in_queue.discard(p.pid)

        # ─── First response ───
        if p.start == -1:
            p.start = time
            p.response = time - p.arrival

        run = min(quantum, p.remaining)
        start_t = time
        time += run
        p.remaining -= run

        gantt.append((p.pid, start_t, time))
        wait_time[p.pid] = 0

        # ─── Add arrivals during execution ───
        enqueue_arrivals(time)

        # ─── Finished or demote ───
        if p.remaining == 0:
            p.finish = time
            p.turnaround = p.finish - p.arrival
            p.waiting = p.turnaround - p.burst
            done.append(p)
        else:
            if level == 0:
                q1.append(p)
            elif level == 1:
                q2.append(p)
            else:
                q2.append(p)
            in_queue.add(p.pid)

    return done, gantt


# ─────────────────────────────
# Display
# ─────────────────────────────
def show_result(procs, gantt):
    print("\nGantt Chart:")
    for g in gantt:
        print(f"  {g[0]} [{g[1]}-{g[2]}]", end=" |")
    print()

    print("\n{:<6} {:>4} {:>5} {:>5}".format("PID", "WT", "TAT", "RT"))
    print("-" * 22)
    for p in procs:
        print("{:<6} {:>4} {:>5} {:>5}".format(p.pid, p.waiting, p.turnaround, p.response))

    n = len(procs)
    print("\nAverage WT  : {:.2f}".format(sum(p.waiting for p in procs) / n))
    print("Average TAT : {:.2f}".format(sum(p.turnaround for p in procs) / n))
    print("Average RT  : {:.2f}".format(sum(p.response for p in procs) / n))


# ─────────────────────────────
# MAIN
# ─────────────────────────────
def main():
    while True:
        print("\n===== CPU Scheduling Simulator =====")
        print("1. Use Sample Data")
        print("2. Enter Manually")
        print("0. Exit")

        choice = input("Choice: ").strip()

        if choice == "0":
            print("Goodbye")
            break

        # ─── Input ───
        if choice == "1":
            processes = [
                Process("P1", 0, 5),
                Process("P2", 1, 3),
                Process("P3", 2, 8),
                Process("P4", 3, 6),
            ]
        elif choice == "2":
            processes = []
            n = int(input("Number of processes: ").strip())
            for i in range(n):
                pid     = input(f"  P{i+1} PID     : ").strip()
                at      = int(input(f"  P{i+1} Arrival : ").strip())
                bt      = int(input(f"  P{i+1} Burst   : ").strip())
                processes.append(Process(pid, at, bt))
        else:
            print("Invalid choice.")
            continue

        # ─── Algorithm Menu ───
        print("\nSelect Algorithm:")
        print("  1. FCFS")
        print("  2. SJF  (Non-preemptive)")
        print("  3. SRT  (Preemptive)")
        print("  4. Round Robin")
        print("  5. MLFQ")
        print("  0. Back")
        algo = input("Choice: ").strip()

        if algo == "0":
            continue
        elif algo == "1":
            p, g = fcfs(processes)
        elif algo == "2":
            p, g = sjf(processes)
        elif algo == "3":
            p, g = srt(processes)
        elif algo == "4":
            q = int(input("Time Quantum: ").strip())
            p, g = rr(processes, q)
        elif algo == "5":
            p, g = mlfq(processes)
        else:
            print("Invalid choice.")
            continue

        show_result(p, g)

        again = input("\nRun again? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye")
            break


if __name__ == "__main__":
    main()