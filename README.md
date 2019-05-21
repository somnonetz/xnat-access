# XNAT Access

Thin XNAT REST API wrapper for Python 3 requests.


## Installation

```bash
pip3 install --user xnat-access
```


## Usage

```python
from xnat_access import XNATClient

xnat = XNATClient(
    'https://example.com/xnat',
    'USERNAME',
    'PASSWORD'
)

url = 'projects/PROJECT/subjects/SUBJECT/experiments/EXPERIMENT/scans'
scans = xnat.get_result(url)
print(scans)

# all functions
# --------------------
# xnat.get_request
# xnat.get_json
# xnat.get_result
# xnat.get_file
# xnat.download_file
# xnat.put_request
# xnat.upload_file
# xnat.delete_request
# xnat.open_session
# xnat.close_session
# xnat.session_is_open
```
