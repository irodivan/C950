# C950 Task 2 Student ID: 001158554 - Gonzalo Rodriguez

import csv
from datetime import datetime, timedelta


# Hash table: stores package data using the package ID as the key
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

        # Used to correct package 9's address
        self.corrected = False

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


# Pull data from package file csv to insert raw data into hash table
def load_package_data(filename, hashTable):

    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:

            packageID = int(row[0])

            hashTable.insert(packageID, [
                row[1],  # address
                row[5],  # deadline
                row[2],  # city
                row[4],  # zip code
                row[6],  # weight
                "At Hub",  # status
                None  # delivery time
            ])

# Package object creation method for use with hash table raw data
# Allows delivery algorithm to work with object classes
def create_package(packageID):
    data = packageTable.lookup(packageID)
    return Package(
        packageID,
        data[0],
        data[2],
        "",
        data[3],
        data[1],
        data[4],
        ""
    )

# Find address index for reference when calculating distances
def address_index(address):
    for i, a in enumerate(addresses):
        if a.strip() == address.strip():
            return i
    raise Exception(f"Address not found: {address}")


# Calculates distance between addresses via distance table for use by nearest neighbor algorithm
def get_distance(addr1, addr2):

    i = address_index(addr1)
    j = address_index(addr2)

    d = distances[i][j]

    if d == '':
        d = distances[j][i]

    return float(d)


# Nearest neighbor algorithm logic
# Finds closest undelivered package after each delivery
def deliver_packages(truck):

    undelivered = truck.packages[:]
    package9 = next((p for p in truck.packages if p.id == 9), None)
    while undelivered:

        nearest = None
        nearestNeighbor = float("inf")

        # Updates correct address for package 9 at 10:20
        if truck.time >= timedelta(hours=10, minutes=20) and package9 and not package9.corrected:
            # Update Package object
            package9.address = "410 S State St"
            package9.zip = "84111"

            # Update hash table
            data = packageTable.lookup(9)
            data[0] = "410 S State St"
            data[3] = "84111"

            package9.corrected = True

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
        data = packageTable.lookup(nearest.id)
        data[5] = "Delivered"
        data[6] = truck.time

        truck.location = nearest.address

        undelivered.remove(nearest)

# Below methods are for the user to query packages at a desired time
# Pulls data from hash table and trucks loaded package class objects
def package_status_at_time(package, queryTime, truckStartTime):

    if queryTime < truckStartTime:
        return "At Hub"

    if package[6] is None:
        return "En Route"

    if queryTime < package[6]:
        return "En Route"

    return f"Delivered at {package[6]}"

def print_truck_status(truck, queryTime):

    print("\nTruck Status at", queryTime)
    print("-----------------------------------")

    for package in truck.packages:
        status = package_status_at_time(package, queryTime, truck.time)
        print(f"Package {package.id} | {packageTable.lookup(package.id)[0]} | {status}")

def print_all_status(queryTime, trucks):

    print("\n================================================")
    print("Package Status at", queryTime)
    print("================================================")

    for i, truck in enumerate(trucks, start=1):

        print(f"\n--- Truck {i} ---")

        sorted_packages = sorted(truck.packages, key=lambda p: p.id)

        for package in sorted_packages:

            if package.delivery_time and queryTime >= package.delivery_time:
                status = f"Delivered at {package.delivery_time}"
            elif queryTime >= timedelta(hours=8):
                status = "En Route"
            else:
                status = "At Hub"

            print(f"Package {package.id} | {packageTable.lookup(package.id)[0]} | {status}")

# Program Flow:
# 1. Load package and distance data from CSV files into memory
# 2. Store package data in a hash table
# 3. Convert raw data into Package objects for delivery simulation
# 4. Assign packages to trucks with specific start times
# 5. Run the delivery algorithm using nearest neighbor approach
# 6. Track mileage, delivery times, and package statuses
# 7. Allow user to query package status at any time
# 8. Display results grouped by truck or individual package lookup
# Program start
packageTable = HashTable()

load_package_data("WGUPS Package File.csv", packageTable)
load_distance_data("WGUPS Distance Table.csv")


# Load trucks with Package class objects for use with algorithm logic
truck1 = Truck(
    [create_package(i) for i in [1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40]],
    timedelta(hours=8)
)

truck2 = Truck(
    [create_package(i) for i in [3, 6, 18, 25, 26, 27, 28, 32, 33, 35, 36, 38]],
    timedelta(hours=9, minutes=5)
)

truck3 = Truck(
    [create_package(i) for i in [2, 4, 5, 7, 8, 9, 10, 11, 12, 17, 21, 22, 23, 24, 39]],
    timedelta(hours=10, minutes=20)
)

# Run deliveries
deliver_packages(truck1)
deliver_packages(truck2)
deliver_packages(truck3)
trucks = [truck1, truck2, truck3]

# Total mileage
totalMiles = truck1.mileage + truck2.mileage + truck3.mileage

print("Total mileage:", round(totalMiles, 2))

# Package look up
while True:

    inquiry = input("Enter package ID or All(or 'exit'): ")

    # Print all packages at desired time
    if inquiry.lower() == "all":
        queryTime = input("Enter time: (HH:MM format)")
        h, m = queryTime.split(":")
        queryTime = timedelta(hours=int(h), minutes=int(m))
        print_all_status(queryTime, trucks)
        continue

    if inquiry.lower() == "exit":
        break

    # create package object from raw data for ease of use
    package = create_package(int(inquiry))

    if package:
        queryTime = input("Enter package time: (HH:MM format)")
        h, m = queryTime.split(":")
        queryTime = timedelta(hours=int(h), minutes=int(m))
        if package.delivery_time and queryTime >= package.delivery_time:
            status = f"Delivered at {package.delivery_time}"
        elif queryTime >= timedelta(hours=8):
            status = "En Route"
        else:
            status = "At Hub"
        print(f"Package {package.id} | {packageTable.lookup(package.id)[0]} | {status}")



# Status prints for screenshot requirements
print_all_status(timedelta(hours=9), trucks)
print_all_status(timedelta(hours=10), trucks)
print_all_status(timedelta(hours=12, minutes=30), trucks)