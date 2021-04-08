import json
import ipaddress
from pathlib import Path
import os

import arrow
import boto3
import requests

#Variable Declaration - Change These
HOSTED_ZONE_ID=""
NAME=""
TYPE="A"
TTL=60

VALUE_TMP_FILE = "/tmp/current_route53_value.json"
CACHE_TTL = 86400



client = boto3.client('route53')

current_ip_resp = requests.get('http://checkip.amazonaws.com/')
validated_current_ip = ipaddress.ip_address(current_ip_resp.text.rstrip())
current_ip = str(validated_current_ip)


def get_route53_value():
    resp = client.list_resource_record_sets(HostedZoneId=HOSTED_ZONE_ID)
    found = False
    for record_set in resp['ResourceRecordSets']:
        if record_set['Name'] == NAME and record_set['Type'] == TYPE:
            found = True
            route53_value = record_set['ResourceRecords'][0]['Value']
            break
    if not found:
        print("hosted zone record matching name not found")
        exit()
    return route53_value


def update_cache(route53_value, updated_at):
    with open(VALUE_TMP_FILE, 'w') as file:
        new_cached_data = {'ip': route53_value, 'last_updated': str(updated_at)} 
        json.dump(
            new_cached_data, file)
        return new_cached_data


if not os.path.exists(VALUE_TMP_FILE):
    print("generating route53 value cache file")
    Path(VALUE_TMP_FILE).touch()

with open(VALUE_TMP_FILE, 'r') as value_tmp_file:
    try:
        cached_data = json.load(value_tmp_file)
    except json.decoder.JSONDecodeError:
        cached_data = None
        

# if there is no current data, check and update the local file cache
if not cached_data:
    print("no currently cached route53 value, checking...")
    route53_value = get_route53_value()
    cached_data = update_cache(route53_value, arrow.utcnow())
else:
    # check to see if the last updated cached value of the route53 value has expired
    # and update if necessary
    cache_expiration = arrow.utcnow().shift(seconds=-CACHE_TTL)
    if arrow.get(cached_data['last_updated']) <= cache_expiration:
        print("Cached route53 value ttl expired, rechecking...")
        route53_value = get_route53_value()
        cached_data = update_cache(route53_value, arrow.utcnow())
    else:
        route53_value = cached_data['ip']

if current_ip != route53_value:
    # Update the route53 value and save the data locally on success
    change_set = {
        'Comment': 'Updating value to match current IP at: {}'.format(arrow.utcnow()),
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': NAME,
                    'Type': TYPE,
                    'TTL': TTL,
                    'ResourceRecords': [
                        {
                            'Value': current_ip
                        }
                    ]
                }
            }
        ]
    }
    # if this fails then the cache won't be updated and it should retry
    client.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch=change_set
    )
    update_cache(current_ip, arrow.utcnow())
    print("Updated the Route53 record with the current ip and cached new record value")
else:
    print("Route53 and the current IP are in sync")





