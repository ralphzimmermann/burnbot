Burn Master - Burning Man Events Guide


I want to create a website that allows to browse events for a festival based on categories and allows a simple keyword search.

The system should have 2 parts
- Data-collector 
- Website

The data collector should use a webcrawler to download the data from a website and then convert all the data into a json file. Let's see how big that file is and then go an decide how if we can load that into the frontend all together or we have to use a backend database.


# Data Collector

Write a service in python (script) that does the following


Download the index files from the following urls

https://playaevents.burningman.org/2025/playa_events/01
https://playaevents.burningman.org/2025/playa_events/02
https://playaevents.burningman.org/2025/playa_events/03
https://playaevents.burningman.org/2025/playa_events/04
https://playaevents.burningman.org/2025/playa_events/05
https://playaevents.burningman.org/2025/playa_events/06
https://playaevents.burningman.org/2025/playa_events/07
https://playaevents.burningman.org/2025/playa_events/08

Each of the index files has urls in a structure like this

https://playaevents.burningman.org/2025/playa_event/53931/

so it's basically https://playaevents.burningman.org/2025/playa_event/{event_id}/

That means we just need to extract the event_id from the index files.

Download all the event data into a structured file "events.json"

The event json should have a structure like this

{
    times:  [ /* list of dates with start_time/time 
                    Sample string that we need to parse: "Sunday, August 24th, 2025, 12 AM – 11:45 PM" */
        {
            date: "{date in a standard format e.g MM/DD/YYYY}",
            start_time: "HH:MM", /* we don't need timezones! */
            end_time: "HH:MM"
        }
    ],
    type: "<type of event>",
    camp: "<camp of event>",
    campurl:  "<camp url from the camp link in the document>",
    location: "<location of event>",
    description: "<description of event>"       
}

Put the script into the "data-collector" directory. Start by download a sample index file and a sample event file so that you can an understand of the files than iterate on the download script until we can get all the data for the events. 

This should be a very simple program. Use YAGNI principles. We are not going to run this in docker or on a server. This is just a program we use locally for the data extractions.