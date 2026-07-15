#!/bin/bash
echo "Position | Total TCP | Retransmissions | Loss Rate (%)"
echo "------------------------------------------------------"

for f in position*.pcapng; do
    total=$(tshark -r "$f" -Y "tcp" 2>/dev/null | wc -l)
    retr=$(tshark -r "$f" -Y "tcp.analysis.retransmission" 2>/dev/null | wc -l)
    
    # Avoid division by zero
    if [ "$total" -gt 0 ]; then
        loss=$(echo "scale=2; ($retr * 100) / $total" | bc)
    else
        loss=0
    fi
    
    printf "%-8s | %-9s | %-15s | %s%%\n" "$f" "$total" "$retr" "$loss"
done
