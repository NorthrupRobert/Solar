import spiceypy
import datetime

"""
-------------------------------
    NOTES ON SPICE TOOLKIT
-------------------------------
+ FILE/DATA TYPES
    lsk -> .tls     time info
    spk -> .bsp     trajectory info

+ FUNCTIONS
    spkgeo(target, reference_frame, observer)
        Abstract: "Compute the geometric state (position and velocity) of a target body relative to an observing body."
    utc2et(utc_time)
        given a UTC time as a string, in the form of "YEAR-MONTH-DAY HR:MN:SC", this function will convert this data to
        the ET (ephemeris time) standard.

+ NFID's
    WHAT?
        NAIF's spice toolkit uses NFID's to refer to objects in space.  The full list can be found here:
        https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html
    399 - Earth
    10 - Sun
"""

spiceypy.furnsh('naif0012.tls')
spiceypy.furnsh('de432s.bsp')

def main():
    curr_date = datetime.datetime.now()
    print(f'CURRENT TIME (datetime library):\t\t\t{curr_date}')

    curr_date = curr_date.strftime('%Y-%m-%d 00:00:00') # reformats datatime info as a string, in the requested format: YEAR-MONTH-DAY HR:MN:SC
    print(f'CURRENT TIME (datetime library, midnight adjustment):\t{curr_date}')

    et_curr_date_midnight = spiceypy.utc2et(curr_date)
    print(f'CURRENT TIME (ephemeris time, ET):\t\t\t{et_curr_date_midnight}')

    # Can we compute now the position and velocity (so called state) of the Earth
    # with respect to the Sun? We use the following function to determine the
    # state vector and the so called light time (travel time of the light between 
    # the Sun and our home planet). Positions are always given in km, velocities 
    # in km/s and times in seconds

    # targ : Object that shall be pointed at
    # et : The ET of the computation
    # ref : The reference frame. Here, it is ECLIPJ2000 (so Medium article)
    # obs :  The observer respectively the center of our state vector computation

    earth_state_wrt_sun, earth_sun = spiceypy.spkgeo(targ = 399, \
                                                    et = et_curr_date_midnight, \
                                                    ref = 'ECLIPJ2000', \
                                                    obs = 10)

    print('\n===========================================\n\tEARTH_STATE_WRT_SUN -> DATA\n===========================================')
    print(earth_state_wrt_sun)

if __name__ == "__main__":
    main()
