import MetaTrader5 as mt5

print(f"Version: {mt5.__version__}")
print("Attributes:")
for attr in dir(mt5):
    if "calendar" in attr:
        print(f" - {attr}")
