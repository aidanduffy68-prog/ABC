# Foundry Transform: Process Synthetic Compliance Data
#
# Simple pass-through: Copy all 5 columns
# For DataFrame transform in Foundry UI, use this code:

def transform(input_df):
    """
    Simple pass-through: copy all 5 columns.
    
    In Foundry UI:
    1. Select your input dataset (Synthetic Compliance Data)
    2. Select your output dataset (scenario_forge_output)
    3. Paste this function body in the transform
    """
    # Simple pass-through - copy all columns
    return input_df.copy()

# Alternative: If using Foundry Functions (@function pattern):
# from functions.api import function, String, Integer
# 
# @function  
# def process_transactions(transactions: String) -> String:
#     """Process transactions column."""
#     return transactions
# 
# Then use in transform UI to map columns as needed
