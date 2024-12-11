import simpy
import uuid
import csv
import random
from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict


@dataclass
class Order:
    pid: str
    tyre_type: str
    brand: str
    tread_pattern: str
    size: str
    quantity: int


@dataclass
class ProcessTime:
    wait_time: float
    process_time: float


@dataclass
class Tyre:
    serial_number: str
    pid: str
    tyre_type: str
    start_time: float = 0
    end_time: float = 0
    process_times: Dict[str, ProcessTime] = None

    def __post_init__(self):
        if self.process_times is None:
            self.process_times = {}


class TyreFactory:
    def __init__(self, env: simpy.Environment):
        self.env = env
        # Initialize resources
        self.building_stations = {
            'wrap_inner_heal': simpy.Resource(env, capacity=1),
            'apply_bead': simpy.Resource(env, capacity=1),
            'wrap_heal': simpy.Resource(env, capacity=1),
            'wrap_bond': simpy.Resource(env, capacity=2),
            'wrap_soft': simpy.Resource(env, capacity=1),
            'wrap_tread': simpy.Resource(env, capacity=1),
            'press': simpy.Resource(env, capacity=1)
        }
        self.curing_ovens = simpy.Resource(env, capacity=12)

        # Statistics
        self.completed_tyres: List[Tyre] = []
        self.station_wait_times = defaultdict(list)
        self.station_process_times = defaultdict(list)
        self.station_queue_lengths = defaultdict(list)

    def generate_serial_number(self) -> str:
        return str(uuid.uuid4())

    def get_building_time(self, step: str) -> float:
        return random.uniform(40, 50) / 60

    def get_curing_temperature(self, tyre_type: str) -> float:
        if tyre_type == 'Resilient':
            heal_temp = random.uniform(70, 100)
            soft_temp = random.uniform(80, 110)
            return min(heal_temp, soft_temp)
        else:
            return random.uniform(80, 110)

    def calculate_curing_time(self, temperature: float) -> float:
        base_time = 40
        temp_difference = 110 - temperature
        additional_time = (temp_difference // 10) * 10
        return base_time + additional_time

    def record_station_metrics(self, station: str, wait_time: float, process_time: float):
        self.station_wait_times[station].append(wait_time)
        self.station_process_times[station].append(process_time)
        queue_length = len(self.building_stations[station].queue) if station != 'curing' else len(
            self.curing_ovens.queue)
        self.station_queue_lengths[station].append(queue_length)

    def build_resilient_tyre(self, tyre: Tyre):
        building_steps = [
            'wrap_inner_heal', 'apply_bead', 'wrap_heal',
            'wrap_bond', 'wrap_soft', 'wrap_tread', 'press'
        ]

        for step in building_steps:
            arrival_time = self.env.now
            with self.building_stations[step].request() as req:
                yield req
                wait_time = self.env.now - arrival_time

                process_start = self.env.now
                yield self.env.timeout(self.get_building_time(step))
                process_time = self.env.now - process_start

                tyre.process_times[step] = ProcessTime(wait_time, process_time)
                self.record_station_metrics(step, wait_time, process_time)
                print(f"{self.env.now:.2f}: {tyre.serial_number} completed {
                      step} (Wait: {wait_time:.2f}, Process: {process_time:.2f})")

    def build_press_on_tyre(self, tyre: Tyre):
        building_steps = ['wrap_bond', 'wrap_soft', 'wrap_tread', 'press']

        for step in building_steps:
            arrival_time = self.env.now
            with self.building_stations[step].request() as req:
                yield req
                wait_time = self.env.now - arrival_time

                process_start = self.env.now
                yield self.env.timeout(self.get_building_time(step))
                process_time = self.env.now - process_start

                tyre.process_times[step] = ProcessTime(wait_time, process_time)
                self.record_station_metrics(step, wait_time, process_time)
                print(f"{self.env.now:.2f}: {tyre.serial_number} completed {
                      step} (Wait: {wait_time:.2f}, Process: {process_time:.2f})")

    def cure_tyre(self, tyre: Tyre):
        arrival_time = self.env.now
        with self.curing_ovens.request() as req:
            yield req
            wait_time = self.env.now - arrival_time

            process_start = self.env.now
            temperature = self.get_curing_temperature(tyre.tyre_type)
            curing_time = self.calculate_curing_time(temperature)
            print(f"{self.env.now:.2f}: {
                  tyre.serial_number} starting cure at {temperature:.1f}°C")
            yield self.env.timeout(curing_time)
            process_time = self.env.now - process_start

            tyre.process_times['curing'] = ProcessTime(wait_time, process_time)
            self.record_station_metrics('curing', wait_time, process_time)
            print(f"{self.env.now:.2f}: {tyre.serial_number} completed curing (Wait: {
                  wait_time:.2f}, Process: {process_time:.2f})")

    def manufacture_tyre(self, order: Order):
        for _ in range(order.quantity):
            tyre = Tyre(
                serial_number=self.generate_serial_number(),
                pid=order.pid,
                tyre_type=order.tyre_type,
                start_time=self.env.now
            )

            if order.tyre_type == 'Resilient':
                yield from self.build_resilient_tyre(tyre)
            else:
                yield from self.build_press_on_tyre(tyre)

            yield from self.cure_tyre(tyre)

            tyre.end_time = self.env.now
            self.completed_tyres.append(tyre)
            print(f"{self.env.now:.2f}: {
                  tyre.serial_number} completed manufacturing")

    def generate_insights(self):
        print("\n=== Manufacturing Process Insights ===")

        print("\nStation Wait Times (minutes):")
        for station, times in self.station_wait_times.items():
            avg_wait = sum(times) / len(times) if times else 0
            max_wait = max(times) if times else 0
            print(f"{station:15} Avg: {avg_wait:6.2f}  Max: {max_wait:6.2f}")

        print("\nStation Process Times (minutes):")
        for station, times in self.station_process_times.items():
            avg_process = sum(times) / len(times) if times else 0
            max_process = max(times) if times else 0
            print(f"{station:15} Avg: {
                  avg_process:6.2f}  Max: {max_process:6.2f}")

        print("\nStation Queue Lengths:")
        for station, lengths in self.station_queue_lengths.items():
            avg_queue = sum(lengths) / len(lengths) if lengths else 0
            max_queue = max(lengths) if lengths else 0
            print(f"{station:15} Avg: {avg_queue:6.2f}  Max: {max_queue:6.2f}")

        print("\nBottleneck Analysis:")
        avg_wait_times = {station: sum(times)/len(times) if times else 0
                          for station, times in self.station_wait_times.items()}
        bottleneck_station = max(avg_wait_times.items(), key=lambda x: x[1])[0]
        print(f"Primary bottleneck: {bottleneck_station} (Avg wait: {
              avg_wait_times[bottleneck_station]:.2f} minutes)")


def load_orders(filename: str) -> List[Order]:
    orders = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            orders.append(Order(
                pid=row['PID'],
                tyre_type=row['TyreType'],
                brand=row['Brand'],
                tread_pattern=row['TreadPattern'],
                size=row['Size'],
                quantity=int(row['Quantity'])
            ))
    return orders


def run_simulation(orders: List[Order], sim_time: float = 480):
    env = simpy.Environment()
    factory = TyreFactory(env)

    for order in orders:
        env.process(factory.manufacture_tyre(order))

    env.run(until=sim_time)

    print("\nSimulation Results:")
    print(f"Total tyres completed: {len(factory.completed_tyres)}")

    total_time = sum(
        tyre.end_time - tyre.start_time for tyre in factory.completed_tyres)
    avg_time = total_time / \
        len(factory.completed_tyres) if factory.completed_tyres else 0
    print(f"Average manufacturing time: {avg_time:.2f} minutes")

    # Generate detailed insights
    factory.generate_insights()

    return factory.completed_tyres


if __name__ == "__main__":
    orders = load_orders("order.csv")
    completed_tyres = run_simulation(orders)
