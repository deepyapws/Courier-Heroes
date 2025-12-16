# CourierTracker — Web UI

This adds a small Flask web UI that uses the existing `unified.py` tracker to search for package status.

Quick start (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
# then open http://127.0.0.1:5000/ in your browser
```

Notes:
- The UI sends a POST to `/api/track` with JSON `{ "tracking_number": "..." }` and shows the returned JSON.
- `unified.py` performs HTTP requests to courier websites; network access is required.

UI improvements:
- The web UI now uses Bootstrap for a cleaner layout and displays results in nicely formatted cards and a table for the event history.

Debugging tips

Example (PowerShell using curl):
```powershell
curl -X POST -H "Content-Type: application/json" -d '{"tracking_number":"363136094640","debug":true}' http://127.0.0.1:5000/api/track
```

When `debug` is true the JSON response will include `_debug` with a `raw` field containing the HTML/JSON returned by the courier page, which helps inspect parsing problems.
When `debug` is true the JSON response will include `_debug` with helpful fields:

- `raw`: the full text returned by the courier page (may be large)
- `snippet`: the first part of the response (for quick viewing)
- `status_code` and `headers`: HTTP metadata
- `attempts`: list of decoding/extraction attempts and their lengths
- `used`: which candidate (requests text / utf8 / cp949) successfully parsed

This helps diagnose encoding issues or identify where the embedded JSON is located in the page.

From the UI, check the **Show debug** box before submitting to view the debug output directly under the results.

Watchlist / Tracked numbers
---------------------------
You can keep a watchlist of tracking numbers in the UI. Use the input below the search form to add a tracking number to your watchlist.

- **Add**: enter a tracking number in the "Add tracking number to watchlist" input and click Add.
- **Check**: click "Check" on a tracked item to fetch and store the latest status for that number.
- **Check All**: click the "Check All" button to refresh every saved tracking number.
- **Remove**: click Remove to delete a tracking number from your watchlist.

The watchlist is persisted to a local SQLite database file (`tracked.db`) in the project folder and includes the last fetched result and timestamp.

Also useful:
- Open the browser devtools → Network to see what the frontend sent and the returned response.
- Start the Flask app with `DEBUG` logging: set `debug: true` in the API payload or set `logger` level in `app.py`.

If you'd like changes to the UI (colors, logo, or more fields), tell me what style you're aiming for and I can adjust it.
