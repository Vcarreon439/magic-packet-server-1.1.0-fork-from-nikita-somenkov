### Magic Packet API

#### Common info methods:

------
Check version of backend
* **Method**: `GET`
* **Request:** `info/version`
* **Added in:** `1.0.0`
* **Return:**
```json
{
  "version": "1.0.0"
}
```

------
Check status of PC
* **Method**: `GET`
* **Request:** `info/status`
* **Added in:** `1.0.0`
* **Return:**
```json
{
  "status": true
}
```

#### Controlling power of PC methods:

------
Shutdown PC request
* **Method**: `POST`
* **Request:** `control/shutdown`
* **Added in:** `1.0.0`
* **Input:**
```json
{
  "timeout": 42
}
```
* **Return:**
```json
{
  "status": true,
  "error": "Some error in error case"
}
```

------
Reboot PC request
* **Method**: `POST`
* **Request:** `control/reboot`
* **Added in:** `1.0.0`
* **Input:**
```json
{
  "timeout": 42
}
```
* **Return:**
```json
{
  "status": true,
  "error": "Some error in error case"
}
```

------
Sleep PC request
* **Method**: `POST`
* **Request:** `control/sleep`
* **Added in:** `1.1.0`
* **Input:**
```json
{
  "timeout": 42
}
```
* **Return:**
```json
{
  "status": true,
  "error": "Some error in error case"
}
```