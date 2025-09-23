import random
import matplotlib.pyplot as plt
from collections import deque
import pandas as pd
import time  # oben sicherstellen, dass time importiert ist

Num_Ticks = 50
Num_Nodes = 20
Num_Tasks = 200
Num_Tasks_Per_Tick = 50
Num_Nodes_Per_Tick = 1
Prob_Node_Change = 0.2


class Node:
    def __init__(self, node_id, cpu, ram, storage):
        self.node_id = node_id
        self.total_cpu = cpu
        self.total_ram = ram
        self.total_storage = storage
        self.available_cpu = cpu
        self.available_ram = ram
        self.available_storage = storage
        self.tasks = []

    def can_host(self, task):
        return (self.available_cpu >= task.cpu and
                self.available_ram >= task.ram and
                self.available_storage >= task.storage)

    def assign_task(self, task):
        if self.can_host(task):
            self.available_cpu -= task.cpu
            self.available_ram -= task.ram
            self.available_storage -= task.storage
            self.tasks.append(task)
            task.assigned_node = self
            return True
        return False

    def release_task(self, task):
        if task in self.tasks:
            self.available_cpu += task.cpu
            self.available_ram += task.ram
            self.available_storage += task.storage
            self.tasks.remove(task)


class Task:
    def __init__(self, task_id, cpu, ram, storage, duration, start_time):
        self.task_id = task_id
        self.cpu = cpu
        self.ram = ram
        self.storage = storage
        self.duration = duration
        self.remaining = duration
        self.start_time = start_time
        self.assigned_node = None

    def tick(self):
        if self.remaining > 0:
            self.remaining -= 1
        return self.remaining == 0


class GreedyScheduler:
    def __init__(self, nodes):
        self.nodes = nodes

    def schedule(self, task):
        for node in self.nodes:  # Greedy: erstes passendes Node wählen
            if node.assign_task(task):
                return True
        return False


def export_to_csv(history, filename="schedule.csv"):
    df = pd.DataFrame(history, columns=["task_id", "node_id", "start", "duration"])
    df.to_csv(filename, index=False)
    print(f"Exported schedule to {filename}")


# Simulation mit Logging für Gantt-Chart
def run_simulation(seed=42):
    random.seed(seed)
    nodes = [Node(node_id=i, cpu=16, ram=64, storage=500) for i in range(Num_Nodes)]
    scheduler = GreedyScheduler(nodes)

    waiting_tasks = deque()
    running_tasks = []
    history = []
    utilization_log = []
    scheduling_time_log = []
    system_log = []  # neues Log für aktive Nodes & Tasks

    # === Start-Tasks ===
    for i in range(Num_Tasks):
        t = Task(
            task_id=f"Init-{i}",
            cpu=random.randint(1, 8),
            ram=random.randint(2, 16),
            storage=random.randint(10, 100),
            duration=random.randint(2, 20),
            start_time=0
        )
        waiting_tasks.append(t)

    for tick in range(1, Num_Ticks + 1):
        # === neue Tasks ===
        num_new = random.randint(0, Num_Tasks_Per_Tick)
        for _ in range(num_new):
            if random.random() < 0.6:
                t = Task(
                    task_id=f"T{tick}-{random.randint(100,999)}",
                    cpu=random.randint(1, 8),
                    ram=random.randint(2, 16),
                    storage=random.randint(10, 100),
                    duration=random.randint(2, 20),
                    start_time=tick
                )
                waiting_tasks.append(t)

        # === zufällige Stornierung ===
        num_remove = random.randint(0, min(Num_Tasks_Per_Tick, len(waiting_tasks)))
        for _ in range(num_remove):
            if waiting_tasks and random.random() < 0.2:
                dropped = waiting_tasks.popleft()
                print(f"Task {dropped.task_id} wurde vor Start entfernt")

        # === zufällige Node-Änderungen ===
        if random.random() < Prob_Node_Change:
            num_changes = random.randint(1, Num_Nodes_Per_Tick)
            for _ in range(num_changes):
                if random.random() < 0.5 and nodes:  # Node entfernen
                    removed = nodes.pop()
                    print(f"⚠️ Node {removed.node_id} entfernt")
                    # Laufende Tasks von entferntem Node abbrechen
                    for t in removed.tasks[:]:
                        removed.release_task(t)
                        running_tasks.remove(t)
                        waiting_tasks.append(t)  # zurück in Queue
                else:  # Node hinzufügen
                    new_id = max([n.node_id for n in nodes]) + 1 if nodes else 0
                    new_node = Node(new_id, cpu=16, ram=64, storage=500)
                    nodes.append(new_node)
                    print(f"✅ Node {new_node.node_id} hinzugefügt")

        # === Scheduling-Zeit messen ===
        start_time_tick = time.perf_counter()
        for _ in range(len(waiting_tasks)):
            task = waiting_tasks.popleft()
            if scheduler.schedule(task):
                running_tasks.append(task)
                history.append((task.task_id, task.assigned_node.node_id, task.start_time, task.duration))
            else:
                waiting_tasks.append(task)
        end_time_tick = time.perf_counter()
        scheduling_time_log.append(end_time_tick - start_time_tick)

        # === Laufende Tasks updaten ===
        finished = []
        for task in running_tasks:
            if task.tick():
                finished.append(task)
        for task in finished:
            task.assigned_node.release_task(task)
            running_tasks.remove(task)

        # === Auslastung loggen ===
        tick_util = {"tick": tick, "num_nodes": len(nodes)}
        for node in nodes:
            tick_util[f"Node{node.node_id}_CPU"] = (node.total_cpu - node.available_cpu) / node.total_cpu
            tick_util[f"Node{node.node_id}_RAM"] = (node.total_ram - node.available_ram) / node.total_ram
            tick_util[f"Node{node.node_id}_Storage"] = (node.total_storage - node.available_storage) / node.total_storage
        utilization_log.append(tick_util)

        # === Systemmetriken loggen ===
        system_log.append({
            "tick": tick,
            "num_nodes": len(nodes),
            "waiting_tasks": len(waiting_tasks),
            "running_tasks": len(running_tasks),
            "total_tasks": len(waiting_tasks) + len(running_tasks),
            "scheduling_time_s": end_time_tick - start_time_tick
        })

    util_df = pd.DataFrame(utilization_log)
    sched_time_df = pd.DataFrame({"tick": range(1, Num_Ticks + 1), "scheduling_time_s": scheduling_time_log})
    system_df = pd.DataFrame(system_log)
    system_df.to_csv("system_metrics.csv", index=False)
    print("Exported system metrics to system_metrics.csv")

    return history, nodes, util_df, sched_time_df, system_df


# Visualisierung als Gantt-Chart
def plot_schedule(history, num_nodes):
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.get_cmap("tab20", len(history))

    for i, (task_id, node_id, start, duration) in enumerate(history):
        ax.broken_barh([(start, duration)], (node_id - 0.4, 0.8), facecolors=colors(i), label=task_id if i < 10 else "")

    ax.set_xlabel("Zeit (Ticks)")
    ax.set_ylabel("Node")
    ax.set_yticks(range(num_nodes))
    ax.set_yticklabels([f"Node {i}" for i in range(num_nodes)])
    ax.set_title("Greedy Scheduling Simulation (Gantt-Chart)")
    ax.grid(True)

    # Nur die ersten 10 Tasks in Legende
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, title="Tasks", loc="upper right", fontsize="small")

    plt.show()


def plot_utilization(nodes):
    resources = ["CPU", "RAM", "Storage"]
    used = {r: [] for r in resources}
    total = {r: [] for r in resources}

    for node in nodes:
        total["CPU"].append(node.total_cpu)
        total["RAM"].append(node.total_ram)
        total["Storage"].append(node.total_storage)

        used["CPU"].append(node.total_cpu - node.available_cpu)
        used["RAM"].append(node.total_ram - node.available_ram)
        used["Storage"].append(node.total_storage - node.available_storage)

    avg_usage = {
        r: sum(used[r]) / sum(total[r]) if sum(total[r]) else 0
        for r in resources
    }

    fig, ax = plt.subplots(figsize=(10, 5))
    bar_width = 0.25
    x = range(len(nodes))

    for i, r in enumerate(resources):
        usage = [used[r][j] / total[r][j] if total[r][j] else 0 for j in range(len(nodes))]
        ax.bar([p + i*bar_width for p in x], usage, width=bar_width, label=r)

    for i, r in enumerate(resources):
        ax.bar(len(nodes) + i*bar_width,
               avg_usage[r],
               width=bar_width,
               color=ax.patches[i].get_facecolor(),
               hatch="//",
               label=f"{r} (Gesamt)")

    ax.set_ylabel("Auslastung (0–1)")
    ax.set_title("Node- und Gesamtauslastung")
    ax.set_xticks([p + bar_width for p in x] + [len(nodes) + bar_width])
    ax.set_xticklabels([f"Node {n.node_id}" for n in nodes] + ["Gesamt"])
    ax.legend()
    ax.set_ylim(0, 1.1)
    ax.grid(True, axis="y")

    plt.show()


def plot_utilization_over_time(util_df):
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    resources = ["CPU", "RAM", "Storage"]

    for i, res in enumerate(resources):
        ax = axs[i]
        for col in [c for c in util_df.columns if res in c]:
            ax.plot(util_df["tick"], util_df[col], label=col.replace("_", " "))
        ax.set_ylabel(f"{res}-Auslastung")
        ax.set_ylim(0, 1.1)
        ax.grid(True)
        ax.legend(loc="upper right")

    axs[-1].set_xlabel("Ticks")
    fig.suptitle("Auslastung der Nodes über die Zeit")
    plt.tight_layout()
    plt.show()


def plot_scheduling_time(sched_time_df):
    plt.figure(figsize=(10, 4))
    plt.plot(sched_time_df["tick"], sched_time_df["scheduling_time_s"], marker='o')
    plt.xlabel("Tick")
    plt.ylabel("Schedulingzeit pro Tick [s]")
    plt.title("Greedy Schedulingzeit pro Tick")
    plt.grid(True)
    plt.show()


def plot_system_log(system_df):
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    axs[0].plot(system_df["tick"], system_df["num_nodes"], label="Aktive Nodes", color="blue")
    axs[0].set_ylabel("Nodes")
    axs[0].set_title("Aktive Nodes über die Zeit")
    axs[0].grid(True)
    axs[0].legend()

    axs[1].plot(system_df["tick"], system_df["waiting_tasks"], label="Wartend", color="orange")
    axs[1].plot(system_df["tick"], system_df["running_tasks"], label="Laufend", color="green")
    axs[1].plot(system_df["tick"], system_df["total_tasks"], label="Gesamt", color="red", linestyle="--")
    axs[1].set_ylabel("Tasks")
    axs[1].set_xlabel("Ticks")
    axs[1].set_title("Tasks über die Zeit")
    axs[1].grid(True)
    axs[1].legend()

    plt.tight_layout()
    plt.show()


# Hauptprogramm
if __name__ == "__main__":
    history, nodes, util_df, sched_time_df, system_df = run_simulation()
    plot_schedule(history, len(nodes))
    plot_utilization(nodes)  # Endzustand
    plot_utilization_over_time(util_df)  # Verlauf der Ressourcen
    plot_scheduling_time(sched_time_df)  # Schedulingzeit pro Tick
    plot_system_log(system_df)  # Nodes & Tasks über Zeit
    export_to_csv(history)
