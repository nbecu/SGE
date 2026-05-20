# Manual Test Scripts

These scripts require a display and manual visual inspection.
They are NOT part of the automated pytest suite (`pytest tests/`).

Run them individually when you need to visually validate specific behaviors:

```powershell
.\venv\Scripts\python.exe tests/manual/test_legend_control_panel_separation.py
.\venv\Scripts\python.exe tests/manual/test_displayTooltip.py
.\venv\Scripts\python.exe tests/manual/test_SGAdminPlayer.py
.\venv\Scripts\python.exe tests/manual/test_complete_admin_super_player.py
.\venv\Scripts\python.exe tests/manual/test_controlPanel_adminPlayer.py
```
