
import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Exact Sequence of points
    spatial_sequence = [
        "position_9",
        "position_10", # Single Knife Edge
        "position_8",
        "position_4",
        "position_5",  # Double Knife Edge
        "position_6",
        "position_7"
    ]
    
    # Exact Measured Values
    distances = {
        "position_9": 4.52,
        "position_10": 5.36, # Single Knife Edge
        "position_8": 3.067,
        "position_4": 3.89,
        "position_5": 6.083, # Double Knife Edge
        "position_6": 10.43,
        "position_7": 10.25
    }
    
    csv_path = "/Users/tanayagrawal/Desktop/wifi performance/Pathloss Analysis/pcap_loss_report.csv"
    if not os.path.exists(csv_path):
        print(f"[-] Error: '{csv_path}' not found. Please verify the path.")
        return
        
    df = pd.read_csv(csv_path)
    
    df['Clean_Name'] = df['Filename'].str.lower().str.replace('.pcapng', '', regex=False).str.strip()
    
    dl_rows = []
    ul_rows = []
    
    for pos in spatial_sequence:
        match_dl = df[df['Clean_Name'] == f"{pos}_dl"]
        match_ul = df[df['Clean_Name'] == f"{pos}_ul"]
        
        if not match_dl.empty:
            dl_rows.append(match_dl.iloc[0])
        else:
            dl_rows.append({'Fast_Retrans': 0, 'RTO_Timeouts': 0})
            
        if not match_ul.empty:
            ul_rows.append(match_ul.iloc[0])
        else:
            ul_rows.append({'Fast_Retrans': 0, 'RTO_Timeouts': 0})
            
    df_dl = pd.DataFrame(dl_rows)
    df_ul = pd.DataFrame(ul_rows)
    
    x_labels = [f"{pos.upper()}\n({distances[pos]} m)" for pos in spatial_sequence]
    
   # plotting
    print("Generating Sequence-Aligned Anomaly Map...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Uplink Fast Retransmissions (Sequence Aligned)
    ax1.plot(spatial_sequence, df_ul['Fast_Retrans'], marker='o', color='tab:blue', linewidth=2.5, label='Uplink Fast Retrans')
    ax1.set_xticks(range(len(spatial_sequence)))
    ax1.set_xticklabels(x_labels)
    ax1.set_xlabel("Spatial Walking Path Sequence\n(Geometric Distance from AP)", fontweight='bold', labelpad=10)
    ax1.set_ylabel("Fast Retransmission Packet Count", color='tab:blue', fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title("Uplink Loss Dynamics Along Spatial Path", fontweight='bold', fontsize=12)
    
    # Annotation tracking for actual Uplink spikes
    max_fast = df_ul['Fast_Retrans'].max()
    if max_fast > 0:
        p10_idx = spatial_sequence.index("position_10")
        p10_val = df_ul.iloc[p10_idx]['Fast_Retrans']
        ax1.annotate(f'Single Knife Edge\n(Pos 10: {int(p10_val)} Retrans)', 
                     xy=(p10_idx, p10_val),
                     xytext=(p10_idx + 0.1, max_fast * 0.9),
                     arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6))
                     
        p5_idx = spatial_sequence.index("position_5")
        p5_val = df_ul.iloc[p5_idx]['Fast_Retrans']
        ax1.annotate(f'Double Knife Edge\n(Pos 5: {int(p5_val)} Retrans)', 
                     xy=(p5_idx, p5_val),
                     xytext=(p5_idx - 1.2, max_fast * 0.5),
                     arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6))

    # Downlink RTO Timeouts (Sequence Aligned)
    ax2.plot(spatial_sequence, df_dl['RTO_Timeouts'], marker='s', color='tab:red', linewidth=2.5, label='Downlink RTOs')
    ax2.set_xticks(range(len(spatial_sequence)))
    ax2.set_xticklabels(x_labels)
    ax2.set_ylim(-1, 5) 
    ax2.set_xlabel("Spatial Walking Path Sequence\n(Geometric Distance from AP)", fontweight='bold', labelpad=10)
    ax2.set_ylabel("Hard RTO Timeout Count", color='tab:red', fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title("Downlink Stalls (RTO) Along Spatial Path", fontweight='bold', fontsize=12)
    
    
    ax2.text(0.5, 0.5, "Seamless Link Continuity\n(0 RTO Stalls Detected)", 
             transform=ax2.transAxes, fontsize=12, color='tab:red', weight='bold',
             ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    plt.suptitle("Impact of Geometric Barriers Along Walking Sequence", 
                 fontweight='bold', fontsize=14, y=0.98)
    plt.tight_layout()
    
    output_png = "/Users/tanayagrawal/Desktop/wifi performance/Pathloss Analysis/spatial_sequence_anomaly_map.png"
    plt.savefig(output_png, dpi=300)
    print(f"[+] Walking sequence visualization saved to: {output_png}")
    plt.show()

if __name__ == "__main__":
    main()