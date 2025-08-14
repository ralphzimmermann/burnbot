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

## Deploying with Nginx and HTTPS (Let's Encrypt via DNS validation)

This project ships a single container that runs both the FastAPI backend and serves the built React frontend behind Nginx. The container exposes HTTP on port 80 and HTTPS on port 443. Let's Encrypt certificates are stored on persistent Docker volumes so rebuilds do not erase them.

- Domain: `burnbot.thehealthwarriors.net`
- Volumes: certificates at `/etc/letsencrypt` and logs at `/var/log/letsencrypt`

### Prerequisites

- Ability to create a DNS TXT record for the domain (DNS-01 validation). For automation with Route 53, have AWS credentials ready.
- Set environment variables (see `website/backend/.env.example`) including a strong `SECRET_KEY`.

### Start the stack

```bash
cd <repo-root>
docker compose up -d --build
```

The app will be available at `http://localhost` immediately. Once certificates are issued, restart or reload Nginx to switch to HTTPS and then use `https://burnbot.thehealthwarriors.net`.

### Generate Let's Encrypt certificates (DNS-01)

Because the server is not publicly accessible, use DNS validation. You have two options:

- Manual DNS (works with any DNS provider): create a TXT record when prompted.
- Provider plugin (optional): if your DNS provider has a Certbot plugin and API token, you can automate issuance. An example for Cloudflare is provided, but not required.

#### Option A: Manual DNS (no provider dependency)

```bash
CONTAINER=$(docker compose ps -q eventguide)
docker exec -it "$CONTAINER" /bin/sh -c "/certbot-dns-manual.sh burnbot.thehealthwarriors.net"
```

Follow the prompts to add the `_acme-challenge.burnbot.thehealthwarriors.net` TXT record in your DNS, wait for propagation, then continue. On success, certs are stored in `/etc/letsencrypt/live/burnbot.thehealthwarriors.net/` and will persist via the Docker volume.

Reload Nginx (switches to HTTPS if certs are present):

```bash
docker exec "$CONTAINER" nginx -s reload
```

#### Option B: Using a DNS provider plugin (Route 53)

1. Provide AWS credentials to the container (any of these):
   - Export in your shell before `docker compose up`: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
   - Or add them to `website/backend/.env` which is referenced by `docker-compose.yml`.
2. Issue the cert:
   ```bash
   CONTAINER=$(docker compose ps -q eventguide)
   docker exec -it "$CONTAINER" /bin/sh -c "/certbot-dns-route53.sh burnbot.thehealthwarriors.net"
   docker exec "$CONTAINER" nginx -s reload
   ```

### Renewal

Certificates are valid for 90 days. To renew non-interactively (recommended monthly):

```bash
CONTAINER=$(docker compose ps -q eventguide)
docker exec "$CONTAINER" certbot renew --quiet
docker exec "$CONTAINER" nginx -s reload
```

You can automate this via a host cron job.

### Files and scripts

- `website/nginx/app.conf`: Nginx reverse proxy (80 → redirect to 443; 443 → proxy to Uvicorn 8000)
- `website/nginx/start.sh`: Entrypoint that starts Uvicorn and Nginx; generates a temporary self-signed cert if Let's Encrypt certs are not present.
- `certbot-dns-route53.sh`: Helper script to request DNS-validated certs using the Route 53 plugin.
- `certbot-dns-manual.sh`: Manual DNS flow that works with any DNS provider.

### Security notes

- Keep your AWS credentials secure. Prefer least-privilege IAM users limited to Route 53 DNS changes for the specific hosted zone.
- Volumes `letsencrypt` and `letsencrypt-logs` persist across rebuilds.
- Consider restricting Nginx to TLS 1.2/1.3 only (already configured).
