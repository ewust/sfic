#!/usr/bin/python

import argparse
import random   # todo: replace with /dev/urandom

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pins", help="Number of pins (default: 6)", default=6, type=int)
parser.add_argument("-M", "--MACS", help="Maximum Adjacent Cut Specifiction (default: 9 (sfic))", default=9, type=int)
parser.add_argument("-c", "--cuts", help="Range of cut depths (default: 0-9 (sfic))", default="0-9")
parser.add_argument("-t", "--type", help="key type sfic (0-9) or kwikset (1-7) (default: sfic). Overrides MACS and cuts")

parser.add_argument("-k", "--change-key", help="Specify the change key tip to bow")
parser.add_argument("-C", "--control-key", help="Specify the control key tip to bow")
parser.add_argument("-m", "--master-key", help="Specify the master key tip to bow")



args = parser.parse_args()

if args.type == "sfic":
    args.cuts = "0-9"
    args.MACS = 9
elif args.type == "kwikset":
    args.cuts = "1-7"
    args.MACS = 4


# decode the cut range (e.g. 0-9 for sfic)
cut_min, cut_max = [int(x) for x in args.cuts.split("-")]


def gen_key(cut_min, cut_max, pins):
    return [random.randint(cut_min, cut_max) for i in range(pins)]

# Takes a key as a string "13782" and returns as array of ints [1, 3, 7, 8, 2]
def decode_key(key):
    return [int(key[i]) for i in range(len(key))]



class Key(object):
    def __init__(self, key=None, pins=6, min_cut=0, max_cut=9, macs=9):

        # Save constraints
        self.pins = pins
        self.min_cut = min_cut
        self.max_cut = max_cut
        self.macs = macs

        # Generate random key given constraints
        self.gen_key()

        # Decode key if given one
        if key is not None:
            if len(key) != self.pins:
                raise Exception("Expected %d pins, got %d pins" % (self.pins, len(key)))
            self.cuts = [int(key[i]) for i in range(self.pins)]
            self.verify_MACS()


    # verify that this key follows the MACS
    def verify_MACS(self):
        for i in range(1, self.pins):
            if abs(self.cuts[i] - self.cuts[i-1]) > self.macs:
                raise Exception("Pins (%d,%d): |%d-%d| > MACS (%d)" % (i, i-1, self.cuts[i], self.cuts[i-1], self.macs))


    ### (re)generates a key, obeying MACS and the min/max_cut depths
    def gen_key(self):
        self.cuts = [random.randint(self.min_cut, self.max_cut)]
        for i in range(1, self.pins):
            last = self.cuts[i-1]
            cut = random.randint(max(self.min_cut, (last - self.macs)), \
                                 min(self.max_cut, (last + self.macs)))
            self.cuts.append(cut)

    def __str__(self):
        return ''.join([str(x) for x in self.cuts])


###
###

# generate missing keys
change_key = Key(key=args.change_key, pins=args.pins, min_cut=cut_min, max_cut=cut_max, macs=args.MACS)
control_key = Key(key=args.control_key, pins=args.pins, min_cut=cut_min, max_cut=cut_max, macs=args.MACS)
# Default to no master key
master_key = change_key
if args.master_key is not None:
    master_key = Key(key=args.master_key, pins=args.pins, min_cut=cut_min, max_cut=cut_max, macs=args.MACS)



print "Change key:  %s" % change_key
print "Control key: %s" % control_key
print "Master key:  %s" % master_key

#for i in range(args.pins):
