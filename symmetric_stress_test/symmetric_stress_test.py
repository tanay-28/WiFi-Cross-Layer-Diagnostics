import matplotlib
matplotlib.use('Agg')  # Headless mode for clean execution

from scapy.all import PcapReader, IP, TCP
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Configuration ---
PCAP_FILE = "/Users/tanayagrawal/Desktop/wifi_performance/symmetric_stress.pcapng"
HOST_IP = "192.168.1.60"   # Your MacBook Client
SERVER_IP = "192.168.1.50" # Your Fixed PC Server

# Tracking independent data profiles directly
metrics = {
    HOST_IP: {"upload": 0, "download": 0},
    SERVER_IP: {"upload": 0, "download": 0}
}

def analyze_pcap():
    print(f"📦 Streaming deep-layer packet analysis for: '{PCAP_FILE}'...")
    
    if not os.path.exists(PCAP_FILE):
        print(f"❌ Error: File not found at {PCAP_FILE}")
        return

    packet_count = 0

    with PcapReader(PCAP_FILE) as pcap_stream:
        for pkt in pcap_stream:
            packet_count += 1
            if packet_count % 50000 == 0:
                print(f"   ⏱️  Processed {packet_count} packets...", flush=True)

            if IP in pkt and TCP in pkt:
                ip_layer = pkt[IP]
                src = ip_layer.src
                dst = ip_layer.dst
                pkt_len = len(pkt)

                # --- MacBook Perspective (.60) ---
                if src == HOST_IP:
                    metrics[HOST_IP]["upload"] += pkt_len
                elif dst == HOST_IP:
                    metrics[HOST_IP]["download"] += pkt_len

                # --- Server Perspective (.50) ---
                if src == SERVER_IP:
                    metrics[SERVER_IP]["upload"] += pkt_len
                elif dst == SERVER_IP:
                    metrics[SERVER_IP]["download"] += pkt_len

    generate_dual_station_plots()

def generate_dual_station_plots():
    print("\n📊 Generating Device-Centric Asymmetry Profiles...")
    
    # Convert tracked raw bytes into Megabytes
    host_up = metrics[HOST_IP]["upload"] / (1024 * 1024)
    host_down = metrics[HOST_IP]["download"] / (1024 * 1024)
    
    server_up = metrics[SERVER_IP]["upload"] / (1024 * 1024)
    server_down = metrics[SERVER_IP]["download"] / (1024 * 1024)

    # Compile structured dataframes for side-by-side distribution mapping
    df_host = pd.DataFrame({
        'Direction': ['Upload (Sent)', 'Download (Received)'],
        'Megabytes': [host_up, host_down]
    })

    df_server = pd.DataFrame({
        'Direction': ['Upload (Sent)', 'Download (Received)'],
        'Megabytes': [server_up, server_down]
    })

    # Initialize plotting environment
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Bidirectional iPerf3: Device Telemetry Asymmetry Profile", fontsize=15, fontweight="bold")

    # --- LEFT PLOT: MacBook Client View ---
    sns.barplot(
        x="Direction", 
        y="Megabytes", 
        data=df_host, 
        ax=axes[0], 
        hue="Direction",
        palette=["#e76f51", "#2a9d8f"],
        legend=False
    )
    axes[0].set_title(f"💻 MacBook Client Profile\nLocal IP: {HOST_IP}", fontsize=12, fontweight="semibold")
    axes[0].set_ylabel("Data Transferred (MB)")
    axes[0].set_xlabel("")

    # --- RIGHT PLOT: Fixed PC Server View ---
    sns.barplot(
        x="Direction", 
        y="Megabytes", 
        data=df_server, 
        ax=axes[1], 
        hue="Direction",
        palette=["#e76f51", "#2a9d8f"],
        legend=False
    )
    axes[1].set_title(f"🖥️ Fixed PC Server Profile\nTarget IP: {SERVER_IP}", fontsize=12, fontweight="semibold")
    axes[1].set_ylabel("")
    axes[1].set_xlabel("")

    plt.tight_layout()
    output_name = "device_centric_throughput.png"
    plt.savefig(output_name, dpi=300)
    print(f"\n💾 Dashboard saved successfully as '{output_name}'")
    os.system(f"open '{output_name}'")

if __name__ == "__main__":
    analyze_pcap()