#!/usr/bin/env python3
import os
import glob
import subprocess
import pandas as pd

def run_tshark_count(pcap_path, display_filter):
    """Calls tshark via standard terminal subprocess to get a clean packet count."""
    # Look for common tshark paths on macOS
    tshark_path = "tshark"
    if not os.path.exists("/usr/local/bin/tshark") and os.path.exists("/Applications/Wireshark.app/Contents/MacOS/tshark"):
        tshark_path = "/Applications/Wireshark.app/Contents/MacOS/tshark"

    cmd = [
        tshark_path,
        "-r", pcap_path,
        "-Y", display_filter,
        "-T", "fields",
        "-e", "frame.number"
    ]
    
    try:
        # Run tshark, capture the text output, and count the lines (frames)
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        count = len([l for l in lines if l])
        return count
    except subprocess.CalledProcessError as e:
        print(f"Error executing tshark command: {e.stderr}")
        return 0
    except FileNotFoundError:
        print("[-] Error: tshark binary not found. Please install Wireshark or verify your path.")
        return 0

def analyze_pcap_loss_dynamics(pcap_path):
    print(f"Processing: {os.path.basename(pcap_path)}...")
    
    # Define our target Wireshark filters
    total_filter = "tcp"
    fast_filter  = "tcp.analysis.fast_retransmission"
    rto_filter   = "tcp.analysis.retransmission && !tcp.analysis.fast_retransmission"
    
    total_count = run_tshark_count(pcap_path, total_filter)
    if total_count == 0:
        return {"Total_TCP": 0, "Fast_Retrans": 0, "RTO_Timeouts": 0, "Loss_Rate_%": 0.0}
        
    fast_count = run_tshark_count(pcap_path, fast_filter)
    rto_count = run_tshark_count(pcap_path, rto_filter)
    
    total_loss_packets = fast_count + rto_count
    loss_rate = (total_loss_packets * 100.0) / total_count
    
    return {
        "Total_TCP": total_count,
        "Fast_Retrans": fast_count,
        "RTO_Timeouts": rto_count,
        "Loss_Rate_%": round(loss_rate, 2)
    }

def main():
    pcap_files = sorted(glob.glob("*.pcapng"))
    
    if not pcap_files:
        print(f"No .pcapng files found in: {os.getcwd()}")
        return

    results = []
    for file_path in pcap_files:
        stats = analyze_pcap_loss_dynamics(file_path)
        if stats:
            stats["Filename"] = os.path.basename(file_path)
            results.append(stats)
            
    df = pd.DataFrame(results)
    df = df[["Filename", "Total_TCP", "Fast_Retrans", "RTO_Timeouts", "Loss_Rate_%"]]
    
    print("\n========================================================")
    print("      LAYER 4 LOSS METRIC ANALYSIS REPORT")
    print("========================================================\n")
    print(df.to_string(index=False))
    print("\n========================================================\n")
    
    df.to_csv("pcap_loss_report.csv", index=False)
    print("[+] Report exported successfully to 'pcap_loss_report.csv'")

if __name__ == "__main__":
    main()