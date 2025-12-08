# MVP - Version 0.1 (12/7/2025- 2-3 weeks)

# Features

- Upload CSV with columns: software_name, install_date, source
- Normalize to: vendor, product, version, edition
- Match agaisnt EOS database(hardcoded products)
- Calculate risk score (days until EOL)
- Display results table

## Tech Stack

- Backend: Python + Flask
- Database: SQLite (no setup)
- Normalization: rapidfuzz + regex
- Frontend: React

## Out of Scope for MVP

- Live Web Scrape
- ML predictions
- Multi user/auth
- Real time updates
- Jira/Slack intergrations
