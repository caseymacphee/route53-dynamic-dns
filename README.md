# route53-dynamic-dns

This project uses boto3 and expects the aws credentials have been configured on the host.

Set your custom variables in the update_ddns.py file:
HOSTED_ZONE_ID=""
NAME=""
TYPE="A"
TTL=60

This python script is mean to be ran at a regular interval. First it checks the current public ip address using an aws provided endpoint. There is a cache file that the script uses for storing the route53 value for the given NAME and TYPE and HOSTED_ZONE_ID which are configurable. If the cache doesn't exist it will go and fetch the current value from route53 and store it in the cache. If the cached value was last updated before the cache ttl it will fetch again. If the current IP is different than the route53 value it will update in route53 and the cache.

