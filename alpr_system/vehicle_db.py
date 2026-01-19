"""
Nigerian Vehicle Registration Database

Mock database simulating Nigerian vehicle registry.
Contains vehicle information indexed by license plate numbers.

Plate Format: AAA-123AA (e.g., KTS-123AB)

Fields per vehicle:
- owner_name: Vehicle owner name
- vehicle_type: Vehicle make/model
- state: Nigerian state
- plate_color: Blue (Private), Red (Commercial), Green (Government)
- year: Year of registration

Author: ALPR System
Date: January 2026
"""

# Mock Nigerian Vehicle Database
VEHICLE_DATABASE = {
    # Test Records with hyphenated keys
    'KTS-123AB': {
        'owner_name': 'Lawal Nasiru',
        'vehicle_type': 'Toyota Corolla',
        'state': 'Katsina',
        'plate_color': 'Blue',
        'plate_type': 'Private',
        'year': 2021
    },
    
    'LAG-456CD': {
        'owner_name': 'Adewale Johnson',
        'vehicle_type': 'Honda Accord',
        'state': 'Lagos',
        'plate_color': 'Blue',
        'plate_type': 'Private',
        'year': 2020
    },
    
    'KDU-789EF': {
        'owner_name': 'Aminu Haruna',
        'vehicle_type': 'Toyota Hilux',
        'state': 'Kaduna',
        'plate_color': 'Red',
        'plate_type': 'Commercial',
        'year': 2019
    },
    
    'OGU-234GH': {
        'owner_name': 'Chioma Okonkwo',
        'vehicle_type': 'Nissan Patrol',
        'state': 'Ogun',
        'plate_color': 'Blue',
        'plate_type': 'Private',
        'year': 2022
    },
    
    'ABA-567IJ': {
        'owner_name': 'Federal Road Safety Corps',
        'vehicle_type': 'Ford Transit',
        'state': 'Federal',
        'plate_color': 'Green',
        'plate_type': 'Government',
        'year': 2023
    },
    
    'LAG-901KL': {
        'owner_name': 'Lagos State Transport Company',
        'vehicle_type': 'BRT Bus',
        'state': 'Lagos',
        'plate_color': 'Red',
        'plate_type': 'Commercial',
        'year': 2021
    },
    
    'KAN-345MN': {
        'owner_name': 'Ibrahim Sani',
        'vehicle_type': 'Mercedes-Benz Sprinter',
        'state': 'Kano',
        'plate_color': 'Red',
        'plate_type': 'Commercial',
        'year': 2020
    },
    
    'PRT-678OP': {
        'owner_name': 'Kingsley Okoro',
        'vehicle_type': 'Lexus RX350',
        'state': 'Rivers',
        'plate_color': 'Blue',
        'plate_type': 'Private',
        'year': 2022
    },
    
    'ENL-012QR': {
        'owner_name': 'Mary Uche Enugu',
        'vehicle_type': 'Kia Picanto',
        'state': 'Enugu',
        'plate_color': 'Blue',
        'plate_type': 'Private',
        'year': 2021
    },
    
    'IBA-345ST': {
        'owner_name': 'Ibadan Municipal Authority',
        'vehicle_type': 'Hyundai Bus',
        'state': 'Oyo',
        'plate_color': 'Green',
        'plate_type': 'Government',
        'year': 2022
    },
    
    'AKU-678UV': {
        'owner_name': 'Precious Adeleke',
        'vehicle_type': 'Hyundai i10',
        'state': 'Akure',
        'plate_color': 'Blue',
        'plate_type': 'Private',
        'year': 2023
    },
    
    'ABJ-901WX': {
        'owner_name': 'Federal Inland Revenue Service',
        'vehicle_type': 'Toyota Fortuner',
        'state': 'Federal',
        'plate_color': 'Green',
        'plate_type': 'Government',
        'year': 2021
    },
    
    'BEN-234YZ': {
        'owner_name': 'Okechukwu Nwakwo',
        'vehicle_type': 'Volkswagen Golf',
        'state': 'Benin',
        'plate_color': 'Blue',
        'plate_type': 'Private',
        'year': 2020
    },
    
    'MAI-567AA': {
        'owner_name': 'Hauwa Mohammed',
        'vehicle_type': 'Peugeot 307',
        'state': 'Maiduguri',
        'plate_color': 'Blue',
        'plate_type': 'Private',
        'year': 2019
    },
    
    'YLA-890BB': {
        'owner_name': 'Yola State Transport',
        'vehicle_type': 'Ashok Leyland Bus',
        'state': 'Adamawa',
        'plate_color': 'Red',
        'plate_type': 'Commercial',
        'year': 2021
    },
}


def lookup_vehicle(plate_number):
    """
    Look up vehicle information by license plate number.
    
    Handles both formatted (e.g., 'KTS-123AB') and unformatted (e.g., 'KTS123AB').
    
    Args:
        plate_number: License plate number
    
    Returns:
        dict: Vehicle information if found, else None
    """
    plate_number = plate_number.strip().upper()
    
    # Try direct lookup with hyphen
    if plate_number in VEHICLE_DATABASE:
        return VEHICLE_DATABASE[plate_number]
    
    # Try without hyphen
    plate_no_hyphen = plate_number.replace('-', '')
    for key in VEHICLE_DATABASE:
        if key.replace('-', '') == plate_no_hyphen:
            return VEHICLE_DATABASE[key]
    
    return None


def is_plate_registered(plate_number):
    """
    Check if a license plate is registered.
    
    Args:
        plate_number: License plate number
    
    Returns:
        bool: True if plate exists in database
    """
    return lookup_vehicle(plate_number) is not None


def get_all_vehicles():
    """
    Get all vehicles in the database.
    
    Returns:
        list: List of all vehicle records
    """
    results = []
    for plate, info in VEHICLE_DATABASE.items():
        results.append({
            'plate_number': plate,
            **info
        })
    return results
