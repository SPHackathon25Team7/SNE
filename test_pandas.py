#!/usr/bin/env python3
"""
Test if pandas is working correctly
"""
try:
    import pandas as pd
    print("✅ pandas imported successfully")
    
    # Test basic DataFrame operations
    data = {'ID': [1, 2, 3], 'Name': ['Alice', 'Bob', 'Charlie']}
    df = pd.DataFrame(data)
    print("✅ DataFrame created successfully")
    print(df)
    
    # Test iterrows
    print("\n✅ Testing iterrows:")
    for _, row in df.iterrows():
        print(f"  ID: {row['ID']}, Name: {row['Name']}")
        
except ImportError as e:
    print(f"❌ pandas not available: {e}")
except Exception as e:
    print(f"❌ pandas error: {e}")