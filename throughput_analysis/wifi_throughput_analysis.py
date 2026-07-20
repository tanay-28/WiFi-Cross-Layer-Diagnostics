import os
import subprocess
import re
import pandas as pd
import matplotlib.pyplot as plt


NUM_POSITIONS = 10
DATA_DIR = "/Users/tanayagrawal/Desktop/wifi_performance/captured_data"  
results = []

def get_retransmission_rate(pcap_path):
    if not os.path.exists(pcap_path):
        print(f"Warning: File not found: {pcap_path}")
        return 0.0
    
    # Extract
    cmd_total = f"tshark -r \"{pcap_path}\" -Y \"tcp.port == 5201\" -T fields -e frame.number 2>/dev/null | wc -l"
    cmd_retrans = f"tshark -r \"{pcap_path}\" -Y \"tcp.port == 5201 && tcp.analysis.retransmission\" -T fields -e frame.number 2>/dev/null | wc -l"
    
    try:
        total = int(subprocess.check_output(cmd_total, shell=True).decode().strip())
        retrans = int(subprocess.check_output(cmd_retrans, shell=True).decode().strip())
        return (retrans / total) * 100 if total > 0 else 0.0
    except Exception as e:
        print(f"Error parsing pcap {pcap_path}: {e}")
        return 0.0

def parse_iperf_terminal(txt_path):
    
    if not os.path.exists(txt_path):
        print(f"Warning: Text log not found: {txt_path}")
        return 0.0
    with open(txt_path, 'r') as f:
        content = f.read()
    
    # Matches the average summary lines at the very bottom (handles both sender and receiver)
    matches = re.findall(r'([\d\.]+)\s+Mbits/sec\s+(?:sender|receiver)', content)
    if matches:
        return float(matches[-1]) # Extracts the last matching summary number
    
    # Fallback: Extract the final absolute numeric value preceding Mbits/sec if layout varies
    matches_alt = re.findall(r'([\d\.]+)\s+Mbits/sec', content)
    return float(matches_alt[-1]) if matches_alt else 0.0

custom_positions = [9, 10, 8, 4, 5, 6, 7]

for pos in custom_positions:
    # Construct exact path mappings
    dl_pcap = os.path.join(DATA_DIR, f"position_{pos}_DL.pcapng")
    dl_txt = os.path.join(DATA_DIR, f"position_{pos}_DL.rtf")
    ul_pcap = os.path.join(DATA_DIR, f"position_{pos}_UL.pcapng")
    ul_txt = os.path.join(DATA_DIR, f"position_{pos}_UL.rtf")
    
    # Extract data metrics
    dl_throughput = parse_iperf_terminal(dl_txt)
    ul_throughput = parse_iperf_terminal(ul_txt)
    dl_retrans = get_retransmission_rate(dl_pcap)
    ul_retrans = get_retransmission_rate(ul_pcap)
    
    results.append({
        "Position": pos,
        "DL_Throughput_Mbps": dl_throughput,
        "UL_Throughput_Mbps": ul_throughput,
        "DL_Retrans_Percent": dl_retrans,
        "UL_Retrans_Percent": ul_retrans
    })

# Convert to DataFrame and save
df = pd.DataFrame(results)
df.to_csv("wireless_performance_master.csv", index=False)
print("\n=== Data Processing Complete! Saved to wireless_performance_master.csv ===")
print(df.to_string(index=False))

# plotting
try:
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Create an artificial left-to-right spacing array (0, 1, 2, 3...)
    x_indices = range(len(df)) 

    color = 'tab:blue'
    ax1.set_xlabel('Spatial Walking Path (Physical Order)', fontweight='bold')
    ax1.set_ylabel('Throughput (Mbps)', color=color, fontweight='bold')
    
    # Plot using our clean 0, 1, 2 indices instead of the out-of-order numbers
    ax1.plot(x_indices, df['DL_Throughput_Mbps'], color=color, marker='o', linewidth=2, label='DL Throughput')
    ax1.plot(x_indices, df['UL_Throughput_Mbps'], color='tab:cyan', marker='^', linestyle=':', linewidth=2, label='UL Throughput')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    custom_labels = [f"Pos {p}" for p in df['Position']]
    plt.xticks(x_indices, custom_labels, fontweight='bold')
    ax1.legend(loc='upper left')

    # Right Axis: Retransmissions
    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('TCP Retransmission Rate (%)', color=color, fontweight='bold')
    ax2.plot(x_indices, df['DL_Retrans_Percent'], color=color, marker='s', linestyle='--', linewidth=2, label='DL Retransmissions')
    ax2.plot(x_indices, df['UL_Retrans_Percent'], color='orange', marker='d', linestyle='-.', linewidth=1.5, label='UL Retransmissions')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc='upper right')

    plt.title('Throughput vs. Retransmissions Along the Measurement Path', fontsize=12, fontweight='bold', pad=15)
    fig.tight_layout()
    
    plt.savefig("cross_layer_analysis.png", dpi=300)
    print("\nGraph successfully saved to: cross_layer_analysis.png")
    plt.show()

except Exception as plot_error:
    print(f"\nData saved to CSV, but plotting failed: {plot_error}")

# --- GENERATE 4 SEPARATE STANDALONE PLOTS ---
try:
    x_indices = range(len(df))
    custom_labels = [f"Pos {p}" for p in df['Position']]
    
    # ----------------------------------------------------
    # Plot 1: Downlink Throughput Standalone
    # ----------------------------------------------------
    plt.figure(figsize=(8, 4.5))
    plt.plot(x_indices, df['DL_Throughput_Mbps'], color='tab:blue', marker='o', linewidth=2.5, label='DL Throughput')
    plt.xticks(x_indices, custom_labels, fontweight='bold')
    plt.xlabel('Spatial Walking Path', fontweight='bold')
    plt.ylabel('Throughput (Mbps)', fontweight='bold')
    plt.title('Downlink Throughput Profile Along Path', fontsize=11, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("plot_1_dl_throughput.png", dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Plot 2: Uplink Throughput Standalone
    # ----------------------------------------------------
    plt.figure(figsize=(8, 4.5))
    plt.plot(x_indices, df['UL_Throughput_Mbps'], color='tab:cyan', marker='^', linestyle='-', linewidth=2.5, label='UL Throughput')
    plt.xticks(x_indices, custom_labels, fontweight='bold')
    plt.xlabel('Spatial Walking Path', fontweight='bold')
    plt.ylabel('Throughput (Mbps)', fontweight='bold')
    plt.title('Uplink Throughput Profile Along Path', fontsize=11, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("plot_2_ul_throughput.png", dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Plot 3: Downlink Retransmission Rate Standalone
    # ----------------------------------------------------
    plt.figure(figsize=(8, 4.5))
    plt.plot(x_indices, df['DL_Retrans_Percent'], color='tab:red', marker='s', linestyle='--', linewidth=2.5, label='DL Retransmissions')
    plt.xticks(x_indices, custom_labels, fontweight='bold')
    plt.xlabel('Spatial Walking Path', fontweight='bold')
    plt.ylabel('TCP Retransmission Rate (%)', fontweight='bold')
    plt.title('Downlink TCP Retransmission Analysis', fontsize=11, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("plot_3_dl_retransmissions.png", dpi=300)
    plt.close()

    # ----------------------------------------------------
    # Plot 4: Uplink Retransmission Rate Standalone
    # ----------------------------------------------------
    plt.figure(figsize=(8, 4.5))
    plt.plot(x_indices, df['UL_Retrans_Percent'], color='orange', marker='d', linestyle='-.', linewidth=2.5, label='UL Retransmissions')
    plt.xticks(x_indices, custom_labels, fontweight='bold')
    plt.xlabel('Spatial Walking Path', fontweight='bold')
    plt.ylabel('TCP Retransmission Rate (%)', fontweight='bold')
    plt.title('Uplink TCP Retransmission Analysis', fontsize=11, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("plot_4_ul_retransmissions.png", dpi=300)
    plt.close()

    print("\n=== All 4 individual plots generated successfully! ===")
    print("1. plot_1_dl_throughput.png")
    print("2. plot_2_ul_throughput.png")
    print("3. plot_3_dl_retransmissions.png")
    print("4. plot_4_ul_retransmissions.png")

except Exception as batch_plot_error:
    print(f"\nBatch processing failed for individual plots: {batch_plot_error}")


   