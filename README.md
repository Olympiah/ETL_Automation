# ETL_Automation

An automated ETL pipeline that extracts video metadata from a YouTube playlist using the YouTube Data API, transforms it into structured data, and loads it into a repository. This project demonstrates how GitHub Actions can be leveraged to automate ETL workflows.

### Project Overview
---
The goal of this project is to:

- Automate repetitive ETL tasks using GitHub Actions.

- Keep video index files up-to-date with minimal manual intervention.

- Experiment with cross-platform automation (Ubuntu vs Windows runners).

This project also served as a hands-on exploration of CI/CD automation, YAML workflow configuration, and integrating with external services.

### ⚙️ Tech Stack
---

- Python – core ETL logic (data_pipeline.py, functions.py)

- Polars – fast DataFrame operations

- LangChain Google GenAI Embeddings – for text embeddings

- YouTube Data API & YouTube PlaylistItems API

- GitHub Actions – CI/CD automation


### ✨ Features

---

- Automated ETL pipeline triggered via GitHub Actions.

- CI/CD workflows on multiple OS runners (ubuntu-latest, windows-latest).

- Automatic commits and pushes back to the repository.

- Integration with LangChain GenAI for advanced processing (until quota got maxed out 😅).

### How to Run
---
*Locally*

Clone the repository:
```

git clone https://github.com/Olympiah/ETL_Automation.git
cd ETL_Automation

```

Install dependencies:

```
pip install -r requirements.txt

```

Set environment variables (e.g., via .env):
```
YT_API_KEY=<your_api_key>
PLAYLIST_ID=<your_playlist_id>
GOOGLE_API_KEY=<your_google_key>

```

Run the pipeline:

```
python data_pipeline.py

```

### Via GitHub Actions 

Make sure your repo’s Settings → Secrets include:

- YT_API_KEY

- PLAYLIST_ID

- GOOGLE_API_KEY

On push or schedule, Actions picks these up and runs the pipeline automatically.

### Troubleshooting & Lessons Learned

---

1. Windows Runner Failures : The workflow runs smoothly on ubuntu-latest, but Windows (windows-latest) fails on commands like `git diff … vecause nn windows-latest, the default shell is PowerShell (pwsh).
2. Infinite Workflow Loops : Auto-commit logic can trigger itself over and over. Solved by adding filters in workflow or using [skip ci] in commit messages.
3. API Quota Reached	     : LangChain GenAI embeddings hit their quota — after that, the pipeline stages involving embeddings fail and can’t be resolved with YAML tweaks alone.

### Useful Links

---

<a href='https://www.google.com/search?q=can+you+use+someone+elses+youtube+channel+id++to+get+videos+and+api+key&sca_esv=1c2c48b035966a68&rlz=1C1CHBD_enKE953KE953&ei=ed-laOz-HLjtkdUPxYK56Qg&ved=0ahUKEwisn82p0JmPAxW4dqQEHUVBLo0Q4dUDCBA&uact=5&oq=can+you+use+someone+elses+youtube+channel+id++to+get+videos+and+api+key&gs_lp=Egxnd3Mtd2l6LXNlcnAiR2NhbiB5b3UgdXNlIHNvbWVvbmUgZWxzZXMgeW91dHViZSBjaGFubmVsIGlkICB0byBnZXQgdmlkZW9zIGFuZCBhcGkga2V5SLcmUN4CWPQjcAF4AZABAJgBuwKgAeQ0qgEGMi0yNS4yuAEDyAEA-AEBmAIRoAKSIsICChAAGLADGNYEGEfCAgcQIRigARgKwgIFECEYnwWYAwCIBgGQBgiSBwgxLjAuMTQuMqAHtnCyBwYyLTE0LjK4B_8hwgcHMC4zLjkuNcgHaA&sclient=gws-wiz-serp#fpstate=ive&vld=cid:2d8bbea1,vid:GwTcTQxZ9Xw,st:0'>Link to youtube channel showing you how to access YouTube channel ID</a>

<a href='https://google-api-client-libraries.appspot.com/documentation/youtube/v3/python/latest/youtube_v3.playlistItems.html'>Link to more info about Youtube Playlist items (Python)</a>
