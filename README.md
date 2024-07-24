# process_controller
The training project for multiprocessing in Python.

## Project Goal
The ProcessController class runs the functions concurrently.
A client can configure the maximum number of concurrent processes and 
the running function timeout.

A common use case:
```python
from process_controller import ProcessController

pc = ProcessController()
pc.set_max_proc(2)
pc.start(
    [
        (function_1, (1, 2)),  # function_1 has 2 arguments
        (function_2, (3,)),    # function_2 has 1 argument
        (function_3, tuple()), # function_3 has 0 arguments
    ],
    5  # every function will be waited for 5 seconds
)
pc.wait()
```

## Quick Start
1. Install Python 3.12.
2. Run the tests
```shell
python -m unittest test.py
```
The code is tested for Linux only.