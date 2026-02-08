"""Oracle interface for on-chain publication"""
import json
import hashlib
from datetime import datetime, timezone

def create_trace(index, p, q, score_p, score_q, verified):
    """Create an oracle trace record for on-chain publication."""
    trace = {
        'version': '1.0.0',
        'index': index,
        'p': str(p),
        'q': str(q),
        'score_p': score_p,
        'score_q': score_q,
        'verified': verified,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    # Compute trace hash for integrity
    trace_data = f"{index}:{p}:{q}:{score_p}:{score_q}:{verified}"
    trace['hash'] = hashlib.sha256(trace_data.encode()).hexdigest()
    return trace

def format_for_contract(trace):
    """Format trace data for Ethereum smart contract submission.
    Returns tuple suitable for contract call.
    """
    return (
        trace['index'],
        int(trace['p']),
        int(trace['q']),
        int(trace['score_p'] * 10000),  # Fixed point (4 decimals)
        int(trace['score_q'] * 10000),
        trace['verified'],
        bytes.fromhex(trace['hash']),
    )

def export_traces(traces, filepath):
    """Export traces to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(traces, f, indent=2, default=str)
