# IPGeoTrack

## Overview

IPGeoTrack is an advanced Python-based tool designed to retrieve geographic and proxy information for IP addresses from multiple databases, including MaxMind and DB-IP. This project facilitates in-depth analysis and monitoring of IP addresses, becoming an invaluable resource for cybersecurity professionals, network administrators, and researchers.


## Open Bot Availability

Based on the presented code, an open bot has been developed for anyone interested in utilizing its features. The bot can be accessed at the following link: [https://t.me/IPGeoTrack_bot](https://t.me/IPGeoTrack_bot).

## Utility and Potential

- **Accurate Geolocation**: The tool provides detailed information about the geographic location of IP addresses, which is crucial for tracking the origin of cybercriminal or terrorist activities.
- **Detection of Anonymization Services**: By identifying whether an IP is associated with proxy services, VPNs, or Tor, the tool aids in detecting attempts to conceal attackers' true locations.
- **Historical Analysis**: The ability to query historical information allows researchers to trace patterns of behavior and movements of malicious actors over time.
- **ASN and ISP Identification**: This information can be vital for coordination with service providers in cybercrime investigations.
- **Change Detection**: The functionality to detect and estimate dates of changes in IP information can help identify when an attacker alters their infrastructure.

## Strengths

- **Multiple Data Sources**: By combining information from MaxMind, DB-IP, and IP2Location, the tool offers a more comprehensive and accurate view.
- **Telegram Bot Interface**: It facilitates quick access to information for researchers, even from mobile devices.
- **Temporal Flexibility**: It allows for both current and historical queries, expanding the scope of investigations.
- **Threat Detection**: The inclusion of threat information helps prioritize the investigation of potentially malicious IPs.

## Unique Features

- **Change Date Estimation**: The ability to estimate when the information for an IP changed is a rare and valuable feature for tracking suspicious activities.
- **Integration of Multiple Databases**: Combining different sources into a single query provides a more comprehensive perspective than most similar tools.
- **IP Range Analysis**: The ability to provide information about IP ranges when an exact match is not found can be crucial for identifying broader suspicious networks.

## Installation

To install IPGeoTrack, ensure that you have Python 3.x installed on your machine and follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/N4rr34n6/IPGeoTrack.git
   cd IPGeoTrack
   ```

2. Install the required packages:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Download the necessary database files from MaxMind and DB-IP and place them in the appropriate directories.

## Usage

To run the IPGeoTrack script, use the following command:

```bash
python3 ipgeotrack.py <mode> <date> <IP>
```

Where:
- `<mode>` can be `Proxy`, `Geolocation`, or `both`.
- `<date>` is the desired date in the `YYYYMMDD` format.
- `<IP>` is the target IP address to query.

### Example

```bash
python3 ipgeotrack.py Geolocation 20240901 169.150.218.58
```

**Expected Output:**
```
No exact information found for IP 169.150.218.58. Using the closest range:
IP Range: 169.150.221.198 - 169.150.221.198
Proxy Type: PUB
Country: United States of America
Country Code: US
Region: California
City: San Jose
ISP: DataCamp Limited
Domain: datacamp.co.uk
Usage Type: DCH
ASN: 60068
Last Seen: DataCamp Limited
Threat: 30
Residential: -
Provider: Private Internet Access
Information has been saved in the file 20241005_PX_169.150.218.58.xlsx.
The estimated change date is 20221025.
IP information retrieved on 20240830:
City: Amsterdam
Country: Netherlands
Subdivisions:
- North Holland

IP information retrieved on 20240903:
City: Amsterdam
Country: Netherlands
Subdivisions:
- North Holland

ISP information retrieved on 202409:
Autonomous System Number: 212238
Autonomous System Organization: Datacamp Limited

Results have been saved in the file 20241005_169.150.218.58.xlsx.
```

## Technical Details

- **Programming Language**: Python 3.x
- **Dependencies**: 
  - `sqlite3`: For database management
  - `socket`, `struct`: For IP address handling
  - `pandas`: For data manipulation and exporting to Excel
  - `maxminddb`: To query MaxMind database files

## Legal Disclaimer

IPGeoTrack is intended for authorized use only. Users are responsible for complying with applicable laws and regulations related to data privacy and IP tracking. The authors do not endorse any illegal activity or misuse of the tool.

## License

This script is provided under the GNU Affero General Public License v3.0. You can find the full license text in the [LICENSE](LICENSE) file.

## Conclusion

IPGeoTrack stands out in the field of IP geolocation tools, offering unique capabilities and extensive data retrieval options. Its robust architecture and ease of use make it an essential tool for anyone needing accurate and detailed information about IP addresses. Explore the power of IPGeoTrack and enhance your understanding of network behavior today.
