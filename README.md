**<h1>Simple Paint</h1>**

*Install:*
>python3 -m venv venv
>
>source venv/bin/activate
>
>pip install -r requirements.txt

*Run:*
>python painter.py
>
>**or**
>
>./painter.py

*Help:*
>python painter.py --help

*Commands from input file:*

>**canvas**: C w h
>
>**line**: Lx1y1x2y2
>
>**rectangle**: Rx1y1x2y2
>
>**fill**: Bxyc

## Output example:

    ----------------------
    |                    |
    |                    |
    |                    |
    |                    |
    ----------------------
    ----------------------
    |                    |
    |xxxxxx              |
    |                    |
    |                    |
    ----------------------
    ----------------------
    |                    |
    |xxxxxx              |
    |     x              |
    |     x              |
    ----------------------
    ----------------------
    |               xxxxx|
    |xxxxxx         x   x|
    |     x         xxxxx|
    |     x              |
    ----------------------
    ----------------------
    |oooooooooooooooxxxxx|
    |xxxxxxooooooooox   x|
    |     xoooooooooxxxxx|
    |     xoooooooooooooo|
    ----------------------
