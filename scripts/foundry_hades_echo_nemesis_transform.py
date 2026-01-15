# Foundry Transform: Hades/Echo/Nemesis Compilation
# Simple transform to process abc_output through Hades/Echo/Nemesis and generate "the concept"

import json
import pandas as pd

from src.verticals.ai_verification.core.nemesis.foundry_integration.foundry_compilation_transform import (
    compile_from_verified_hashes
)


def transform(abc_output):
    """
    Process abc_output through Hades/Echo/Nemesis to generate the concept.
    """
    # Convert DataFrame rows to list of dicts
    input_data = abc_output.to_dict('records')

    # Convert block data to verified hash format for compilation
    verified_hashes = []
    for row in input_data:
        # Parse transactions JSON if it's a string
        transactions_json = row.get('transactions', '[]')
        if isinstance(transactions_json, str):
            try:
                transactions = json.loads(transactions_json)
            except (json.JSONDecodeError, ValueError):
                transactions = []
        else:
            transactions = transactions_json if isinstance(transactions_json, list) else []

        # Create verified hash record for each transaction or block
        verified_hashes.append({
            'hash': row.get('block_hash'),
            'block_height': row.get('block_height'),
            'timestamp': row.get('timestamp'),
            'tx_count': row.get('tx_count'),
            'transactions': json.dumps(transactions) if transactions else transactions_json,
            'verified': True,
            'source': 'abc_output'
        })

    # Compile through Hades/Echo/Nemesis
    result = compile_from_verified_hashes(
        verified_hashes,
        assumed_scenario="aml_investigation"
    )

    # Build output row with "the concept" (compiled intelligence)
    output_row = {
        "compilation_id": result["compilation_id"],
        "actor_id": result["actor_id"],
        "actor_name": result["actor_name"],
        "behavioral_signature_json": json.dumps(result["behavioral_signature"]),
        "coordination_network_json": json.dumps(result["coordination_network"]),
        "threat_forecast_json": json.dumps(result["threat_forecast"]),
        "targeting_package_json": json.dumps(result["targeting_package"]),
        "confidence_score": result["confidence_score"],
        "compilation_time_ms": result["compilation_time_ms"],
        "receipt_id": result["receipt_id"],
        "receipt_hash": result["receipt_hash"],
        "compiled_at": result["compiled_at"],
        "assumed_scenario": result["assumed_scenario"],
        "input_hash_count": result["input_hash_count"],
        "transaction_count": result["transaction_count"]
    }

    # Return as single-row DataFrame (the concept)
    return pd.DataFrame([output_row])

