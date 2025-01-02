import simpy
import random
import uuid
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict
import statistics

# Data structures


@dataclass
class TyreOrder:
    pid: str
    tyre_type: str
    brand: str
    tread_pattern: str
    size: str
    quantity: int


@dataclass
class ProductionStats:
    serial_number: str
    pid: str
    start_time: float
    end_time: float = 0
    waiting_times: Dict[str, float] = None
    total_production_time: float = 0


class TyreFactory:
    def __init__(self, env):
        self.env = env
        # Resources
        self.wrap_inner_heal = simpy.Resource(env, capacity=1)
        self.apply_bead = simpy.Resource(env, capacity=1)
        self.wrap_heal = simpy.Resource(env, capacity=1)
        self.resilient_bond = simpy.Resource(env, capacity=1)
        self.press_on_bond = simpy.Resource(env, capacity=1)
        self.wrap_soft = simpy.Resource(env, capacity=1)
        self.wrap_tread = simpy.Resource(env, capacity=1)
        self.press = simpy.Resource(env, capacity=1)
        self.curing_ovens = simpy.Resource(env, capacity=12)

        # Statistics
        self.production_stats: List[ProductionStats] = []

    def get_process_time(self, process_name: str) -> float:
        """Return processing time for each station"""
        time_ranges = {
            'wrap_inner_heal': (40, 50),
            'apply_bead': (45, 55),
            'wrap_heal': (45, 55),
            'wrap_bond': (45, 55),
            'wrap_soft': (45, 55),
            'wrap_tread': (45, 55),
            'press': (120, 300)  # 2-5 minutes in seconds
        }
        # Convert to minutes
        return random.uniform(*time_ranges.get(process_name, (45, 55))) / 60

    def get_curing_time(self, tyre_type: str, size: str, temp_range: str) -> float:
        """Calculate curing time based on type, size and temperature range"""
        base_times = {
            'Resilient-SoftBond': 120,
            'Resilient-Basic': 100,
            'Press-On': 90
        }

        temp_adjustments = {
            'optimal': 0,
            'acceptable': 20,
            'minimum': 40
        }

        size_adjustments = {
            'Small': 0,
            'Medium': 15,
            'Large': 30
        }

        base_time = base_times[tyre_type]
        temp_adj = temp_adjustments[temp_range]
        size_adj = size_adjustments[size]

        return base_time + temp_adj + size_adj

    def process_tyre(self, order: TyreOrder):
        """Process a single tyre through the production line"""
        serial_number = str(uuid.uuid4())
        start_time = self.env.now
        waiting_times = {}

        # Create stats object
        stats = ProductionStats(
            serial_number=serial_number,
            pid=order.pid,
            start_time=start_time,
            waiting_times={}
        )

        # Different process flows based on tyre type
        if order.tyre_type == 'Resilient-SoftBond':
            # Full process for Resilient tyres with soft & bond
            steps = [
                (self.wrap_inner_heal, 'wrap_inner_heal'),
                (self.apply_bead, 'apply_bead'),
                (self.wrap_heal, 'wrap_heal'),
                (self.resilient_bond, 'wrap_bond'),
                (self.wrap_soft, 'wrap_soft'),
                (self.wrap_tread, 'wrap_tread'),
                (self.press, 'press')
            ]
        elif order.tyre_type == 'Resilient-Basic':
            # Process for Resilient tyres without soft & bond
            steps = [
                (self.wrap_inner_heal, 'wrap_inner_heal'),
                (self.apply_bead, 'apply_bead'),
                (self.wrap_heal, 'wrap_heal'),
                (self.wrap_tread, 'wrap_tread'),
                (self.press, 'press')
            ]
        else:  # Press-On
            # Process for Press-On tyres
            steps = [
                (self.press_on_bond, 'wrap_bond'),
                (self.wrap_soft, 'wrap_soft'),
                (self.wrap_tread, 'wrap_tread'),
                (self.press, 'press')
            ]

        # Execute building process
        for resource, step_name in steps:
            arrival_time = self.env.now
            req = resource.request()
            yield req
            waiting_time = self.env.now - arrival_time
            stats.waiting_times[step_name] = waiting_time
            process_time = self.get_process_time(step_name)
            yield self.env.timeout(process_time)
            resource.release(req)

        # Curing process
        arrival_time = self.env.now
        req = self.curing_ovens.request()
        yield req
        waiting_time = self.env.now - arrival_time
        stats.waiting_times['curing'] = waiting_time

        # Simulate random temperature range
        temp_range = random.choice(['optimal', 'acceptable', 'minimum'])
        curing_time = self.get_curing_time(
            order.tyre_type, order.size, temp_range)
        yield self.env.timeout(curing_time)
        self.curing_ovens.release(req)

        # Record completion
        stats.end_time = self.env.now
        stats.total_production_time = stats.end_time - stats.start_time
        self.production_stats.append(stats)

    def get_production_insights(self):
        """Generate detailed insights from production statistics"""
        if not self.production_stats:
            return "No production data available"

        total_tyres = len(self.production_stats)

        # Calculate overall statistics
        all_production_times = [
            stat.total_production_time for stat in self.production_stats]
        avg_production_time = statistics.mean(all_production_times)
        max_production_time = max(all_production_times)
        min_production_time = min(all_production_times)

        # Calculate statistics by tyre type
        type_stats = {}
        for stat in self.production_stats:
            tyre_type = stat.pid.split('.')[0]
            if tyre_type not in type_stats:
                type_stats[tyre_type] = []
            type_stats[tyre_type].append(stat.total_production_time)

        type_averages = {
            tyre_type: {
                'count': len(times),
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times)
            }
            for tyre_type, times in type_stats.items()
        }

        # Calculate waiting times for each station
        station_waiting_times = {}
        for stat in self.production_stats:
            for station, time in stat.waiting_times.items():
                if station not in station_waiting_times:
                    station_waiting_times[station] = []
                station_waiting_times[station].append(time)

        station_stats = {
            station: {
                'avg_wait': statistics.mean(times),
                'max_wait': max(times),
                'min_wait': min(times),
                'total_wait': sum(times)
            }
            for station, times in station_waiting_times.items()
        }

        return {
            'overall_statistics': {
                'total_tyres_produced': total_tyres,
                'avg_production_time': avg_production_time,
                'max_production_time': max_production_time,
                'min_production_time': min_production_time,
                'total_simulation_time': self.env.now
            },
            'tyre_type_statistics': type_averages,
            'station_statistics': station_stats
        }

# Simulation setup and execution


def run_simulation(orders: List[TyreOrder], simulation_time: int = 480):  # 8-hour shift
    env = simpy.Environment()
    factory = TyreFactory(env)

    # Create processes for each order
    for order in orders:
        for _ in range(order.quantity):
            env.process(factory.process_tyre(order))

    # Run simulation
    env.run(until=simulation_time)

    return factory.get_production_insights()

# Helper function to create dataframe for visualization


def create_production_dataframe(production_stats):
    data = []
    for stat in production_stats:
        row = {
            'serial_number': stat.serial_number,
            'pid': stat.pid,
            'start_time': stat.start_time,
            'end_time': stat.end_time,
            'total_time': stat.total_production_time
        }
        # Add waiting times for each station
        for station, time in stat.waiting_times.items():
            row[f'{station}_wait'] = time
        data.append(row)
    return pd.DataFrame(data)


# Main simulation execution
if __name__ == "__main__":
    try:
        # Read orders from CSV
        print("Loading orders from orders.csv...")
        orders_df = pd.read_csv('orders.csv')
        orders = [
            TyreOrder(
                pid=row['PID'],
                tyre_type=row['TyreType'],
                brand=row['Brand'],
                tread_pattern=row['TreadPattern'],
                size=row['Size'],
                quantity=int(row['Quantity'])  # Ensure quantity is integer
            ) for _, row in orders_df.iterrows()
        ]

        print(f"\nLoaded {len(orders)} unique orders")
        print(f"Total tyres to produce: {
              sum(order.quantity for order in orders)}")

        # Run simulation for a full 8-hour shift
        print("\nRunning simulation for 8-hour shift (480 minutes)...")
        insights = run_simulation(orders, simulation_time=480)

        # Print detailed insights
        print("\n=== SIMULATION INSIGHTS ===")
        overall = insights['overall_statistics']
        print(f"\nOVERALL STATISTICS:")
        print(f"Total tyres produced: {overall['total_tyres_produced']}")
        print(f"Average production time: {
              overall['avg_production_time']:.2f} minutes")
        print(f"Fastest production time: {
              overall['min_production_time']:.2f} minutes")
        print(f"Slowest production time: {
              overall['max_production_time']:.2f} minutes")
        print(f"Total simulation time: {
              overall['total_simulation_time']:.2f} minutes")

        print(f"\nPRODUCTION BY TYRE TYPE:")
        type_mapping = {'101': 'Resilient-SoftBond',
                        '102': 'Press-On', '103': 'Resilient-Basic'}
        for type_id, stats in insights['tyre_type_statistics'].items():
            tyre_type = type_mapping.get(type_id, type_id)
            print(f"\n{tyre_type}:")
            print(f"  Quantity produced: {stats['count']}")
            print(f"  Average time: {stats['avg_time']:.2f} minutes")
            print(f"  Range: {stats['min_time']                  :.2f} - {stats['max_time']:.2f} minutes")

        print(f"\nSTATION STATISTICS:")
        for station, stats in insights['station_statistics'].items():
            print(f"\n{station.replace('_', ' ').title()}:")
            print(f"  Average wait: {stats['avg_wait']:.2f} minutes")
            print(f"  Maximum wait: {stats['max_wait']:.2f} minutes")
            print(f"  Total wait time: {stats['total_wait']:.2f} minutes")

    except FileNotFoundError:
        print("Error: orders.csv file not found in the current directory")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
