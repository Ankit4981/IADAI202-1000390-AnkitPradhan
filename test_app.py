"""Automated test suite for LogiSight Analytics app."""
import app
import pandas as pd
import numpy as np

print("=" * 65)
print("LogiSight Analytics — Full Test Suite (Verification)")
print("=" * 65)

# 1. Data Loading
df, meta = app.load_data()
assert len(df) == 43594, f"Expected 43594, got {len(df)}"
assert meta["clean"] == 43594
print(f"1. Data loading: PASS — {len(df):,} clean verified records")

# 2. Checkpoints matching assignment & design
assert meta["late"] == 7156, f"Late count mismatch: {meta['late']}"
assert round(meta["late_pct"], 1) == 16.4, f"Late pct mismatch: {meta['late_pct']}"
assert round(meta["mean"], 1) == 124.9, f"Mean mismatch: {meta['mean']}"
print("2. Validation checkpoints: PASS")
print(f"   Mean={meta['mean']:.1f} min, Late={meta['late']} ({meta['late_pct']:.1f}%), On-time={len(df)-meta['late']} ({100-meta['late_pct']:.1f}%)")

# 3. Vehicle breakdown
veh = df[df["Vehicle"].isin(["Van", "Scooter", "Motorcycle"])].groupby("Vehicle")["Order_ID"].count().to_dict()
assert veh.get("Van", 0) == 3518, f"Van mismatch: {veh.get('Van')}"
assert veh.get("Scooter", 0) == 14590, f"Scooter mismatch: {veh.get('Scooter')}"
assert veh.get("Motorcycle", 0) == 25486, f"Motorcycle mismatch: {veh.get('Motorcycle')}"
print(f"3. Vehicle counts: PASS — Van={veh['Van']}, Scooter={veh['Scooter']}, Motorcycle={veh['Motorcycle']}")

# 4. Chart functions
fig1 = app.delay_chart(df)
print("4a. Chart 1 (Delay Analyzer): PASS")

fig2 = app.vehicle_chart(df)
print("4b. Chart 2 (Vehicle Comparison): PASS")

fig3 = app.scatter_chart(df, sample=500)
print("4c. Chart 3 (Agent Performance Scatter): PASS")

fig4 = app.heatmap_chart(df, compact=True)
print("4d. Chart 4 (Area Heatmap): PASS")

fig5 = app.box_chart(df)
print("4e. Chart 5 (Category Boxplot): PASS")

fig6 = app.delivery_distribution_chart(df)
print("4f. Chart 6 (Delivery Time Histogram): PASS")

# 5. Navigation & Pages
expected_nav = ["Dashboard", "Delivery Analysis", "Agent Performance", "Regional & Category", "Data Preparation", "About Project"]
actual_nav = [label for label, _ in app.NAV]
assert actual_nav == expected_nav, f"NAV mismatch: {actual_nav} vs {expected_nav}"
print(f"5. Navigation: PASS — 6 distinct pages: {actual_nav}")

for fn_name in ["page_dashboard", "page_delivery", "page_agent", "page_regional", "page_prep", "page_about"]:
    assert hasattr(app, fn_name) and callable(getattr(app, fn_name)), f"Missing page function: {fn_name}"
print("6. Page Renderers: PASS — all 6 unique page functions verified")

print()
print("=" * 65)
print("ALL TESTS PASSED WITH 100% SUCCESS")
print("=" * 65)
