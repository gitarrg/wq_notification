## Simple Script to notify when cetrain World Quests are up.

Data is yoinked from Wowhead. ty ♥


## Setup:


- in Discord: go to any channel and add a new Webhook

- edit `run.sh`:
    ```sh
    export WEBHOOK_URL="url_to_the_webhook"`
    ```

- edit  `main.py` and adjust `WORLD_QUESTS` as needed

- setup a cronjob or simlar:
  ```cron
  15 * * * * ~/dev/wow_notifications/run.sh
  ```
  *Note: I'm not sure how fast wowhead updates the data... so I decided to delay the
  cronjob by 15min, rather than running it exactly on the hour.*

