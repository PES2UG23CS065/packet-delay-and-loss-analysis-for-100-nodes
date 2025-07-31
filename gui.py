import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import os

# Function to calculate metrics from the trace file
def analyze_trace_file(trace_file):
    sent_packets = {}
    received_packets = {}
    dropped_packets = 0
    delays = []
    tcp_count = 0
    udp_count = 0

    with open(trace_file, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) < 12:
                continue

            event = parts[0]
            time = float(parts[1])
            packet_type = parts[4]
            packet_id = parts[11]

            if packet_type not in ["cbr", "tcp"]:
                continue

            if event == "+":
                sent_packets[packet_id] = time
            elif event == "r" and packet_id in sent_packets:
                delay = time - sent_packets[packet_id]
                delays.append(delay)
                received_packets[packet_id] = time

                if packet_type == "tcp":
                    tcp_count += 1
                elif packet_type == "cbr":
                    udp_count += 1
            elif event == "d":
                dropped_packets += 1

    total_sent = len(sent_packets)
    total_received = len(received_packets)
    total_lost = total_sent - total_received
    loss_percent = (total_lost / total_sent) * 100 if total_sent > 0 else 0
    average_delay = sum(delays) / len(delays) if delays else 0

    # ✅ Updated Jitter Calculation
    jitter = 0
    if len(delays) > 1:
        jitter_values = [abs(delays[i] - delays[i - 1]) for i in range(1, len(delays))]
        jitter = sum(jitter_values) / len(jitter_values)

    duration = max(received_packets.values()) - min(sent_packets.values()) if received_packets else 1
    throughput = ((total_received * 512 * 8) / duration) / (1024 * 1024)

    return {
        "sent": total_sent,
        "received": total_received,
        "lost": total_lost,
        "loss_percent": round(loss_percent, 2),
        "delay": round(average_delay * 1000, 2),
        "jitter": round(jitter * 1000, 2),
        "throughput": round(throughput, 2),
        "duration": round(duration, 2),
        "dropped": dropped_packets,
        "tcp": tcp_count,
        "udp": udp_count
    }, delays

# Plot packet delay over time
def plot_graphs(delays):
    plt.figure(figsize=(8, 5))
    plt.plot(range(len(delays)), [d * 1000 for d in delays], marker='o', linestyle='-')
    plt.title("Packet Delay Over Time")
    plt.xlabel("Packet Number")
    plt.ylabel("Delay (ms)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Pie chart of TCP vs UDP
def show_pie_chart(tcp, udp):
    labels = ['TCP', 'UDP']
    sizes = [tcp, udp]
    colors = ['skyblue', 'lightcoral']
    explode = (0.1, 0)

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title("TCP vs UDP Packet Distribution")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# Bar chart of Packet Loss vs Sent
def plot_packet_loss_vs_sent(data):
    sent = data["sent"]
    lost = data["lost"]
    labels = ["Sent", "Lost"]
    values = [sent, lost]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=["green", "red"])
    plt.title("Packet Loss vs Sent")
    plt.ylabel("Packet Count")
    plt.tight_layout()
    plt.show()

# GUI Application
def start_gui():
    def open_file():
        file_path = filedialog.askopenfilename(filetypes=[("Trace Files", "*.tr")])
        if file_path:
            result, delays = analyze_trace_file(file_path)
            display_results(result)
            plot_graphs(delays)
            show_pie_chart(result["tcp"], result["udp"])
            plot_packet_loss_vs_sent(result)

    def display_results(data):
        result_text.set(
            f"Packets Sent: {data['sent']}\n"
            f"Packets Received: {data['received']}\n"
            f"Packets Lost: {data['lost']} ({data['loss_percent']}%)\n"
            f"Packets Dropped: {data['dropped']}\n"
            f"Average Delay: {data['delay']} ms\n"
            f"Jitter: {data['jitter']} ms\n"
            f"Throughput: {data['throughput']} Mbps\n"
            f"Simulation Time: {data['duration']} sec"
        )

    root = tk.Tk()
    root.title("NS2 Packet Analyzer")

    tk.Label(root, text="NS2 Trace File Analyzer", font=("Helvetica", 16, "bold")).pack(pady=10)
    tk.Button(root, text="Open Trace File (.tr)", command=open_file, font=("Helvetica", 12)).pack(pady=10)

    result_text = tk.StringVar()
    result_label = tk.Label(root, textvariable=result_text, font=("Courier", 12), justify="left")
    result_label.pack(pady=10)

    root.mainloop()

# Correct main block
if _name_ == "_main_":
    start_gui()
