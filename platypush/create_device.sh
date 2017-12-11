#!/bin/bash

API_TOKEN='o.EHMMnZneJdpNQv9FSFbyY2busin7floe'

curl --header "Access-Token: $API_TOKEN" \
     --header 'Content-Type: application/json' \
     --data-binary '{"app_version":8623,"manufacturer":"RaspberryPi","model":"RaspberryPi 3","nickname":"turing","icon":"system","has_sms":false}' \
     --request POST \
     https://api.pushbullet.com/v2/devices

# Copy "iden" from the response as your device identifier

