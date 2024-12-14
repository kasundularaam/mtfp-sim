import simpy
import uuid
import csv
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict

# Enums for different types and states


class TyreType(Enum):
    RESILIENT_SOFT_BOND = "Resilient-SoftBond"
    RESILIENT_BASIC = "Resilient-Basic"
    PRESS_ON = "Press-On"


class Size(Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class TemperatureRange(Enum):
    OPTIMAL = "Optimal"
    ACCEPTABLE = "Acceptable"
    MINIMUM = "Minimum"


@dataclass
class TyreOrder:
    pid: str
    tyre_type: TyreType
    brand: str
    tread_pattern: str
    size: Size
    quantity: int


@dataclass
class Tyre:
    serial_number: str
    order: TyreOrder


class TyreFactory:
    def __init__(self, env: simpy.Environment):
        self.env = env

        # Building stations (capacity=1 for each)
        self.wrap_inner_heal = simpy.Resource(env, capacity=1)
        self.apply_bead = simpy.Resource(env, capacity=1)
        self.wrap_heal = simpy.Resource(env, capacity=1)
        self.resilient_bond_wrap = simpy.Resource(env, capacity=1)
        self.press_on_bond_wrap = simpy.Resource(env, capacity=1)
        self.wrap_soft = simpy.Resource(env, capacity=1)
        self.wrap_tread = simpy.Resource(env, capacity=1)
        self.press = simpy.Resource(env, capacity=1)

        # Curing ovens (capacity=12)
        self.curing_ovens = simpy.Resource(env, capacity=12)

        # Production tracking
        self.completed_tyres: List[Tyre] = []

    def get_temperature_range(self) -> TemperatureRange:
        """Simulate temperature measurement and return the range."""
        rand = random.random()
        if rand < 0.6:  # 60% chance of optimal
            return TemperatureRange.OPTIMAL
        elif rand < 0.9:  # 30% chance of acceptable
            return TemperatureRange.ACCEPTABLE
        else:  # 10% chance of minimum
            return TemperatureRange.MINIMUM

    def get_base_curing_time(self, tyre: Tyre) -> int:
        """Get base curing time in minutes based on tyre type."""
        if tyre.order.tyre_type == TyreType.RESILIENT_SOFT_BOND:
            return 120
        elif tyre.order.tyre_type == TyreType.RESILIENT_BASIC:
            return 100
        else:  # Press-On
            return 90

    def get_size_adjustment(self, size: Size) -> int:
        """Get additional curing time based on size."""
        if size == Size.MEDIUM:
            return 15
        elif size == Size.LARGE:
            return 30
        return 0

    def get_temperature_adjustment(self, temp_range: TemperatureRange) -> int:
        """Get additional curing time based on temperature range."""
        if temp_range == TemperatureRange.ACCEPTABLE:
            return 20
        elif temp_range == TemperatureRange.MINIMUM:
            return 40
        return 0

    def wrap_inner_heal_process(self, tyre: Tyre):
        """Simulate wrap inner heal process."""
        process_time = random.uniform(40, 50)  # 40-50 seconds
        yield self.env.timeout(process_time)

    def apply_bead_process(self, tyre: Tyre):
        """Simulate bead application process."""
        process_time = random.uniform(45, 55)  # 45-55 seconds
        yield self.env.timeout(process_time)

    def wrap_heal_process(self, tyre: Tyre):
        """Simulate heal wrapping process."""
        process_time = random.uniform(45, 55)
        yield self.env.timeout(process_time)

    def wrap_bond_process(self, tyre: Tyre):
        """Simulate bond wrapping process."""
        process_time = random.uniform(45, 55)
        yield self.env.timeout(process_time)

    def wrap_soft_process(self, tyre: Tyre):
        """Simulate soft wrapping process."""
        process_time = random.uniform(45, 55)
        yield self.env.timeout(process_time)

    def wrap_tread_process(self, tyre: Tyre):
        """Simulate tread wrapping process."""
        process_time = random.uniform(45, 55)
        yield self.env.timeout(process_time)

    def press_process(self, tyre: Tyre):
        """Simulate pressing process."""
        process_time = random.uniform(120, 300)  # 2-5 minutes in seconds
        yield self.env.timeout(process_time)

    def curing_process(self, tyre: Tyre):
        """Simulate curing process."""
        temp_range = self.get_temperature_range()

        # Calculate total curing time
        base_time = self.get_base_curing_time(tyre)
        size_adj = self.get_size_adjustment(tyre.order.size)
        temp_adj = self.get_temperature_adjustment(temp_range)

        total_time = (base_time + size_adj + temp_adj) * \
            60  # Convert to seconds
        yield self.env.timeout(total_time)

    def manufacture_resilient_soft_bond(self, tyre: Tyre):
        """Manufacturing process for Resilient tyres with soft & bond."""
        # Wrap Inner Heal
        with self.wrap_inner_heal.request() as req:
            yield req
            yield self.env.process(self.wrap_inner_heal_process(tyre))

        # Apply Bead
        with self.apply_bead.request() as req:
            yield req
            yield self.env.process(self.apply_bead_process(tyre))

        # Wrap Heal
        with self.wrap_heal.request() as req:
            yield req
            yield self.env.process(self.wrap_heal_process(tyre))

        # Wrap Resilient Bond
        with self.resilient_bond_wrap.request() as req:
            yield req
            yield self.env.process(self.wrap_bond_process(tyre))

        # Wrap Soft
        with self.wrap_soft.request() as req:
            yield req
            yield self.env.process(self.wrap_soft_process(tyre))

        # Wrap Tread
        with self.wrap_tread.request() as req:
            yield req
            yield self.env.process(self.wrap_tread_process(tyre))

        # Press
        with self.press.request() as req:
            yield req
            yield self.env.process(self.press_process(tyre))

        # Curing
        with self.curing_ovens.request() as req:
            yield req
            yield self.env.process(self.curing_process(tyre))

        self.completed_tyres.append(tyre)

    def manufacture_resilient_basic(self, tyre: Tyre):
        """Manufacturing process for Resilient tyres without soft & bond."""
        # Wrap Inner Heal
        with self.wrap_inner_heal.request() as req:
            yield req
            yield self.env.process(self.wrap_inner_heal_process(tyre))

        # Apply Bead
        with self.apply_bead.request() as req:
            yield req
            yield self.env.process(self.apply_bead_process(tyre))

        # Wrap Heal
        with self.wrap_heal.request() as req:
            yield req
            yield self.env.process(self.wrap_heal_process(tyre))

        # Wrap Tread
        with self.wrap_tread.request() as req:
            yield req
            yield self.env.process(self.wrap_tread_process(tyre))

        # Press
        with self.press.request() as req:
            yield req
            yield self.env.process(self.press_process(tyre))

        # Curing
        with self.curing_ovens.request() as req:
            yield req
            yield self.env.process(self.curing_process(tyre))

        self.completed_tyres.append(tyre)

    def manufacture_press_on(self, tyre: Tyre):
        """Manufacturing process for Press-On tyres."""
        # Wrap Press-On Bond
        with self.press_on_bond_wrap.request() as req:
            yield req
            yield self.env.process(self.wrap_bond_process(tyre))

        # Wrap Soft
        with self.wrap_soft.request() as req:
            yield req
            yield self.env.process(self.wrap_soft_process(tyre))

        # Wrap Tread
        with self.wrap_tread.request() as req:
            yield req
            yield self.env.process(self.wrap_tread_process(tyre))

        # Press
        with self.press.request() as req:
            yield req
            yield self.env.process(self.press_process(tyre))

        # Curing
        with self.curing_ovens.request() as req:
            yield req
            yield self.env.process(self.curing_process(tyre))

        self.completed_tyres.append(tyre)


def load_orders(filename: str) -> List[TyreOrder]:
    """Load orders from CSV file."""
    orders = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            order = TyreOrder(
                pid=row['PID'],
                brand=row['Brand'],
                tyre_type=TyreType(row['TyreType']),
                tread_pattern=row['TreadPattern'],
                size=Size(row['Size']),
                quantity=int(row['Quantity'])
            )
            orders.append(order)
    return orders


def order_generator(env: simpy.Environment, factory: TyreFactory, orders: List[TyreOrder]):
    """Generate tyre manufacturing processes based on orders."""
    for order in orders:
        for _ in range(order.quantity):
            tyre = Tyre(
                serial_number=str(uuid.uuid4()),
                order=order
            )

            if order.tyre_type == TyreType.RESILIENT_SOFT_BOND:
                env.process(factory.manufacture_resilient_soft_bond(tyre))
            elif order.tyre_type == TyreType.RESILIENT_BASIC:
                env.process(factory.manufacture_resilient_basic(tyre))
            else:  # Press-On
                env.process(factory.manufacture_press_on(tyre))

            # Small delay between starting each tyre
            yield env.timeout(random.uniform(30, 60))


def run_simulation(orders_file: str, simulation_duration: int = 86400/3):
    """Run the factory simulation for the specified duration (default 24 hours)."""
    # Create SimPy environment
    env = simpy.Environment()

    # Create factory
    factory = TyreFactory(env)

    # Load orders
    orders = load_orders(orders_file)

    # Start order generator
    env.process(order_generator(env, factory, orders))

    # Run simulation
    env.run(until=simulation_duration)

    return factory.completed_tyres


if __name__ == "__main__":
    # Run simulation for 24 hours
    completed_tyres = run_simulation("orders.csv")

    # Print results
    print(f"Total tyres completed: {len(completed_tyres)}")

    # Group completed tyres by type
    type_counts = {}
    for tyre in completed_tyres:
        tyre_type = tyre.order.tyre_type.value
        type_counts[tyre_type] = type_counts.get(tyre_type, 0) + 1

    print("\nCompleted tyres by type:")
    for tyre_type, count in type_counts.items():
        print(f"{tyre_type}: {count}")


# Crack the PID
# All tyre types
# Planning Cards
# Curing Times
# Temperature
