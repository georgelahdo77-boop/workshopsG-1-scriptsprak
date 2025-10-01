# Import the json library so that we can handle json
import json

# Read json from products.json to the variable data
data = json.load(open("network_devices.json","r",encoding = "utf-8"))

# loop through the location list
for location in data["locations"]:
    # print the site/'name' of the location
    print("")
    print(location["site"])
    # print a list of the host names of the devices on the location
    for device in location["devices"]:
        print(" ",device["hostname"])