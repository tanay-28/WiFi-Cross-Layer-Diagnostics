
## Analysis Modules

### 1. **Pathloss Analysis** (`Pathloss Analysis/`)
Analyzes the relationship between spatial position and TCP-layer packet loss. Correlates geometric distance and line-of-sight obstructions with fast retransmission and RTO timeout rates.

- **Input**: PCAP files at different spatial positions (`position_X_DL.pcapng`, `position_X_UL.pcapng`)
- **Output**: Sequence-aligned loss anomaly visualization
- **Key Metrics**: Fast Retransmission count, RTO Timeout count vs. distance

### 2. **Throughput Analysis** (`Throughput Analysis/`)
Measures downlink and uplink throughput degradation across spatial positions using iperf terminal logs and PCAP analysis.

- **Input**: iperf output files (`.rtf`) and PCAP captures
- **Output**: `wireless_performance_master.csv` with DL/UL throughput and retransmission percentages
- **Key Metrics**: Mbps throughput, Retransmission percentage

### 3. **BDP Analysis** (`BDP/`)
Calculates Bandwidth-Delay Product to identify TCP window constraints and their interaction with loss-induced queue buildup.

- **Input**: PCAP files and iperf logs
- **Output**: BDP metrics with window size constraints
- **Key Metrics**: BDP in bytes, optimal window size, congestion window behavior

### 4. **Bufferbloat Analysis** (`bufferbloat/`)
Stress tests the WiFi link under simultaneous bidirectional load to detect buffer-induced latency spikes.

- **Input**: Ping terminal output, stress test iperf logs
- **Output**: Latency statistics, jitter analysis, bufferbloat severity profile
- **Key Metrics**: Min/Max/Avg latency (ms), Jitter, Goodput under stress

### 5. **Retransmission Analysis** (`retransmission analysis/`)
Deep packet inspection using tshark to classify TCP loss events into fast retransmits vs. RTO-triggered events.

- **Input**: PCAP files (`.pcapng`)
- **Output**: `pcap_loss_report.csv` with loss classification
- **Key Metrics**: Total TCP packets, Fast Retrans count, RTO count, Loss Rate %

### 6. **Advanced Metrics** (`Advanced Metrics/`)
Native Python packet parsing using Scapy to extract transport-layer metrics directly from PCAP without external tool dependencies.

- **Input**: PCAP files
- **Output**: Per-packet throughput, RTT estimation, payload analysis
- **Key Metrics**: Goodput (Mbps), Average RTT (ms)

## Dependencies

### Required
- Python 3.7+
- `pandas` - Data analysis and CSV generation
- `matplotlib` - Visualization
- `scapy` - Native PCAP parsing (for Advanced Metrics)
- `tshark` (Wireshark) - Packet filtering and analysis
- `bc` - Bash calculator (for analyze.sh)

### Optional
- iperf3 - Throughput testing (for measurement capture)
- Wireshark GUI - Manual PCAP inspection

### Installation

```bash
# macOS (Homebrew)
brew install wireshark python3

# Python dependencies
pip install pandas matplotlib scapy

# For Linux/Ubuntu
sudo apt-get install tshark python3-pandas python3-matplotlib
pip install scapy
