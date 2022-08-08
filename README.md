## Code purpose
The purpose of *whosup.py* is to provide an extremely simple app that regularly
polls a set of servers, and reports when one or more goes down. I wrote this to
aid in keeping track of power outages in my laboratories at Dalhousie
University.  we use uninterruptible power supplies, but regardless, if there's
a power outage we need to know about it. A clear signal is that the (wired)
internet has failed in our building. When that happens, this code gives a
visual cue and also triggers a message to be sent to us on a Slack channel.
That way, we get the message on our phones without having to be in direct
contact with the computer running the app.

## Code usage

### Download
From github. There is only a single python file to download and a template of the YAML
input file. Nothing to compile.

### Input file
The list of servers to watch, and the Slack webhook data (private!) is read by the program
from a file in YAML format. A template is included. You need to add the name by which your
server is found on the internet, and also the port it uses for connections. For ssh this
is typically 22, but we change the default on many of our servers to cut down on bot
attacks.

### Running the code
- *python whosup.py* will run the program, and assume the input YAML file is in the same
directory and named *whosup.yaml*
- *python whosup.py -h* gives a very minimal help message.
- *python whosup.py -f your.yaml* will run the program with the YAML input file of your
choosing.
