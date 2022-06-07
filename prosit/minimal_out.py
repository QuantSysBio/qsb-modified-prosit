import json

import numpy as np

import constants
import utils

TOP_N = 5

IONS = np.array(
    [
        'y1^1', 'y1^2', 'y1^3', 'b1^1', 'b1^2', 'b1^3',
        'y2^1', 'y2^2', 'y2^3', 'b2^1', 'b2^2', 'b2^3',
        'y3^1', 'y3^2', 'y3^3', 'b3^1', 'b3^2', 'b3^3',
        'y4^1', 'y4^2', 'y4^3', 'b4^1', 'b4^2', 'b4^3',
        'y5^1', 'y5^2', 'y5^3', 'b5^1', 'b5^2', 'b5^3',
        'y6^1', 'y6^2', 'y6^3', 'b6^1', 'b6^2', 'b6^3',
        'y7^1', 'y7^2', 'y7^3', 'b7^1', 'b7^2', 'b7^3',
        'y8^1', 'y8^2', 'y8^3', 'b8^1', 'b8^2', 'b8^3',
        'y9^1', 'y9^2', 'y9^3', 'b9^1', 'b9^2', 'b9^3',
        'y10^1', 'y10^2', 'y10^3', 'b10^1', 'b10^2', 'b10^3',
        'y11^1', 'y11^2', 'y11^3', 'b11^1', 'b11^2', 'b11^3',
        'y12^1', 'y12^2', 'y12^3', 'b12^1', 'b12^2', 'b12^3',
        'y13^1', 'y13^2', 'y13^3', 'b13^1', 'b13^2', 'b13^3',
        'y14^1', 'y14^2', 'y14^3', 'b14^1', 'b14^2', 'b14^3',
        'y15^1', 'y15^2', 'y15^3', 'b15^1', 'b15^2', 'b15^3',
        'y16^1', 'y16^2', 'y16^3', 'b16^1', 'b16^2', 'b16^3',
        'y17^1', 'y17^2', 'y17^3', 'b17^1', 'b17^2', 'b17^3',
        'y18^1', 'y18^2', 'y18^3', 'b18^1', 'b18^2', 'b18^3',
        'y19^1', 'y19^2', 'y19^3', 'b19^1', 'b19^2', 'b19^3',
        'y20^1', 'y20^2', 'y20^3', 'b20^1', 'b20^2', 'b20^3',
        'y21^1', 'y21^2', 'y21^3', 'b21^1', 'b21^2', 'b21^3',
        'y22^1', 'y22^2', 'y22^3', 'b22^1', 'b22^2', 'b22^3',
        'y23^1', 'y23^2', 'y23^3', 'b23^1', 'b23^2', 'b23^3',
        'y24^1', 'y24^2', 'y24^3', 'b24^1', 'b24^2', 'b24^3',
        'y25^1', 'y25^2', 'y25^3', 'b25^1', 'b25^2', 'b25^3',
        'y26^1', 'y26^2', 'y26^3', 'b26^1', 'b26^2', 'b26^3',
        'y27^1', 'y27^2', 'y27^3', 'b27^1', 'b27^2', 'b27^3',
        'y28^1', 'y28^2', 'y28^3', 'b28^1', 'b28^2', 'b28^3',
        'y29^1', 'y29^2', 'y29^3', 'b29^1', 'b29^2', 'b29^3'
    ], 
    dtype='str'
)


ox_int = constants.ALPHABET["M(ox)"]
c_int = constants.ALPHABET["C"]

class Converter():
    def __init__(self, data, out_path):
        self.out_path = out_path
        self.data = data

    def convert(self, write_header):
        """
        """
        with open(self.out_path, mode="w", encoding="utf-8") as f:
            if write_header:
                f.write("modified_sequence\tprecursor_charge\ttop_{}_ions\n".format(TOP_N))
            for i in range(self.data["precursor_charge_onehot"].shape[0]):

                sequence_integer = self.data["sequence_integer"][i]
                precursor_charge = self.data["precursor_charge_onehot"][i].argmax() + 1
                aIntensity = self.data["intensities_pred"][i]
                sel = np.argpartition(aIntensity, -TOP_N)[-TOP_N:]

                aIons = IONS[sel]

                spec = MinimalSpectrum(
                    sequence_integer,
                    precursor_charge,
                    aIons,
                )                    
                f.write(str(spec))
        return spec


class MinimalSpectrum(object):
    def __init__(
        self,
        sequence_integer,
        precursor_charge,
        aIons,
    ):
        self.sequence = utils.get_sequence(sequence_integer)
        self.precursor_charge = precursor_charge
        self.aIons = json.dumps(list(aIons))


    def __str__(self):
        s = "{sequence}\t{charge}\t{aIons}\n"
        s = s.format(
            sequence=self.sequence.replace("M(ox)", "Z"),
            charge=self.precursor_charge,
            aIons=self.aIons,
        )
        return s
