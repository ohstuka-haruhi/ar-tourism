# AR Tourism Guide – Yamadera

Browser-based AR tourism demo for the Risshakuji (山寺) temple complex in Yamagata, Japan.
Displays GPS-anchored text overlays when the user is near a registered location.

## Files

| File | Purpose |
|------|---------|
| `index.html` | AR viewer (main app) |
| `admin.html` | Spot management panel |
| `spots.json` | Seed data – 4 demo spots |

## Quick Start

Camera and Geolocation APIs require **HTTPS** (or `localhost`).
Pick one method below.

---

### Option A – ngrok (recommended for mobile testing)

```bash
# 1. Serve locally (Python built-in)
python3 -m http.server 8080

# 2. In a second terminal, expose via ngrok
ngrok http 8080
```

Open the `https://…ngrok-free.app` URL on your phone.

---

### Option B – local-ssl-proxy

```bash
npm install -g local-ssl-proxy

# Serve files
python3 -m http.server 8080

# Proxy with self-signed TLS
local-ssl-proxy --source 8443 --target 8080
```

Then open `https://localhost:8443` (accept the certificate warning).

---

### Option C – VS Code Live Server + ngrok

1. Install the **Live Server** extension.
2. Right-click `index.html` → *Open with Live Server* (port 5500).
3. Run `ngrok http 5500` and open the HTTPS URL.

---

## Device Notes

### iOS Safari
- Tap **Allow** when Safari asks for camera and location.
- On iOS 13+, device orientation (compass) requires a user gesture to unlock.
  The app handles this automatically on the first tap.
- Tested: Safari 16+, iOS 15+.

### Android Chrome
- Grant camera and location permissions when prompted.
- Enable **High Accuracy** location mode in Android Settings for best GPS.
- Tested: Chrome 112+, Android 11+.

---

## AR Behaviour

| Condition | Behaviour |
|-----------|-----------|
| Inside spot radius | AR card rendered over camera feed |
| Outside radius | Spot hidden from AR; visible in bottom chip list |
| GPS denied | Distance unknown; all spots shown in chip list and list view |
| Camera denied | Fallback list view displayed automatically |

### Testing without visiting Yamadera

**Browser GPS spoof (Chrome DevTools)**

1. Open DevTools → ⋮ → *More tools* → *Sensors*.
2. Under *Location*, select **Custom location**.
3. Enter: `Latitude 38.3165` · `Longitude 140.4493`.
4. Reload the page — spots will appear within their detection radii.

**Note:** AR.js requires a real device with compass and camera for
the directional overlay to work correctly. On desktop you will see
the entity list but not a live camera feed.

---

## Admin Panel

Open `admin.html` in any browser (no HTTPS required for admin).

- **Add Spot** – fill the form; click the map or enter coordinates manually.
- **⌖ My Location** – fills lat/lng from your device's GPS.
- **Edit / Delete** – inline table actions.
- **Export JSON** – downloads current spots as `spots.json`.
- **Import JSON** – replaces all spots from a `.json` file.

Spots are persisted in `localStorage` under the key `arSpots`.
Both `index.html` and `admin.html` share the same key, so changes
in admin are reflected immediately in the AR viewer on the same device.

---

## Spot Data Format

```json
{
  "id": "unique-string",
  "category": "gate | warning | viewpoint | wildlife",
  "lat": 38.3165,
  "lng": 140.4493,
  "radius": 50,
  "name":        { "en": "…", "jp": "…", "zh": "…" },
  "description": { "en": "…", "jp": "…", "zh": "…" }
}
```

`radius` sets the GPS detection distance in metres (default: 50).

---

## Tech Stack

- **A-Frame 1.4** – WebXR scene graph
- **AR.js 3.4.5** – Location-based AR (GPS + compass)
- **Web Geolocation API** – `watchPosition` for real-time tracking
- **Leaflet 1.9** – admin coordinate picker
- No build step — all dependencies via CDN
