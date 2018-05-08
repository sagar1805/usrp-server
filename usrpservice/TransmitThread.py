from __future__ import print_function       #should be on the top
import threading
import time
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import time
import wx
import ctypes
import sys

if sys.platform.startswith('linux'):
    try:
        x11 = ctypes.cdll.LoadLibrary('libX11.so')
        x11.XInitThreads()
    except:
        print("Warning: failed to XInitThreads()")


class TransmitThread(threading.Thread,grc_wxgui.top_block_gui):
    fileName = "none"
    ipAddress = ""
    decIM = ""
    carrFreq =""
    thdRunning=True
    clientID = None

    def __int__(self,fileName, ipAddress, decIM, carrFreq):
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")
        self.fileName = str(fileName)
        self.ipAddress = ipAddress
        self.decIM = int(decIM)
        self.carrFreq = int(carrFreq)

    def run(self):
        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_sink_0_0 = uhd.usrp_sink(
        	",".join(('', self.ipAddress)),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        print("Decimation by ", self.decIM)
        self.uhd_usrp_sink_0_0.set_samp_rate(48000 * 250 / 48)
        self.uhd_usrp_sink_0_0.set_center_freq(self.carrFreq, 0)
        self.uhd_usrp_sink_0_0.set_gain(0.25, 0)
        self.uhd_usrp_sink_0_0.set_antenna('TXA', 0)
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_ccc(
                interpolation=250,
                decimation=self.decIM,
                taps=None,
                fractional_bw=None,
        )
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((1.5259021896696422e-05, ))
        self.blocks_interleaved_short_to_complex_0 = blocks.interleaved_short_to_complex(False, False)
        print("Setting File: ", self.fileName)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_short*1, self.fileName, True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.blocks_interleaved_short_to_complex_0, 0))
        self.connect((self.blocks_interleaved_short_to_complex_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.rational_resampler_xxx_0_0, 0))
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.uhd_usrp_sink_0_0, 0))

        print("Transmission started! Will wait to be killed")
        while self.thdRunning:
            time.sleep(2)
        print("Transmission thread stopped!")


    def endThreadExecution(self):
        self.thdRunning = False;

    def setClientId(self,clientID):
        self.clientID=clientID

    def getClientId(self):
        return self.clientID

    def killThreadExecution(self):
        self.thdRunning = False

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def run(self):
        self.Start(True)
        self.Wait()

    def _get_my_tid(self):
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")
        return self.get_ident()
        raise AssertionError("could not determine the thread's id")

