# Odnoklassniki checker

Based on ok_checher: https://github.com/shllwrld/ok_checker

You can use email / phone number / username to check if account exists.

Output example:

```
$ ./run.py purahina@mail.ru
Target: purahina@mail.ru
Results found: 1
1) Code: 200
Masked Name: Светлана П*******
Masked Email: pu***@mail.ru
Masked Phone: 7********66
Profile Info: 45 лет, Москва
Profile Registred: Профиль создан 19 декабря 2007

------------------------------
Total found: 1
```

## Usage

```sh
$ python3 -m osint-cli-tool-skeleton <target>

# or simply

$ odnoklassniki_checker <target>

# or locally without installing

$ ./run.py <target>
```

<details>
<summary>Targets</summary>
</br>

Specify targets one or more times:
```sh
$ odnoklassniki_checker www.google.com reddit.com patreon.com

Target: www.google.com
Results found: 1
1) Value: Google
Code: 200

------------------------------
Target: patreon.com
Results found: 1
1) Value: Best way for artists and creators to get sustainable income and connect with fans | Patreon
Code: 200

------------------------------
Target: reddit.com
Results found: 1
1) Value: Reddit - Dive into anything
Code: 200

------------------------------
Total found: 3
```

Or use a file with targets list:
```sh
$ odnoklassniki_checker --target-list targets.txt
```

Or combine tool with other through input/output pipelining:
```sh
$ cat list.txt | odnoklassniki_checker --targets-from-stdin
```
</details>

<details>
<summary>Reports</summary>
</br>

The skeleton implements CSV reports:
```sh
$ odnoklassniki_checker www.google.com reddit.com patreon.com -oC results.csv
...
Results were saved to file results.csv

$ more results.csv
"Target","Value","Code"
"www.google.com","Google","200"
"patreon.com","Best way for artists and creators to get sustainable income and connect with fans | Patreon","200"
"reddit.com","Reddit - Dive into anything","200"
```

Also tool supports JSON output format:
```
odnoklassniki_checker www.google.com reddit.com patreon.com -oJ results.json
...
Results were saved to file results.json

$ cat results.json | jq | head -n 10
[
  {
    "input": {
      "value": "www.google.com"
    },
    "output": [
      {
        "value": "Google",
        "code": 200
      }
    ]
  },
```

And can save console output to text file separately:
```sh
odnoklassniki_checker www.google.com reddit.com patreon.com -oT results.txt
...
Results were saved to file results.txt

$ head -n 4 results.txt
Target: www.google.com
Results found: 1
1) Value: Google
Code: 200
```
</details>

<details>
<summary>Proxy</summary>
</br>

The tool supports proxy:
```sh
$ odnoklassniki_checker www.google.com --proxy http://localhost:8080
```
</details>


<details>
<summary>Server</summary>
</br>

The tool can be run as a server:
```sh
$ odnoklassniki_checker --server 0.0.0.0:8080
Server started

$ curl localhost:8080/check -d '{"targets": ["google.com", "yahoo.com"]}' -s | jq
[
  {
    "input": {
      "value": "google.com"
    },
    "output": [
      {
        "value": "Google",
        "code": 200
      }
    ]
  },
  {
    "input": {
      "value": "yahoo.com"
    },
    "output": [
      {
        "value": "Yahoo | Mail, Weather, Search, Politics, News, Finance, Sports & Videos",
        "code": 200
      }
    ]
  }
]
```
</details>


## Installation

Make sure you have Python3 and pip installed.


<details>
<summary>Manually</summary>
</br>

1. Clone or [download](https://github.com/soxoj/osint-cli-tool-skeleton/archive/refs/heads/main.zip) respository
```sh
$ git clone https://github.com/soxoj/osint-cli-tool-skeleton
```

2. Install dependencies
```sh
$ pip3 install -r requirements.txt
```
</details>

<details>
<summary>As a the package</summary>
</br>

You can clone/download repo and install it from the directory to use as a Python package.
```sh
$ pip3 install .
```

Also you can install it from the PyPI registry:
```sh
$ pip3 install https://github.com/soxoj/osint-cli-tool-skeleton
```
</details>
