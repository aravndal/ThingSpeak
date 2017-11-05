# ThingSpeak

## Introduction
The ThingSpeak Plugin allows CraftBeerPi 3.0 to send sensor data to ThingSpeak.com and Ubidots.com  
NEW: Added integration with Ubidots.com

## Add a Channel on ThingSpeak.com
1. Login to your ThingSpeak.com account
2. Write down you "User API Key", found under Account - MyProfile
3. Add a New Channel and save (do not update any fields)
4. Write down your "Channel ID", on the main page or channel settings

## Add a Device on Ubidots.com
1. Login to your Ubidots.com account
2. Write down you "Default token", found under Your Name - API Credentials
3. Add a New Device and write down your "API Label"

## Use
1. Download this Plugin from CraftBeerPi 3 Add-On page
2. Under Parameters add your thingspeak_api (User API Key) and thingspeak_chnid (Channel ID)
3. to use with Ubidots add your API Token (ubidots_token) and Device Label (ubidots_label)
4. Restart CraftBeerPi

The first eight sensors will be updated to the channel every minute. 
On Thingspeak will your channel name will be updated with your brewery name, and fields will get the sensor names.
For ubidots will actors and target temperature be uploaded too.
