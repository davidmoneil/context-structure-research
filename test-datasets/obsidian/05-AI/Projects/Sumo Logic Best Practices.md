---
created: 2025-05-15T13:11
modified: 2025-05-23T16:31
updated: 2026-01-23T20:44
tags:
  - artifact/item
  - depth/quick
  - domain/mechanics
  - depth/standard
  - project/tweenagers
---
## If Statements 
| if(isBlank(first_xff_ip), external_ip, first_xff_ip) as external_ip

## Parse a parsed field 
| json field=_raw "req.headers.x-forwarded-for" as xff noDrop // WAF Log
| parse regex field=xff "^(?<first_xff_ip>[^,]+)" nodrop

## Not Contains 
| where !contains (field, "text")


## General
**LowerCase**
`toLowerCase(field) contains "lower_case_text"`
### Is Null 
isNull(var)
## IP  Info

### Regex Two IPs 
| parse regex "(?<ip_address1>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
| parse regex "(?<ip_address2> \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

### Valide IP 
| isValidIPv4(src_ip) as isIP

### finds low and high of ip from cidr
| min(pIP), max(pIP)

### Private IP 
| isPrivateIP(src_ip) as pIP
### **IP to GEO Location**
`| lookup latitude, longitude, continent, country_code, country_name, region, city, state, postal_code, connection_type from geo://location on ip = %"ip"`
`| lookup organization, registering_organization, carrier_organization, asn from asn://default on ip = %"ip"`

### **Threat IP**
`// This section returns Actor, malicious_confidence, raw_threat, type from https://help.sumologic.com/docs/search/search-query-language/search-operators/threatip/`
`| threatip ip`
`| order by _time`
