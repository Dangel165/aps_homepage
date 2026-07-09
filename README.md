# APS Homepage

## Local Server

Double-click `run_server.bat`, or run:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000/
```

## GitHub Pages

GitHub Pages cannot run Flask directly, so export the site as static files:

```powershell
python -m pip install -r requirements.txt
python export_static.py
```

The static site is generated in `docs/`.

After GitHub CLI login, deploy with:

```powershell
gh auth login -h github.com
deploy_pages.bat
```
