import spiceypy
import datetime
import numpy as np
from matplotlib import pyplot as plt
import math

"""
-------------------------------
    NOTES ON SPICE TOOLKIT
-------------------------------
+ FILE/DATA TYPES
    lsk -> .tls     time info
    spk -> .bsp     trajectory info
    pck -> .tpc     orientation info

+ FUNCTIONS
    spkgeo(target, ephemeris_time, reference_frame, observer)
        Abstract: "Compute the geometric state (position and velocity) of a target body relative to an observing body."
    spkgps(target, ephemeris_time, reference_frame, observer)
        Abstract: "Compute the geometric position of a target body relative to an observing body."
    bodvcd(target, quality, maxn)
        returns the specified value of a quality about an object, say the radii of the sun.  Maxn refers to the number of
        expected parameters
    utc2et(utc_time)
        given a UTC time as a string, in the form of "YEAR-MONTH-DAY HR:MN:SC", this function will convert this data to
        the ET (ephemeris time) standard.

+ NFID's
    WHAT?
        NAIF's spice toolkit uses NFID's to refer to objects in space.  The full list can be found here:
        https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html
    399 - Earth
    10 - Sun
    0 - Solar System Barycentre
"""

def main():
    spiceypy.furnsh('de432s.bsp')
    spiceypy.furnsh('naif0012.tls')
    curr_date = datetime.datetime.now()
    print(f'CURRENT TIME (datetime library):\t\t\t{curr_date}')

    curr_date = curr_date.strftime('%Y-%m-%d %H:%M:%S') # reformats datatime info as a string, in the requested format: YEAR-MONTH-DAY HR:MN:SC
    print(f'CURRENT TIME (datetime library, to S):\t{curr_date}')

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

def main_two():
    # ********************************************************************************************************************************
    # FURNSH KERNELS
    # ********************************************************************************************************************************
    # spiceypy.furnsh('kernel_meta.txt')
    spiceypy.furnsh('de432s.bsp') # General Trajectory Info
    spiceypy.furnsh('naif0012.tls') # General Time Info
    spiceypy.furnsh('pck00010.tpc') # 

    # ********************************************************************************************************************************
    # SETTING TIME INTERVALS, ARRAYS
    # ********************************************************************************************************************************
    # Set initial and end times (ET)
    INIT_DATE_UTC = datetime.datetime(year=2000, month=1, day=1) # default time values set to 2000/01/01 00:00:00
    DELTA_TIME = 10000 # in days
    END_DATE_UTC = INIT_DATE_UTC + datetime.timedelta(DELTA_TIME)
    init_time_et = spiceypy.utc2et(INIT_DATE_UTC.strftime('%Y-%m-%d %H:%M:%S'))
    end_time_et = spiceypy.utc2et(END_DATE_UTC.strftime('%Y-%m-%d %H:%M:%S'))

    # Define time interval array (numpy)
    time_interval_et_array = np.linspace(init_time_et, end_time_et, DELTA_TIME) # Gives an array of the Ephemeris Time of each consecutive day at midnight (UTC)
    SSB_WRT_SUN_POSITION = [] # Solar System Barycentre with respect to the sun at the indicated ET
    SSB_WRT_SUN_DISTANCE = []
    for time_interval_et_instance in time_interval_et_array:
        _position, _light_travel_time = spiceypy.spkgps(targ = 0, et = time_interval_et_instance, ref = 'ECLIPJ2000', obs = 10)
        SSB_WRT_SUN_POSITION.append(_position)

        x, y, z = tuple(_position)
        dist = math.sqrt(x**2 + y**2 + z**2)
        SSB_WRT_SUN_DISTANCE.append(dist)

    # Convert SSB_WRT_SUN_POSITION to numpy array type
    SSB_WRT_SUN_POSITION = np.array(SSB_WRT_SUN_POSITION)
    SSB_WRT_SUN_DISTANCE = np.array(SSB_WRT_SUN_DISTANCE)

    # ********************************************************************************************************************************
    # CALCULATING SUN RADIUS
    # ********************************************************************************************************************************
    # Calculate the radius of the sun
    _number_of_returned_values, SUN_RADII = spiceypy.bodvcd(bodyid = 10, item = 'RADII', maxn = 3)
    SUN_RADIUS = SUN_RADII[0]

    # Scale position values using the Sun's radius
    SSB_WRT_SUN_POSITION_SCALED = SSB_WRT_SUN_POSITION / SUN_RADIUS

    # ********************************************************************************************************************************
    # DISPLAYING DATA TO CONSOLE
    # ********************************************************************************************************************************
    # Display data
    print('========================================\n\t\tDATA\n========================================')
    print(f'+ INIT_DATE_UTC: {INIT_DATE_UTC}')
    print(f'+ init_time_et: {init_time_et}')
    print(f'+ END_DATE_UTC: {END_DATE_UTC}')
    print(f'+ end_time_et: {end_time_et}')

    print('\n+ Position components for the Solar System\n' \
        '  Barycentre (SSB) with respect to the center\n' \
        '  of the sun (at initial time):\n' \
        '\tX -> %s km\n' \
        '\tY -> %s km\n' \
        '\tZ -> %s km\n' % tuple(np.round(SSB_WRT_SUN_POSITION[0])))

    print('+ Distance between the Solar System Barycentre w.r.t the\n' \
      '  centre of the Sun (at initial time): \n' \
      '\td = %s km\n' % round(SSB_WRT_SUN_DISTANCE[0]))
    print(f'+ SUN_RADIUS: {SUN_RADIUS}')

    # ********************************************************************************************************************************
    # PLOT SSB AGAINST SUN POS/SIZE, USING X, Y COOR.
    # ********************************************************************************************************************************
    # We only plot the x, y components (view on the ecliptic plane)
    SSB_WRT_SUN_POSITION_SCALED_XY = SSB_WRT_SUN_POSITION_SCALED[:, 0:2]

    # Set a dark background... since... space is dark
    plt.style.use('dark_background')

    # Create a figure and ax
    FIG, AX = plt.subplots(figsize=(12, 8)) # picture size (x, y)

    # Create a yellow circle that represents the Sun, add it to the ax
    SUN_CIRC = plt.Circle((0.0, 0.0), 1.0, color='yellow', alpha=0.8)
    AX.add_artist(SUN_CIRC)

    # Plot the SSB movement
    AX.plot(SSB_WRT_SUN_POSITION_SCALED_XY[:, 0], \
            SSB_WRT_SUN_POSITION_SCALED_XY[:, 1], \
            ls='solid', color='royalblue')

    # Set some parameters for the plot, set an equal ratio, set a grid, and set
    # the x and y limits
    AX.set_aspect('equal')
    AX.grid(True, linestyle='dashed', alpha=0.5)
    AX.set_xlim(-2, 2)
    AX.set_ylim(-2, 2)

    # Some labelling
    AX.set_xlabel('X in Sun-Radius')
    AX.set_ylabel('Y in Sun-Radius')

    # Saving the figure in high quality
    plt.savefig('SSB_WRT_SUN.png', dpi=300)

if __name__ == "__main__":
    main_two()
