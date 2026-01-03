### Magic Packet API

## Authors

- Nikita Somenkov (original author)
- Victor Carreon (co-author, (new routes and performance improvements))

#### Common info methods:

##### Server Methods

Set up server for managing internal devices

- Enable this if you dont neccesary want to expose ip address of internal devices

- **Method**: `POST`
- **Request:** `control/server/setup`
- **Added in:** `1.1.1`
- **Return:**

```json
{
  "status": true,
  "message": "Server setup completed successfully."
}
```

---

Store device info, for future retrieve and WoL management

- **Method**: `POST`
- **Request:** `control/device/configure`
- **Added in:** `1.1.1`
- **Input:**

```json
{
  "ip": "192.168.0.0",
  "mac": "00:00:00:00:00:00"
}
```

- **Return:**

```json
{
  "status": true,
  "message": "Device configuration stored successfully."
}
```

---

List stored devices

- **Method**: `GET`
- **Request:** `control/device/list`
- **Added in:** `1.1.1`
- **Return:**

```json
{
  "devices": [
    {
      "config": {},
      "ip": "192.168.0.0",
      "mac": "00-00-00-00-00-00"
    }
  ],
  "status": true
}
```

---

Wakes external devices with WoL package

- **Method**: `POST`
- **Request:** `control/device/wake`
- **Added in:** `1.1.1`
- **Input:**

```json
{
  "mac": "00-00-00-00-00-00"
}
```

- **Return:**

```json
{
  "status": true,
  "message": "Wake-on-LAN packet sent to {mac}."
}
```

##### Client Methods

---

Check version of backend

- **Method**: `GET`
- **Request:** `info/version`
- **Modified in:** `1.1.1`
- **Return:**

```json
{
  "mode_server": true,
  "version": "1.1.1"
}
```

---

Check status of PC

- **Method**: `GET`
- **Request:** `info/status`
- **Modified in:** `1.1.1`
- **Return:**

```json
{
  "children": [
    {
      "ip": "192.168.0.0",
      "status": false
    }
  ],
  "status": true
}
```

#### Controlling power of PC methods:

---

Shutdown PC request

- **Method**: `POST`
- **Request:** `control/shutdown`
- **Modified in:** `1.1.1`
- **Input:**

```json
{
  "timeout": 42
}
```

- **Return:**

```json
{
  "status": true,
  "error": "Some error in error case"
}
```

Or

```json
{
  "message": "Server shutdown is not allowed.",
  "status": false
}
```

---

Reboot PC request

- **Method**: `POST`
- **Request:** `control/reboot`
- **Modified in:** `1.1.1`
- **Input:**

```json
{
  "timeout": 42
}
```

- **Return:**

```json
{
  "status": true,
  "error": "Some error in error case"
}
```

Or

```json
{
  "message": "Server reboot is not allowed.",
  "status": false
}
```

---

Sleep PC request

- **Method**: `POST`
- **Request:** `control/sleep`
- **Modified in:** `1.1.1`
- **Input:**

```json
{
  "timeout": 42
}
```

- **Return:**

```json
{
  "status": true,
  "error": "Some error in error case"
}
```

Or

```json
{
  "message": "Server sleep is not allowed.",
  "status": false
}
```

#### Remote devices control methods:

---

Shutdown request

- **Method**: `POST`
- **Request:** `control/device/shutdown`
- **Added in:** `1.1.1`
- **Input:**

```json
{
  "ip": "192.168.0.0"
}
```

- **Return:**

```json
{
  "status": false,
  "error": "Some error in error case"
}
```

Or

```json
{
  "status": true,
  "message": "Shutdown command sent to {ip}."
}
```

---

Reboot request

- **Method**: `POST`
- **Request:** `control/device/reboot`
- **Added in:** `1.1.1`
- **Input:**

```json
{
  "ip": "192.168.0.0"
}
```

- **Return:**

```json
{
  "status": false,
  "error": "Some error in error case"
}
```

Or

```json
{
  "status": true,
  "message": "Reboot command sent to {ip}."
}
```

---

Sleep request

- **Method**: `POST`
- **Request:** `control/device/sleep`
- **Added in:** `1.1.1`
- **Input:**

```json
{
  "ip": "192.168.0.0"
}
```

- **Return:**

```json
{
  "status": false,
  "error": "Some error in error case"
}
```

Or

```json
{
  "status": true,
  "message": "Sleep command sent to {ip}."
}
```
