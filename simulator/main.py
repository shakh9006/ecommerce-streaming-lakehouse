from core.producer import EcommerceEventSimulator

if __name__ == "__main__":
    simulator = EcommerceEventSimulator()
    events = simulator.run()
    print("events:")
    print(events)