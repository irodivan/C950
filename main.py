# C950 Task 2 Student ID: 001158554 - Gonzalo Rodriguez

import csv
from datetime import datetime, timedelta


# Hash table
class HashTable:
    def __init__(self, size=50):
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return key % len(self.table)

    def insert(self, key, package):
        bucket = self.table[self._hash(key)]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = package
                return
        bucket.append([key, package])

    def lookup(self, key):
        bucket = self.table[self._hash(key)]
        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        return None


# Package Class
class Package:
    def __init__(self, packageID, address, city, state, zip_code, deadline, weight, notes):
        self.id = int(packageID)
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip_code
        self.deadline = deadline
        self.weight = weight
        self.notes = notes

        self.status = "At Hub"
        self.delivery_time = None

    def __str__(self):
        return f"{self.id} | {self.address} | {self.status} | {self.delivery_time}"


# Truck Class
class Truck:
    def __init__(self, packages, startTime):
        self.packages = packages
        self.time = startTime
        self.mileage = 0
        self.location = "4001 South 700 East"


# Pull data from distance table csv into distances data member
addresses = []
distances = []
def load_distance_data(filename):
    global addresses, distances

    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)

        addresses = header[1:]

        for row in reader:
            distances.append(row[1:])


# Pull data from package file csv to create package class objects and insert into hash table
def load_package_data(filename, hashTable):

    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:

            package = Package(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7] if len(row) > 7 else ""
            )

            hashTable.insert(package.id, package)


# Find address index
def address_index(address):
    for i, a in enumerate(addresses):
        if a.strip() == address.strip():
            return i
    raise Exception(f"Address not found: {address}")


# Distance between addresses
def get_distance(addr1, addr2):

    i = address_index(addr1)
    j = address_index(addr2)

    d = distances[i][j]

    if d == '':
        d = distances[j][i]

    return float(d)


# Nearest neighbor algorithm logic
def deliver_packages(truck):

    undelivered = truck.packages[:]

    while undelivered:

        nearest = None
        nearestNeighbor = float("inf")

        for package in undelivered:

            distance = get_distance(truck.location, package.address)

            if distance < nearestNeighbor:
                nearestNeighbor = distance
                nearest = package

        truck.mileage += nearestNeighbor

        travel_time = nearestNeighbor / 18
        minutes = int(travel_time * 60)
        truck.time += timedelta(minutes=minutes)

        nearest.status = "Delivered"
        nearest.delivery_time = truck.time

        truck.location = nearest.address

        undelivered.remove(nearest)

def package_status_at_time(package, queryTime, truckStartTime):

    if queryTime < truckStartTime:
        return "At Hub"

    if package.delivery_time is None:
        return "En Route"

    if queryTime < package.delivery_time:
        return "En Route"

    return f"Delivered at {package.delivery_time}"

def print_truck_status(truck, queryTime):

    print("\nTruck Status at", queryTime)
    print("-----------------------------------")

    for package in truck.packages:
        status = package_status_at_time(package, queryTime, truck.time)
        print(f"Package {package.id} | {package.address} | {status}")

def print_all_status(queryTime):

    print("\n================================================")
    print("Package Status at", queryTime)
    print("================================================")

    for i in range(1, 41):

        package = packageTable.lookup(i)

        if package.delivery_time and queryTime >= package.delivery_time:
            status = f"Delivered at {package.delivery_time}"
        elif queryTime >= timedelta(hours=8):
            status = "En Route"
        else:
            status = "At Hub"

        print(f"Package {package.id} | {package.address} | {status}")


# Program start
packageTable = HashTable()

load_package_data("WGUPS Package File.csv", packageTable)
load_distance_data("WGUPS Distance Table.csv")


# Load trucks
truck1 = Truck(
    [packageTable.lookup(i) for i in [1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40]],
    timedelta(hours=8)
)

truck2 = Truck(
    [packageTable.lookup(i) for i in [3, 6, 18, 25, 26, 27, 28, 32, 33, 35, 36, 38]],
    timedelta(hours=9, minutes=5)
)

truck3 = Truck(
    [packageTable.lookup(i) for i in [2, 4, 5, 7, 8, 9, 10, 11, 12, 17, 21, 22, 23, 24, 39]],
    timedelta(hours=10, minutes=20)
)

# Run deliveries
deliver_packages(truck1)
deliver_packages(truck2)
deliver_packages(truck3)

# Total mileage
totalMiles = truck1.mileage + truck2.mileage + truck3.mileage

print("Total mileage:", round(totalMiles, 2))

# Package look up
while True:

    inquiry = input("Enter package ID (or 'exit'): ")

    if inquiry.lower() == "exit":
        break

    package = packageTable.lookup(int(inquiry))

    if package:
        print(package)

# Status prints for screenshot requirements
print_all_status(timedelta(hours=9))
print_all_status(timedelta(hours=10))
print_all_status(timedelta(hours=12, minutes=30))