import random
import matplotlib.pyplot as plt
import itertools
import copy
import time
from adjustText import adjust_text

# ---------------- Datenstrukturen ----------------
class Node:
    def __init__(self, id, cpu, memory, storage):
        self.id = id
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
        self.tasks = []

    def clone(self):
        return Node(self.id, self.cpu, self.memory, self.storage)

class Task:
    def __init__(self, id, cpu, memory, storage, value):
        self.id = id
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
        self.value = value

    def efficiency(self):
        total = self.cpu + self.memory + self.storage
        return self.value / total if total > 0 else 0

# ---------------- Initialisierung ----------------
# Beispielhafte Nodes
base_nodes = [
    Node("Node-A", cpu=5, memory=10, storage=40),
    Node("Node-B", cpu=5, memory=10, storage=40),
    Node("Node-C", cpu=5, memory=10, storage=40),
    Node("Node-D", cpu=5, memory=10, storage=40)
]

# Beispielhafte Tasks (kleine Menge!)
tasks = []
for i in range(10):
    cpu = random.randint(1, 3)
    memory = random.randint(2, 4)
    storage = random.randint(5, 10)
    value = random.randint(10, 50)
    tasks.append(Task(f"Task-{i}", cpu, memory, storage, value))

# ---------------- Greedy-Scheduling ----------------
def greedy_schedule(tasks, nodes):
    nodes = [node.clone() for node in nodes]
    tasks_sorted = sorted(tasks, key=lambda t: t.efficiency(), reverse=True)

    for task in tasks_sorted:
        for node in nodes:
            if (node.cpu >= task.cpu and node.memory >= task.memory and node.storage >= task.storage):
                node.cpu -= task.cpu
                node.memory -= task.memory
                node.storage -= task.storage
                node.tasks.append(task)
                break
    return nodes

# ---------------- Optimale Verteilung (Brute Force) ----------------
def optimal_schedule_bruteforce(tasks, nodes):
    best_nodes = None
    best_value = 0
    all_assignments = itertools.product(range(len(nodes) + 1), repeat=len(tasks))  # +1 = "nicht zugewiesen"

    for assignment in all_assignments:
        temp_nodes = [node.clone() for node in nodes]
        valid = True
        total_value = 0

        for i, node_idx in enumerate(assignment):
            if node_idx == len(nodes):  # Aufgabe nicht zugewiesen
                continue
            task = tasks[i]
            node = temp_nodes[node_idx]
            if (node.cpu >= task.cpu and node.memory >= task.memory and node.storage >= task.storage):
                node.cpu -= task.cpu
                node.memory -= task.memory
                node.storage -= task.storage
                node.tasks.append(task)
                total_value += task.value
            else:
                valid = False
                break

        if valid and total_value > best_value:
            best_value = total_value
            best_nodes = copy.deepcopy(temp_nodes)

    return best_nodes

# ---------------- Gesamtauslastung berechnen ----------------
def calculate_total_efficiency(nodes, original_nodes):
    total_used = {'cpu': 0, 'memory': 0, 'storage': 0}
    total_capacity = {'cpu': 0, 'memory': 0, 'storage': 0}
    resources = ['cpu', 'memory', 'storage']

    for node, orig in zip(nodes, original_nodes):
        for res in resources:
            used = sum(getattr(t, res) for t in node.tasks)
            cap = getattr(orig, res)
            total_used[res] += used
            total_capacity[res] += cap

    efficiencies = {res: (total_used[res] / total_capacity[res] if total_capacity[res] else 0)
                    for res in resources}
    overall_efficiency = sum(efficiencies.values()) / len(resources)
    return overall_efficiency, efficiencies

# ---------------- Visualisierung ----------------
def plot_result(nodes_greedy, nodes_optimal):
    fig, axs = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [2, 2]})
    colors = ['red', 'blue', 'green']
    resources = ['cpu', 'memory', 'storage']

    def plot_nodes(ax, nodes, title):
        texts = []
        for idx, node in enumerate(nodes):
            y = [idx] * len(node.tasks)
            x = [task.value for task in node.tasks]
            labels = [task.id for task in node.tasks]

            ax.scatter(x, y, color=colors[idx % len(colors)], label=node.id, s=100)

            for i, label in enumerate(labels):
                text = ax.text(x[i] + 0.2, y[i] + 0.1, label, ha='center', fontsize=8)
                texts.append(text)

        adjust_text(
        texts,
        ax=ax,
        only_move={'points': 'y', 'text': 'y'},
        force_text=1.5,
        force_points=2.0,
        expand_text=(1.2, 1.2),
        expand_points=(1.2, 1.2),
        arrowprops=dict(arrowstyle='-', color='gray', lw=0.5)
        )

        ax.set_yticks(range(len(nodes)))
        ax.set_yticklabels([node.id for node in nodes])
        ax.set_title(title)
        ax.set_ylabel("Nodes")
        ax.set_ylim(-1, len(nodes))
        ax.grid(True)
        ax.legend(loc='upper right')  # optional: Position der Legende

    def plot_utilization(ax, nodes, original_nodes, title):
        width = 0.2
        bar_positions = list(range(len(nodes)))
        resources = ['cpu', 'memory', 'storage']
        colors_local = ['tab:blue', 'tab:orange', 'tab:green', 'gray']  # letzte = Gesamt

        # Ressourcenbalken pro Node
        for r_idx, resource in enumerate(resources):
            used = []
            for node, orig in zip(nodes, original_nodes):
                used_val = sum(getattr(t, resource) for t in node.tasks)
                total_val = getattr(orig, resource)
                used.append(used_val / total_val if total_val else 0)
            ax.bar(
                [p + r_idx * width for p in bar_positions],
                used, width=width, label=resource.capitalize(), color=colors_local[r_idx]
            )
            for i, val in enumerate(used):
                x_pos = bar_positions[i] + r_idx * width
                ax.text(x_pos, val + 0.02, f"{val:.2f}", ha='center', va='bottom', fontsize=8)

        # === Gesamtauslastung über alle Nodes hinweg ===
        total_node_efficiencies = []
        for idx, node in enumerate(nodes):
            local_sum = 0
            for res in resources:
                used_val = sum(getattr(t, res) for t in node.tasks)
                total_val = getattr(original_nodes[idx], res)
                if total_val:
                    local_sum += used_val / total_val
            avg_eff = local_sum / len(resources)
            total_node_efficiencies.append(avg_eff)

        overall_efficiency = sum(total_node_efficiencies) / len(total_node_efficiencies)

        # Position des Gesamt-Balkens (rechts von den Nodes)
        overall_x = len(nodes) + 0.5
        ax.bar(
            [overall_x],
            [overall_efficiency],
            width=width,
            color=colors_local[-1],
            label='Gesamt'
        )
        ax.text(overall_x, overall_efficiency + 0.02, f"{overall_efficiency:.2f}", 
            ha='center', va='bottom', fontsize=8)

        # Achsenformatierung
        ax.set_title(title)
        ax.set_ylabel("Auslastung (0–1)")
        ax.set_xticks([p + width for p in bar_positions] + [overall_x])
        ax.set_xticklabels([node.id for node in nodes] + ["Gesamt"])
        ax.set_ylim(0, 1.1)
        ax.legend(loc='lower right')
        ax.grid(True)

    # Oben: Task-Zuweisung
    # plot_nodes(axs[0][0], nodes_greedy, "Greedy Lösung")
    # plot_nodes(axs[0][1], nodes_optimal, "Optimale Lösung")

    # Unten: Ressourcenauslastung
    plot_utilization(axs[0], nodes_greedy, base_nodes, "Greedy Ressourcenauslastung")
    plot_utilization(axs[1], nodes_optimal, base_nodes, "Optimale Ressourcenauslastung")

    plt.tight_layout()
    plt.show()

def plot_runtime_comparison(greedy_time, optimal_time):
    plt.figure(figsize=(6, 3))
    names = ['Greedy', 'Optimal']
    times = [greedy_time, optimal_time]
    bars = plt.bar(names, times, color=['blue', 'orange'])
    for bar, t in zip(bars, times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{t:.4f}s", 
                    ha='center', va='bottom')
    plt.ylabel("Rechenzeit (s)")
    plt.title("Vergleich der Laufzeiten")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()

# ---------------- Ausführung ----------------
start_greedy = time.perf_counter()
greedy_nodes = greedy_schedule(tasks, base_nodes)
end_greedy = time.perf_counter()
greedy_time = end_greedy - start_greedy
print(greedy_time)

start_optimal = time.perf_counter()
optimal_nodes = optimal_schedule_bruteforce(tasks, base_nodes)
end_optimal = time.perf_counter()
optimal_time = end_optimal - start_optimal
print(optimal_time)

plot_result(greedy_nodes, optimal_nodes)
plot_runtime_comparison(greedy_time, optimal_time)
