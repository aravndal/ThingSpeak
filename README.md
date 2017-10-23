# ThingSpeak

## Introduction
The ThingSpeak Plugin allows CraftBeerPi 3.0 to send sensor data to ThingSpeak.com

## Add a Channel on ThingSpeak.com
1. Login into you ThingSpeak.com account and add a New Channel
2. Write down your "Channel ID"
3. Write down you "User API Key", found under Account - MyProfile

## Use
1. Download this Plugin from CraftBeerPi 3 Add-On page
2. Under Parameters add your thingspeak_api (User API Key) and thingspeak_chnid (Channel ID)
3. Restart CraftBeerPi

The first eight sensors will be updated to the channel every minute. 
The Channel name will be updated with your brewery name, and fields will get the sensor names.
