# Should use AsyncWorker to send data to server?
ASYNC_WORKER = True

# Data collection endpoints on the papasan server.
ENDPOINTS = {
  }

# Host name of the papasan sever.
HOST = None

# Protocol of the papasan server.
PROTOCOL = 'https'

# Maxmimum number of tasks to queue up for AsyncWorker.
QUEUE_SIZE = 1000

# Maximum number of seconds to wait in case the interpretter is being shutdown
# but the AsyncWorker still has more work to do.
SHUTDOWN_TIMEOUT = 5


# List of handlers that the main middleware will use. Order is important.
TRACR_HANDLERS = (
    )
