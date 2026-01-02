### Magic Packet API

#### Common info methods:

##### Server Methods

Set up server for managing internal devices

- Enable this if you dont neccesary want to expose ip address of internal devices

- **Method**: `POST`
- **Request:** `control/server/setup`
- **Added in:** `1.0.1`
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
- **Added in:** `1.0.1`
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
- **Added in:** `1.0.1`
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
- **Added in:** `1.0.1`
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
- **Added in:** `1.0.0`
- **Return:**

```json
{
  "version": "1.0.0"
}
```

---

Check status of PC

- **Method**: `GET`
- **Request:** `info/status`
- **Added in:** `1.0.0`
- **Return:**

```json
{
  "status": true
}
```

#### Controlling power of PC methods:

---

Shutdown PC request

- **Method**: `POST`
- **Request:** `control/shutdown`
- **Added in:** `1.0.0`
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

---

Reboot PC request

- **Method**: `POST`
- **Request:** `control/reboot`
- **Added in:** `1.0.0`
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

---

Sleep PC request

- **Method**: `POST`
- **Request:** `control/sleep`
- **Added in:** `1.1.0`
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
