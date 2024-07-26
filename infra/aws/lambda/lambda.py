import boto3
import os
import http.client
import json
import time
from datetime import datetime, timedelta

ip_set_name = os.getenv('IP_SET_NAME')
region = os.getenv('REGION')


def create_ip_set(client):
    """
    Create an IP set.

    :return: Summary of the created IP set
    """
    try:
        response = client.create_ip_set(
            Name=ip_set_name,
            Scope='REGIONAL',
            IPAddressVersion='IPV4',
            Addresses=[]
        )
        print(f"IP set {ip_set_name} created successfully.")
        return response['Summary']
    except Exception as e:
        print(f"Error creating IP set {ip_set_name}: {e}")


def add_ip_to_set(client, ip_set_id, ip_address):
    """
    Add an IP address to an IP set.

    :param ip_set_id: The ID of the IP set
    :param ip_address: The IP address to add
    :return: Response from the update_ip_set API call
    """
    try:
        ip_set = client.get_ip_set(
            Name = ip_set_name,
            Scope='REGIONAL',
            Id=ip_set_id
        )
        addresses = ip_set['IPSet']['Addresses']
        addresses.append(ip_address)

        response = client.update_ip_set(
            Name= ip_set_name,
            Scope='REGIONAL',
            Id=ip_set_id,
            Addresses=addresses,
            LockToken=ip_set['LockToken']
        )
        print(f"IP address {ip_address} added to IP set {ip_set_name}.")
        return response
    except Exception as e:
        print(f"Error adding IP address {ip_address} to IP set {ip_set_name}: {e}")


def initialize_waf_client():
    """
    Initialize and return a WAFV2 Boto3 client.

    :return: Boto3 WAFV2 client
    """

    return boto3.client('wafv2', region)

def fetch_ioc_data():
    """
    Fetch IOC data from a given API endpoint.

    :param api: The API endpoint URL
    :return: JSON data fetched from the API
    :raises Exception: If the API call fails
    """
    try:
        start_time = datetime.now() - timedelta(days=1)
        start_time = int(start_time.timestamp())
        end_time = int(time.time())

        conn = http.client.HTTPSConnection("irondome.razorpay.com")

        irondome_api = os.getenv('IRONDOME_API_KEY')
        url = "/v1/irondome/iocs?starttime="+str(start_time)+"&endtime="+str(end_time)


        headers = {
        'accept': 'application/json',
        'Authorization': 'Basic ' + irondome_api
        }
        payload = {}
        conn.request("GET", url, payload, headers)

        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            data = data.decode("utf-8")
            data_type = json.loads(data)
            print(f"Successfully fetched IOC data from API")
            return data_type
        else:
            print("Invalid response from Irondome Service, and the status code is " + str(res.status))
    except Exception as e:
        print(f"Error fetching IOC data from API: {e}")




def lambda_handler(event, context):
    # Get WAF Client
    client = initialize_waf_client()

    # Create IPSet if not exists
    create_ip_set(client)

    waf_ip_sets = client.list_ip_sets(Scope="REGIONAL")
    ip_sets = waf_ip_sets["IPSets"]
    for ip_set in ip_sets:
        if ip_set["Name"] == ip_set_name:

            ipset_id = ip_set["Id"]

            # Fetching the IP's from Irondome Service
            irondome_iocs = fetch_ioc_data()
            if irondome_iocs and "response" in irondome_iocs:
                response = irondome_iocs["response"]
                # Collect all the IP's
                ips = [ item["value"] for item in response if item["category"] == "Network activity" ]
                print(len(ips))

                # Add IP's to IPAddress
                add_ip_to_set(client, ipset_id, ips)
            else:
                print("No data from Irondome")
