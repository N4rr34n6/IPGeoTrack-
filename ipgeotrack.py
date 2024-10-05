import sqlite3
import socket
import struct
import pandas as pd
import argparse
import datetime
import maxminddb
import sys
import os

# Converts an IP address into an integer format
def ip2int(ip):
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

# Retrieves the city/country name based on available language keys
def get_name(names):
    if "es" in names:
        return names["es"]
    elif "en" in names:
        return names["en"]
    else:
        languages = list(names.keys())
        if languages:  # Check if the list is not empty
            language = languages[0]
            return names[language]
        else:  # If the list is empty, return a default value
            return "Unknown"

# Finds the closest MaxMind and DB-IP files based on the provided date
def get_mmdb_files(date):
    date = datetime.datetime.strptime(date, "%Y%m%d")
    maxmind_file_before = None
    maxmind_file_after = None
    dbip_file = None

    # Search for MaxMind files that match the date
    for file in os.listdir("DownloadedFiles/MaxMind/"):
        if file.startswith("GeoLite2-City_"):
            file_path = os.path.join("DownloadedFiles/MaxMind/", file)
            file_name = os.path.basename(file_path)
            file_date = file_name[14:22]
            file_date = datetime.datetime.strptime(file_date, "%Y%m%d")
            if file_date <= date:
                if not maxmind_file_before or file_date > maxmind_file_before[1]:
                    maxmind_file_before = (file_path + "/GeoLite2-City.mmdb", file_date)
            else:
                if not maxmind_file_after or file_date < maxmind_file_after[1]:
                    maxmind_file_after = (file_path + "/GeoLite2-City.mmdb", file_date)

    # Search for DB-IP files that match the date
    for file in os.listdir("DownloadedFiles/DB-IP/"):
        if file.endswith(".mmdb"):
            file_date = file[14:20]
            file_date = datetime.datetime.strptime(file_date, "%Y%m")
            if file_date <= date:
                if not dbip_file or file_date > dbip_file[1]:
                    dbip_file = ("DownloadedFiles/DB-IP/" + file, file_date)

    # Return the latest available file if there isn't a more recent one
    if not maxmind_file_after:
        maxmind_file_after = maxmind_file_before
    if not dbip_file:
        print(f"No DB-IP file earlier than or equal to {date.strftime('%Y%m%d')}.")
        sys.exit()

    return maxmind_file_before[0], maxmind_file_after[0], dbip_file[0]

# Retrieves MaxMind database record for a given IP
def get_mmdb_record(file, ip):
    db = maxminddb.open_database(file)
    record = db.get(ip)
    db.close()
    return record

# Extracts relevant information from the MaxMind record
def get_mmdb_info(record):
    info = ""
    if "city" in record:
        info += "City: " + get_name(record["city"]["names"]) + "\n"
    if "country" in record:
        info += "Country: " + get_name(record["country"]["names"]) + "\n"
    if "subdivisions" in record:
        info += "Subdivisions:\n"
        for subdivision in record["subdivisions"]:
            info += "- " + get_name(subdivision["names"]) + "\n"
    if "autonomous_system_number" in record:
        info += "Autonomous System Number: " + str(record["autonomous_system_number"]) + "\n"
    if "autonomous_system_organization" in record:
        info += "Autonomous System Organization: " + record["autonomous_system_organization"] + "\n"
    return info

# Exports results to an Excel file
def export_results(date, ip, file_name, change_detected, change_fields, change_date):
    columns = ["IP", "Date From", "Date To", "ISP Organization", "ASN Number", "City", "Province", "Region", "Country"]
    data = []

    maxmind_file_before, maxmind_file_after, dbip_file = get_mmdb_files(date)
    maxmind_record_before = get_mmdb_record(maxmind_file_before, ip)
    maxmind_record_after = get_mmdb_record(maxmind_file_after, ip)
    dbip_record = get_mmdb_record(dbip_file, ip)
    
    ip = ip
    maxmind_file_before_name = os.path.splitext(os.path.basename(maxmind_file_before))[0]
    maxmind_file_after_name = os.path.splitext(os.path.basename(maxmind_file_after))[0]
    date_from = maxmind_file_before[38:46]
    date_to = maxmind_file_after[38:46]
    isp = dbip_record["autonomous_system_organization"]
    asn = dbip_record["autonomous_system_number"]

    # Get location information
    city = get_name(maxmind_record_before.get("city", {}).get("names", {}))
    province = get_name(maxmind_record_before.get("subdivisions", [])[1].get("names", {})) if len(maxmind_record_before.get("subdivisions", [])) >= 2 else "Unknown"
    region = get_name(maxmind_record_before.get("subdivisions", [])[0].get("names", {})) if len(maxmind_record_before.get("subdivisions", [])) >= 1 else "Unknown"
    country = get_name(maxmind_record_before.get("country", {}).get("names", {}))

    # Add data to the list
    data.append([ip, date_from, date_to, isp, asn, city, province, region, country])

    # Create a DataFrame and export to Excel
    df = pd.DataFrame(data, columns=columns)

    writer = pd.ExcelWriter(file_name)
    df.to_excel(writer, index=False)
    writer.save()

def get_field_value(record, field):
    # Function to get the value of a specific field in the record
    value = None
    if field == "city":
        try:
            value = get_name(record["city"]["names"])
        except KeyError:
            value = None
    elif field == "country":
        try:
            value = get_name(record["country"]["names"])
        except KeyError:
            value = None
    elif field == "subdivisions":
        try:
            value = [get_name(subdivision["names"]) for subdivision in record["subdivisions"]]
        except KeyError:
            value = None
    elif field == "autonomous_system_number":
        try:
            value = record["autonomous_system_number"]
        except KeyError:
            value = None
    elif field == "autonomous_system_organization":
        try:
            value = record["autonomous_system_organization"]
        except KeyError:
            value = None
    return value

def compare_records(record1, record2):
    # Function to compare two records and return fields with differences
    fields = ["city", "country", "subdivisions", "autonomous_system_number", "autonomous_system_organization"]
    differences = []
    for field in fields:
        value1 = get_field_value(record1, field)
        value2 = get_field_value(record2, field)
        if value1 != value2:
            differences.append(field)
    return differences

def estimate_change_date(date, ip, current_record):
    # Function to estimate the date when a change in record occurred based on geolocation data
    date = datetime.datetime.strptime(date, "%Y%m%d")
    change_date = None
    closest_file = None
    closest_date = None

    for file in os.listdir("DownloadedFiles/MaxMind/"):
        if file.startswith("GeoLite2-City_"):
            file_path = os.path.join("DownloadedFiles/MaxMind/", file)
            file_name = os.path.basename(file_path)
            file_date = file_name[14:22]
            file_date = datetime.datetime.strptime(file_date, "%Y%m%d")
            if file_date < date:
                record = get_mmdb_record(file_path + "/GeoLite2-City.mmdb", ip)
                differences = compare_records(record, current_record)
                if differences:
                    if not closest_file or file_date > closest_date:
                        closest_file = file_path + "/GeoLite2-City.mmdb"
                        closest_date = file_date

    if closest_file and closest_date:
        change_date = closest_date.strftime("%Y%m%d")

    return change_date

def ip2int(ip):
    # Function to convert an IP address to an integer
    return int(''.join(['{:08b}'.format(int(x)) for x in ip.split('.')]), 2)

def int2ip(ip_int):
    # Function to convert an integer back to an IP address
    return '.'.join([str((ip_int >> (8 * i)) & 255) for i in range(3, -1, -1)])

def query_ip2location(cur, ip_int):
    # Function to query IP location data from the database
    # Search for an exact match
    sql = "SELECT * FROM PXLocation WHERE ip_from <= ? AND ip_to >= ?"
    cur.execute(sql, (ip_int, ip_int))
    row = cur.fetchone()
    
    if row:
        return row, "exact"
    
    # Search for the closest range below the IP
    cur.execute("SELECT * FROM PXLocation WHERE ip_to < ? ORDER BY ip_to DESC LIMIT 1", (ip_int,))
    lower_range = cur.fetchone()
    
    # Search for the closest range above the IP
    cur.execute("SELECT * FROM PXLocation WHERE ip_from > ? ORDER BY ip_from ASC LIMIT 1", (ip_int,))
    upper_range = cur.fetchone()
    
    # Return the closest range
    if lower_range and (not upper_range or ip_int - lower_range[1] <= upper_range[0] - ip_int):
        return lower_range, "lower"
    elif upper_range:
        return upper_range, "upper"
    else:
        return None, "not_found"

def main(mode, date, ip):
    if mode == "Proxy" or mode == "both":
        file = f"Databases/{date[:4]}{date[4:6]}_IP2Location.db"
        try:
            conn = sqlite3.connect(file)
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")
            sys.exit()

        cur = conn.cursor()
        ip_int = ip2int(ip)

        row2, match_type = query_ip2location(cur, ip_int)
        
        if row2:
            if match_type == "exact":
                print(f"Details of the IP {ip}'s hiding service according to the database:")
            elif match_type == "lower":
                print(f"No exact information was found for IP {ip}. Using the closest range below:")
                print(f"IP Range: {int2ip(row2[0])} - {int2ip(row2[1])}")
            elif match_type == "upper":
                print(f"No exact information was found for IP {ip}. Using the closest range above:")
                print(f"IP Range: {int2ip(row2[0])} - {int2ip(row2[1])}")
            
            print(f"Proxy Type: {row2[2]}")
            print(f"Country: {row2[4]}")
            print(f"Country Code: {row2[3]}")
            print(f"Region: {row2[5]}")
            print(f"City: {row2[6]}")
            print(f"ISP: {row2[7]}")
            print(f"Domain: {row2[8]}")
            print(f"Usage Type: {row2[9]}")
            print(f"ASN: {row2[10]}")
            print(f"Last Seen: {row2[11]}")
            print(f"Threat: {row2[12]}")
            print(f"Residential: {row2[13]}")
            print(f"Provider: {row2[14]}")
        else:
            print(f"No location-hiding or location-modifying service was found for IP {ip} in the database.")

        data = {
            "PXLocation": {
                "Match Type": [],
                "IP Range": [],
                "Proxy Type": [],
                "Country": [],
                "Country Code": [],
                "Region": [],
                "City": [],
                "ISP": [],
                "Domain": [],
                "Usage Type": [],
                "ASN": [],
                "Last Seen": [],
                "Threat": [],
                "Residential": [],
                "Provider": []
            }
        }

        if row2:
            data["PXLocation"]["Match Type"].append(match_type)
            data["PXLocation"]["IP Range"].append(f"{int2ip(row2[0])} - {int2ip(row2[1])}")
            data["PXLocation"]["Proxy Type"].append(row2[2])
            data["PXLocation"]["Country"].append(row2[4])
            data["PXLocation"]["Country Code"].append(row2[3])
            data["PXLocation"]["Region"].append(row2[5])
            data["PXLocation"]["City"].append(row2[6])
            data["PXLocation"]["ISP"].append(row2[7])
            data["PXLocation"]["Domain"].append(row2[8])
            data["PXLocation"]["Usage Type"].append(row2[9])
            data["PXLocation"]["ASN"].append(row2[10])
            data["PXLocation"]["Last Seen"].append(row2[11])
            data["PXLocation"]["Threat"].append(row2[12])
            data["PXLocation"]["Residential"].append(row2[13])
            data["PXLocation"]["Provider"].append(row2[14])

        today = datetime.date.today()
        today_str = today.strftime("%Y%m%d")
        file_name = f"{today_str}_PX_{ip}.xlsx"
        
        df = pd.DataFrame(data["PXLocation"])
        df.to_excel(file_name, sheet_name="PXLocation", index=False)

        conn.close()
        print(f"The results have been saved to the file {file_name}.")

    if mode == "Geolocation" or mode == "both":
        today = datetime.date.today()
        today_str = today.strftime("%Y%m%d")

        file_name = f"{today_str}_{ip}.xlsx"

        maxmind_file_before, maxmind_file_after, dbip_file = get_mmdb_files(date)
        maxmind_record_before = get_mmdb_record(maxmind_file_before, ip)
        maxmind_record_after = get_mmdb_record(maxmind_file_after, ip)
        dbip_record = get_mmdb_record(dbip_file, ip)
        # Check if the before and after files are the same
        same_file = (maxmind_file_before == maxmind_file_after)

        change_detected = False
        change_date = None
        change_fields = []

        # Only compare with the earlier file if they are different
        if not same_file:
            differences_maxmind = compare_records(maxmind_record_before, maxmind_record_after)
            if differences_maxmind:
                change_detected = True
                change_fields.extend(differences_maxmind)

        differences_dbip = compare_records(dbip_record, maxmind_record_after)
        if differences_dbip:
            change_detected = True
            change_fields.extend([field for field in differences_dbip if field not in change_fields])

        if change_detected:
            change_date = estimate_change_date(date, ip, maxmind_record_after)
            if change_date:
                print(f"The estimated change date is {change_date}.")
            else:
                print(f"Could not estimate the date of the change.")
        else:
            print(f"No change in the location or Internet provider of IP {ip} was detected between {date} and {today_str}.")

        # Retrieve information again to avoid unnecessary reprocessing
        maxmind_file_before, maxmind_file_after, dbip_file = get_mmdb_files(date)
        maxmind_record_before = get_mmdb_record(maxmind_file_before, ip)
        maxmind_record_after = get_mmdb_record(maxmind_file_after, ip)
        dbip_record = get_mmdb_record(dbip_file, ip)
        maxmind_info_before = get_mmdb_info(maxmind_record_before)
        maxmind_info_after = get_mmdb_info(maxmind_record_after)
        dbip_info = get_mmdb_info(dbip_record)

        maxmind_file_before_date = maxmind_file_before[38:46]
        maxmind_file_after_date = maxmind_file_after[38:46]
        dbip_file_date = dbip_file[36:42]
        
        print(f"IP information obtained on {maxmind_file_before_date}:\n"
            f"{maxmind_info_before}\n"
            f"IP information obtained on {maxmind_file_after_date}:\n"
            f"{maxmind_info_after}\n"
            f"ISP information obtained on {dbip_file_date}:\n"
            f"{dbip_info}")

        export_results(date, ip, file_name, change_detected, change_fields, change_date)

        print(f"The results have been saved to the file {file_name}.")

    else:
        print("Invalid mode. It must be either Proxy or Geolocation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obtain geographic information of an IP from different databases.")
    parser.add_argument("--mode", choices=["Proxy", "Geolocation", "both"], default="both", help="Search mode: Proxy, Geolocation, or both")
    parser.add_argument("date", help="Date in YYYYMMDD format")
    parser.add_argument("ip", help="IP address")
    args = parser.parse_args()
    main(args.mode, args.date, args.ip)
