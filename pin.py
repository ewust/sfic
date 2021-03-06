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

class Key(object):
    def __init__(self, key=None, pins=6, min_cut=0, max_cut=9, macs=9, parity=None):

        # Save constraints
        self.pins = pins
        self.min_cut = min_cut
        self.max_cut = max_cut
        self.macs = macs
        self.parity = parity

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

    # Return the odd/even parity array (0 for even, 1 for odd)
    def get_parity(self):
        return [x%2 for x in self.cuts]

    def gen_cut(self, idx, last_cut=None):
        while 1:
            if last_cut is None:
                cut = random.randint(self.min_cut, self.max_cut)
            else:
                cut = random.randint(max(self.min_cut, (last_cut - self.macs)), \
                                     min(self.max_cut, (last_cut + self.macs)))

            if self.parity is None or self.parity[idx] == (cut % 2):
                return cut

    ### (re)generates a key, obeying parity, MACS and the min/max_cut depths
    def gen_key(self):
        self.cuts = [self.gen_cut(0)]
        for i in range(1, self.pins):
            last = self.cuts[i-1]
            cut = self.gen_cut(i, last)
            self.cuts.append(cut)

    def __getitem__(self, i):
        return self.cuts[i]

    def __len__(self):
        return len(self.cuts)

    def __str__(self):
        return ''.join([str(x) for x in self.cuts])


###
###

# Generate control first
control_key = Key(key=args.control_key, pins=args.pins, min_cut=cut_min, max_cut=cut_max, macs=args.MACS)
parity = control_key.get_parity()

# Master obeys parity
master_key = None
if args.master_key is not None:
    master_key = Key(key=args.master_key, pins=args.pins, min_cut=cut_min, max_cut=cut_max, macs=args.MACS, parity=parity)

# generate missing keys
change_key = Key(key=args.change_key, pins=args.pins, min_cut=cut_min, max_cut=cut_max, macs=args.MACS, parity=parity)
if master_key is None:
    master_key = change_key


print "Change key:  %s" % change_key
print "Control key: %s" % control_key
print "Master key:  %s" % master_key


###
### Combinate
###

def combinate(change_key, master_key, control_key):
    pins = []
    for i in range(len(change_key)):
        bottom_pin = min(change_key[i], master_key[i])
        master_pin = max(change_key[i], master_key[i]) - bottom_pin

        build_up_pin = control_key[i] + 10 - (bottom_pin + master_pin)

        top_pin = 23 - (build_up_pin + master_pin + bottom_pin)

        pins.append([top_pin, build_up_pin, master_pin, bottom_pin])

    return pins


pins = combinate(change_key, master_key, control_key)

pin_names = ['TP', 'BU', 'MP', 'BP']
for pin_idx in range(len(pin_names)):
    buf = '%s  ' % pin_names[pin_idx]
    for i in range(args.pins):
        pin = str(pins[i][pin_idx])
        if (pin_idx != (len(pin_names)-1)) and pin == '0':
            pin = '-'
        buf += '% 4s ' % pin
    print buf
