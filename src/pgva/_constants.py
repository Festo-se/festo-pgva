"""Internal hardware limit constants for the PGVA-1 device.

These values are derived from the PGVA-1 operation manual and are used
internally by the driver. They are not part of the public API.
"""

# Output pressure limits (mBar)
MAXIMUM_OUTPUT_PRESSURE_MBAR = 450
MINIMUM_OUTPUT_PRESSURE_MBAR = -450

# Internal pressure chamber limits (mBar)
MAXIMUM_PRESSURE_CHAMBER_MBAR = 1000
MINIMUM_PRESSURE_CHAMBER_MBAR = 200

# Internal vacuum chamber limits (mBar)
MAXIMUM_VACUUM_CHAMBER_MBAR = -200
MINIMUM_VACUUM_CHAMBER_MBAR = -900

# Scaling factors derived from the PGVA-1 operation manual
PRESSURE_CHAMBER_CONVERSION_FACTOR = 1 / 0.5543
VACUUM_CHAMBER_CONVERSION_FACTOR = 1 / -0.277
