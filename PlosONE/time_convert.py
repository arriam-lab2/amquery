
import datetime

def parse_h(x):
    return datetime.datetime.strptime(x, "%H:%M:%S.%f")

def parse_m(x):
    return datetime.datetime.strptime(x, "%M:%S.%f")

def parse_s(x):
    return datetime.datetime.strptime(x, "%S.%f")

def to_timedelta(x):
    return datetime.timedelta(hours=x.hour, minutes=x.minute, seconds=x.second, microseconds=x.microsecond)

def to_datetime(x):
    return parse_h("0:0:0.0") + x


if __name__ == "__main__":
    import sys

    #x = [to_timedelta(parse_h(t)).total_seconds() for t in sys.argv[1:]]
    #print(" ".join(str(t) for t in x))

    print(" ".join(str(int(z)) for z in (float(x) / 1024 for x in sys.argv[1:])))

    #x = [to_timedelta(parse_m(t))for t in sys.argv[1:]]
    #print(to_datetime(x[0] + x[1] + x[2] + x[3] + x[4] + x[5] + x[6]).strftime("%H:%M:%S.%f"))
    #print(to_datetime(x[0] + x[1] + x[2] + x[3] + x[4] + x[5] + x[7]).strftime("%H:%M:%S.%f"))

    #z = to_timedelta(x1) + to_timedelta(x2)
    #print(to_datetime(z).strftime("%M:%S.%f"))

    #x1 = sys.argv[1]
    #x1 = parse_s(x1)
    #print(x1.strftime("%M:%S.%f"))

    # memory
    #x = sys.argv[1]
    #x = float(x) / 1024
    #y = "Mb"
    #if x > 1024:
    #    x = float(x) / 1024
    #    y = "Gb"

    #print(x, y)
    

