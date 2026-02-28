import sys
import itertools
from typing import Any
from logic import push_metadata


DEFAULTS = {
    "dir": ".",
    "out": "a.out",
    "host": "localhost",
    "port": 5432,
    "startDate": None,
    "endDate": None,
    "usersMentioned": [],
    "reunionResult": None,
    "input": "data.csv",
    "help": False,
}


def cli():
    args = iter2(sys.argv, parse_args, update)

    DEFAULTS.update(args)
    args = DEFAULTS

    if args["help"] == True:
        print("""
              Operation:
                  push, p               Pulls the metadata from the specified
                                        [--dir]ectory and updates the database.
                                        Stores the metadata from the specified
                                        [--in]put file onto the
                                        [--host][--port] machine. This is your
                                        denodo socket is located.
                  query, q              Runs a query with the specified
                                        filters. to the [--host][--port]
                                        machine.
              Operation flags:
                  -d,  --dir            Sets the directory.
                  -p,  --port           Sets the port.
                  -h,  --host           Sets the host machine IP.
                  -o,  --out            Sets the output file.
              Filters:
                  -sd, --startDate      Sets the start date.
                  -ed, --endDate        Sets the end date.
                  -m,  --usersMentioned Sets the participating users.
                  -r,  --reunionResult  Sets the reunion result.
              """)
        return

    match sys.argv[1]:
        case "push" | "p":
            # Extract the metadata from the args["dir"] directory
            #
            # Presumably something like extract(args) should do.
            # Maybe returns the data / writes it to a file
            print(push_metadata(args))

        case "store" | "s":
            # Send the metadata to the denodo database
            #
            # Presumably something like send(args) should do.
            # could return something like "ok" | ("error", description)
            pass
        case "query" | "q":
            # Send a query to the denodo AI agent
            #
            # Presumably something like query(args) should do.
            # could return something like ("ok", response) | ("error", description)
            pass



def parse_args(arg1: str, arg2: str):
    match (arg1, arg2):
        case ("-d", v):
            return { "dir": v }
        case ("-o", v):
            return { "output": v }
        case ("-h", v):
            return { "host": v }
        case ("-p", v):
            return { "port": v }
        case ("-sd", v):
            return { "startDate": parseDate(v) }
        case ("-ed", v):
            return { "endDate": parseDate(v) }
        case ("-m", v):
            return { "usersMentioned": v.split(",") }
        case ("-r", v):
            return { "reunionResult": v }
        case ("-i", v):
            return { "input": v }
        case (None, _):
            return {}
        case (v, _):
            if v.startswith("--help"):
                return {"help": True}
            if v.startswith("--dir="):
                return {"dir": v[6:]}
            if v.startswith("--port="):
                return {"port": v[7:]}
            if v.startswith("--host="):
                return {"host": v[7:]}
            if v.startswith("--out="):
                return {"output": v[6:]}
            if v.startswith("--startDate="):
                return {"startDate": parseDate(v[12:])}
            if v.startswith("--endDate="):
                return {"endDate": parseDate(v[12:])}
            if v.startswith("--usersMentioned="):
                return {"usersMentioned": v[17:].split(",")}
            if v.startswith("--reunionResult="):
                return {"reunionResult": parseDate(v[16:])}
            if v.startswith("--in="):
                return {"input": v[5:]}

            return {}


def extractDuration(string, sign):
    match string[-1]:
        case "h" | "H":
            return datetime.timedelta(hours = sign * int(string[1:-1]))
        case "m":
            return datetime.timedelta(minutes = sign * int(string[1:-1]))
        case "s" | "S":
            return datetime.timedelta(seconds = sign * int(string[1:-1]))
        case "Y" | "y":
            return datetime.timedelta(days = sign * 365 * int(string[1:-1]))
        case "M":
            return datetime.timedelta(days = sign * 30 * int(string[1:-1]))
        case "D" | "d":
            return datetime.timedelta(days = sign * int(string[1:-1]))


def parseDate(string):
    """
    Parse a date.
    Allowed formats are:
        - ISO8601 (YYYY-MM-DDTHH:MM:SS)
        - Time deltas (+1D|+5Y|-5h|+3s)
        - Spanish dates (DD/MM/YYYY)
    """

    if string[0] == "+":
        return extractDuration(string, 1)
    if string[0] == "-":
        return extractDuration(string, -1)

    # Spanish format 🇪🇸🐂🇪🇸🐂🇪🇸
    if string[2] == "/":
        day = int(string[0:2])
        month = int(string[3:5])
        year = int(string[6:10])

        return datetime.date(year, month, day)

    year = int(string[0:4])
    month = int(string[5:7])
    day = int(string[8:10])
    hour = int(string[11:13])
    minute = int(string[14:16])
    second = int(string[17:19])

    return datetime.datetime(year, month, day, hour, minute, second)


def update(d1, d2):
    """
    Updates d1 with all values of d2.
    If a key is present in both, it gets merged as a list
    """
    for k, v in d2.items():
        try:
            d1[k] = list(itertools.chain.from_iterable([d1[k], v]))
        except KeyError:
            d1[k] = v
    return d1


def iter2(l: list[str], f: Callable[[str, str], Any], merge_func: Callable[[Any, Any], Any]) -> Any:
    ret = {}
    prev = None
    for curr in l:
        if curr == None:
            prev = e
            continue

        ret = merge_func(ret, f(prev, curr))
        prev = curr

    return ret

