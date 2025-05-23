import pandas as pd
from scipy import constants as sc
from bisect import bisect_left

# boundaries of UV A, B and C in nm from https://www.ncbi.nlm.nih.gov/books/NBK304366/
uva = (315, 400)
uvb = (280, 315)
uvc = (100, 280)

# function that calculates photon energy in eV from given wavelength
def get_ev(wavelength, tuple = True):

    """
    Converts given wavelength (in nm) into photon energy (in eV)

    Parameters
    ----------
    wavelength: wavelength in nm
    tuple: Bool, if tuple == True input is expected as a tuple and output will be a tuple as well.
           If tuple == False input is expected as a float and output will be a float as well

    Returns
    -------
    phot_E: photon energy in eV corresponding to input-wavelength, tuple or float (depends on tuple variable)
    """

    c = sc.c
    h = sc.h
    eV = sc.value("electron volt")

    if tuple == False:
        l = wavelength * 10 ** (-9)  # converting wavelength from nm to m
        phot_E = h * c / (l * eV)
        return phot_E

    elif tuple == True:
        low_bound = wavelength[0] * 10 ** (-9)
        high_bound = wavelength[1] * 10 ** (-9)

        phot_E_high = h * c / (low_bound * eV)
        phot_E_low = h * c / (high_bound * eV)

        return (phot_E_low, phot_E_high)

def get_wavelength(photon_energy, tuple = True):

    """
    Converts given photon energy (in eV) into wavelength (in nm).

    Parameters
    ----------
    photon_energy: Photon energy in electron volts, if tuple:
    tuple: Bool, if tuple == True input is expected as a tuple and output will be a tuple as well.
           If tuple == False input is expected as a float and output will be a float as well

    Returns
    -------
    wavelength: Wavelength (in nm) corresponding to input-photon energy, tuple or float (depends on tuple variable)
    """

    c = sc.c
    h = sc.h
    eV = sc.value("electron volt")

    if tuple == False:
        E = photon_energy * eV  # converting photon energy from eV to Joule
        wavelength = h * c / E * 10**(9) # multiplying by 10^(9) to convert m to nm
        return wavelength

    elif tuple == True:
        low_bound = photon_energy[0] * eV
        high_bound = photon_energy[1] * eV

        wavelength_high = h * c / low_bound * 10**(9)
        wavelength_low = h * c / high_bound * 10**(9)

        return (wavelength_low, wavelength_high)


def take_closest(dataframe, number):
    """
    Get closest value to number in dataframe
    Parameters
    ----------
    dataframe: dataframe to be searched
    number: float for which the closest value should be found in dataframe

    Returns
    closest value to number
    -------

    Assumes dataframe is sorted. Returns closest value to number.

    If two values are equally close, return the smallest value.

    """
    pos = bisect_left(dataframe, number)
    if pos == 0:
        return dataframe[0]
    if pos == len(dataframe):
        return dataframe[len(dataframe) - 1]
    before = dataframe[pos - 1]
    after = dataframe[pos]
    if after - number < number - before:
        return after
    else:
        return before

def get_index_of_closest_number(dataframe, number):

    """
    Finds the index corresponding to the closest value to number in input dataframe.

    Parameters
    ----------
    dataframe: pandas Dataframe, 1D
    number: float for which the index of the closest value should be returned

    Returns
    -------
    index of closest value to number in the dataframe
    """

    closest_number = take_closest(dataframe, number)

    idx = dataframe.index[dataframe == closest_number]

    return int(idx[0])


# defining class for KOMPOT tables
class KOMPOT:

    """
    Class to work with KOMPOT tables. Input file path to read and work with KOMPOT output table.

    KOMPOT.path = filepath
    KOMPOT.file = kompot table as a pandas dataframe
    KOMPOT.header = Column labels of table
    KOMPOT.shape = shape of the kompot table
    KOMPOT.photon_energies = sub-table containing just the photon energy bin columns

    KOMPOT.get_integrated_flux = class method to calculate the integrated flux in a given wavelength range
    and at a certain height (for more info see get_integrated_flux() docstring
    """

    # boundaries of UV A, B and C in nm from https://www.ncbi.nlm.nih.gov/books/NBK304366/
    uva = (315, 400)
    uvb = (280, 315)
    uvc = (100, 280)

    def __init__(self, filepath):

        df = pd.read_fwf(filepath, header = 3)

        self.path = filepath
        self.file = df
        self.header = df.columns
        self.shape = df.shape
        self.photon_energies = df.iloc[:,7:1009]

    def get_integrated_flux(self, height, bounds):

        """
        Computes the integrated flux between bounds[0] and bounds[1] (in nm) at height (in km) within a KOMPOT table.

        Parameters
        ----------
        height: Float, height at which to compute the integrated flux in km
        bounds: Tuple of the form (lower_bound, upper_bound), containing boundaries of wavelength range (in nm) within
                which to calculate the integrated flux

        Returns
        -------
        integrated_flux: Float, integrated flux at height within wavelength-bounds.
        """

        dataframe = self.file
        integrated_flux = 0
        #bounds = getattr(KOMPOT, bounds) # work in progress

        height = height * 100000  # convert height to cm
        bounds = get_ev(bounds, tuple=True)  # convert bounds from wavelength to photon energy in eV

        photon_energies = dataframe.iloc[:, 7:1009]
        bins = photon_energies.columns

        height_index = get_index_of_closest_number(dataframe["Altitude_(cm)"], height)

        for i in range(len(bins)):
            if float(bins[i]) < bounds[0]:
                pass
            elif float(bins[i]) > bounds[1]:
                pass
            else:
                integrated_flux += photon_energies.iloc[(height_index, i)]

        return integrated_flux

if __name__ == "__main__":

    # Example usage
    data1 = 'spectrum80.dat'
    table1 = KOMPOT(data1)

    data2 = 'spectrum_surf.dat'
    table2 = KOMPOT(data2)

    int_flux_uva1 = table1.get_integrated_flux(80,uva)
    int_flux_uvb1 = table1.get_integrated_flux(80,uvb)
    int_flux_uvc1 = table1.get_integrated_flux(80,uvc)

    int_flux_uva2 = table2.get_integrated_flux(80,uva)
    int_flux_uvb2 = table2.get_integrated_flux(80,uvb)
    int_flux_uvc2 = table2.get_integrated_flux(80,uvc)

    print("Integrated flux in 80km height run at 80km in UV-A band:", int_flux_uva1, "erg_s^-1_cm^-2")
    print("Integrated flux in 80km height run at 80km in UV-B band:", int_flux_uvb1, "erg_s^-1_cm^-2")
    print("Integrated flux in 80km height run at 80km in UV-C band:", int_flux_uvc1, "erg_s^-1_cm^-2")
    print("-----------------------------------------------------------------------------------------")
    print("Integrated flux in surface run at 80km in UV-A band:", int_flux_uva2, "erg_s^-1_cm^-2")
    print("Integrated flux in surface run at 80km in UV-B band:", int_flux_uvb2, "erg_s^-1_cm^-2")
    print("Integrated flux in surface run at 80km in UV-C band:", int_flux_uvc2, "erg_s^-1_cm^-2")