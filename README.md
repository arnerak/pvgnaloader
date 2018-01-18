# pvgnaloader

Clone this repository and install dependencies as shown.

`git clone https://github.com/arnibold/pvgnaloader`

Fill in your [pvgna](http://pvgna.com) credentials in pvgnaloader.ini and run with 

`python pvgnaloader.py`

### pvgnaloader.ini

* email: your pvgna registered email address.
* password: your pvgna account password.
* resolution: choose from 1080p, 720p, 480p, 360p.
* crawlchapters: set to true if you want pvgnaloader to automatically download all chapters from a single link.
* links: list of desired videos. If crawlchapters is true, only enter a single link of each guide.

## Dependencies

### Python Requests

Clone repository:

`git clone git://github.com/requests/requests.git`

Install:

`cd requests`

`pip install .`

[Installation guide](http://docs.python-requests.org/en/master/user/install/)

### ffmpeg

Download [here](https://ffmpeg.zeranoe.com/builds/) and place ffmpeg.exe in pvgnaloader folder.