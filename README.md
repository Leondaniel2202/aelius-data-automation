# Aelius Data Automation

Small Python scripts for Aelius data and process automation.

## Current scope

The first proof of concept is a manually triggered WhatsApp sender for the Mentee Zwischenbericht workflow.

Planned first script:

- read the `Mentees` table in SeaTable
- select rows where a phone number exists
- only include rows where `Zwischenbericht verschickt` is not checked
- require a Mentee ID for the personalized form link
- preview the recipients before sending
- require manual confirmation
- send the WhatsApp message
- mark `Zwischenbericht verschickt` only after a successful send

The script is intentionally manual for now. No scheduler or background automation is included yet.
