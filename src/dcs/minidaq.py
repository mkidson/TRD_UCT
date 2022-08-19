
from datetime import datetime
import os
from re import T
import signal
import time
import click
import zmq
# import dcs.oscilloscopeRead.scopeRead as scopeRead


class zmq_env:
    def __init__(self):

        self.context = zmq.Context()

        self.trdbox = self.context.socket(zmq.REQ)
        self.trdbox.connect('tcp://localhost:7766')

        self.sfp0 = self.context.socket(zmq.REQ)
        self.sfp0.connect('tcp://localhost:7750')

        self.sfp1 = self.context.socket(zmq.REQ)
        self.sfp1.connect('tcp://localhost:7751')


@click.group()
@click.pass_context
def minidaq(ctx):
    ctx.obj = zmq_env()


@minidaq.command()
@click.option('--n_events','-n', default=5, help='Number of triggered events you want to read.')
@click.pass_context

def trigger_read(ctx, n_events):
    # scopeReader = scopeRead.Reader("ttyACM3")
    #run_period = time.time() + 60*0.5 #How long you want to search for triggers for
    # trig_count_1 = int(os.popen('trdbox reg-read 0x102').read().split('\n')[0])

    ctx.obj.trdbox.send_string("read 0x102")
    trig_count_1 = int(ctx.obj.trdbox.recv_string(), 16)
    print(trig_count_1)
    # os.system("trdbox unblock")
    trig_count_2 = 0
    i = 0
    ctx.obj.trdbox.send_string("write 0x103 1")
    ctx.obj.trdbox.recv_string()
    
    while i < (n_events):
        ctx.obj.trdbox.send_string("read 0x102")
        trig_count_2 = int(ctx.obj.trdbox.recv_string(), 16)

        if trig_count_2 != trig_count_1:
            i += 1

            try:
                 ctx.invoke(readevent)
            except:
                 i -= 1

            ctx.obj.trdbox.send_string("read 0x102")
            trig_count_1 = int(ctx.obj.trdbox.recv_string(), 16)
            ctx.obj.trdbox.send_string("write 0x103 1")
            ctx.obj.trdbox.recv_string()
        else:
            pass




@minidaq.command()
@click.pass_context
def readevent(ctx):

    # ctx.obj.trdbox.send_string(f"write 0x103 1") # unblocks
    # ctx.obj.trdbox.send_string(f"write 0x08 1") # send trigger

    ctx.obj.sfp0.send_string("read")
    data = ctx.obj.sfp0.recv()
    print(len(data))

    f = open("data", "wb")
    f.write(data)
    f.close()

@minidaq.command()
@click.pass_context
def old_readevent(ctx):

    ctx.obj.trdbox.send_string(f"write 0x103 1") # unblocks
    # ctx.obj.trdbox.send_string(f"write 0x08 1") # send trigger
    print(ctx.obj.trdbox.recv_string())

    ctx.obj.sfp0.send_string("read")
    data = ctx.obj.sfp0.recv()
    print(len(data))

    f = open("data", "wb")
    f.write(data)
    f.close()