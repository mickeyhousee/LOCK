import scp


host="192.168.151.218"

# or
client = scp.Client(host, user, password)

# and then
client.transfer('/etc/local/filename', '/etc/remote/filename')