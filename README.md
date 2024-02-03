## Simple Script to notify when cetrain World Quests are up.

Data is yoinked from WoWHead.


## Setup:


- in Discord: go to any channel and add a new Webhook
- `export WEBHOOK_URL="url_to_the_webhook"`
- in `main.py` adjust `WORLD_QUESTS` as needed

- setup a cronjob or simlar like:
  Note: I'm not sure how fast wowhead updates the data... so I decided to delay the
  cronjob by 15min, rather than running it exactly on the hour.
```cron
15 * * * * ~/dev/wow_notifications/run.sh
```

