
"""
Nigerian Vehicle Registration Database

Mandatory test records as per project requirements:
- KTS123AB → Lawal Nasiru → Toyota Corolla → Katsina → Personal
- LAG456CD → Adewale Johnson → Honda Accord → Lagos → Personal
- KT234KTN → Musa Abdullahi → Toyota Hiace → Katsina → Commercial
- LA567BRT → Lagos State Transport Authority → BRT Bus → Lagos → Commercial
- FG234KT → Federal Government of Nigeria → Toyota Hilux → Federal → Government
"""

# Sample vehicle database with mandatory test records
VEHICLE_DATABASE = {
    # ===== MANDATORY TEST RECORDS =====
    
    # Personal plate: KTS-123-AB (format: 3 letters, 3 digits, 2 letters)
    'KTS123AB': {
        'owner_name': 'Lawal Nasiru',
        'state': 'Katsina',
        'vehicle_type': 'Toyota Corolla',
        'color': 'Silver',
        'year': 2021,
        'plate_type': 'Personal'
    },
    
    # Personal plate: LAG-456-CD
    'LAG456CD': {
        'owner_name': 'Adewale Johnson',
        'state': 'Lagos',
        'vehicle_type': 'Honda Accord',
        'color': 'Black',
        'year': 2020,
        'plate_type': 'Personal'
    },
    
    # Commercial plate: KT-234-KTN (format: 2 letters, 3 digits, 3 letters)
    'KT234KTN': {
        'owner_name': 'Musa Abdullahi',
        'state': 'Katsina',
        'vehicle_type': 'Toyota Hiace',
        'color': 'White',
        'year': 2019,
        'plate_type': 'Commercial'
    },
    
    # Commercial plate: LA-567-BRT
    'LA567BRT': {
        'owner_name': 'Lagos State Transport Authority',
        'state': 'Lagos',
        'vehicle_type': 'BRT Bus',
        'color': 'Red',
        'year': 2018,
        'plate_type': 'Commercial'
    },
    
    # Government plate: FG-234-KT (format: FG, 3 digits, 2 letters)
    'FG234KT': {
        'owner_name': 'Federal Government of Nigeria',
        'state': 'Federal',
        'vehicle_type': 'Toyota Hilux',
        'color': 'White',
        'year': 2022,
        'plate_type': 'Government'
    },
    
    # ===== ADDITIONAL TEST RECORDS =====
    
    'LA342BCA': {
        'owner_name': 'Aminu Adeyemi',
        'state': 'Lagos',
        'vehicle_type': 'Private Car',
        'color': 'Silver',
        'year': 2022,
        'plate_type': 'Personal'
    },
    'KD123ABC': {
        'owner_name': 'Fatima Mohammed',
        'state': 'Kaduna',
        'vehicle_type': 'Sedan',
        'color': 'Black',
        'year': 2021,
        'plate_type': 'Personal'
    },
    'AB567XYZ': {
        'owner_name': 'Federal Road Safety Corps',
        'state': 'Abuja',
        'vehicle_type': 'Official Vehicle',
        'color': 'White',
        'year': 2023,
        'plate_type': 'Government'
    },
    'OG789PQR': {
        'owner_name': 'Lagos State Transport Company',
        'state': 'Ogun',
        'vehicle_type': 'Commercial Bus',
        'color': 'Green',
        'year': 2020,
        'plate_type': 'Commercial'
    },
    'RI456DEF': {
        'owner_name': 'Chinedu Okafor',
        'state': 'Rivers',
        'vehicle_type': 'Private Truck',
        'color': 'Red',
        'year': 2019,
        'plate_type': 'Personal'
    }
}


def lookup_vehicle(plate_number):
    """
    Look up vehicle information by license plate number.
    
    Handles both formatted (e.g., 'KTS-123-AB') and unformatted (e.g., 'KTS123AB') versions.
    
    Args:
        plate_number: License plate number (e.g., 'LA342BCA' or 'KTS-123-AB')
    
    Returns:
        dict: Vehicle information if found, else None
    """
    plate_number = plate_number.strip().upper()
    
    # Try direct lookup first (unformatted)
    if plate_number in VEHICLE_DATABASE:
        return VEHICLE_DATABASE[plate_number]
    
    # Try removing hyphens and looking up again
    plate_no_hyphens = plate_number.replace('-', '')
    if plate_no_hyphens in VEHICLE_DATABASE:
        return VEHICLE_DATABASE[plate_no_hyphens]
    
    # Try adding hyphens if not present
    # Check if we can format it
    if '-' not in plate_number:
        # Try Personal format: AAA-123-AA
        if len(plate_number) == 8 and plate_number[0:3].isalpha() and plate_number[3:6].isdigit() and plate_number[6:8].isalpha():
            formatted = f"{plate_number[0:3]}-{plate_number[3:6]}-{plate_number[6:8]}"
            if formatted.replace('-', '') in VEHICLE_DATABASE:
                return VEHICLE_DATABASE[formatted.replace('-', '')]
        
        # Try Commercial format: AA-123-AAA
        if len(plate_number) == 8 and plate_number[0:2].isalpha() and plate_number[2:5].isdigit() and plate_number[5:8].isalpha():
            formatted = f"{plate_number[0:2]}-{plate_number[2:5]}-{plate_number[5:8]}"
            if formatted.replace('-', '') in VEHICLE_DATABASE:
                return VEHICLE_DATABASE[formatted.replace('-', '')]
        
        # Try Government format: FG-123-AA or AA-456-FG
        if len(plate_number) == 7:
            if plate_number[0:2] == 'FG':
                formatted = f"FG-{plate_number[2:5]}-{plate_number[5:7]}"
                if formatted.replace('-', '') in VEHICLE_DATABASE:
                    return VEHICLE_DATABASE[formatted.replace('-', '')]
            elif plate_number[5:7] == 'FG':
                formatted = f"{plate_number[0:2]}-{plate_number[2:5]}-FG"
                if formatted.replace('-', '') in VEHICLE_DATABASE:
                    return VEHICLE_DATABASE[formatted.replace('-', '')]
    
    return None


def lookup_by_owner_name(owner_name):
    """
    Look up vehicles by owner name.
    
    Args:
        owner_name: Name of vehicle owner (partial match)
    
    Returns:
        list: List of vehicle records matching the name
    """
    owner_name = owner_name.strip().upper()
    results = []
    
    for plate, info in VEHICLE_DATABASE.items():
        if owner_name in info['owner_name'].upper():
            results.append({
                'plate_number': plate,
                **info
            })
    
    return results


def lookup_by_state(state_code):
    """
    Look up all vehicles registered in a state.
    
    Args:
        state_code: Two-letter state code (e.g., 'LA' for Lagos)
    
    Returns:
        list: List of vehicles in that state
    """
    state_code = state_code.strip().upper()
    results = []
    
    for plate, info in VEHICLE_DATABASE.items():
        # Extract state code from plate (first 2 letters)
        plate_state = plate[:2]
        if state_code == plate_state:
            results.append({
                'plate_number': plate,
                **info
            })
    
    return results


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


def is_plate_registered(plate_number):
    """
    Check if a license plate is registered in the database.
    
    Args:
        plate_number: License plate number
    
    Returns:
        bool: True if plate exists in database
    """
    return plate_number.strip().upper() in VEHICLE_DATABASE


def get_state_code_from_plate(plate_number):
    """
    Extract state code from a license plate.
    Nigerian plates start with 2-letter state code.
    
    Args:
        plate_number: License plate number
    
    Returns:
        str: Two-letter state code
    """
    if len(plate_number) >= 2:
        return plate_number[:2].upper()
    return ""


def get_registration_info(plate_number):
    """
    Get comprehensive registration information for a plate.
    
    Args:
        plate_number: License plate number
    
    Returns:
        dict: Complete registration information
    """
    vehicle = lookup_vehicle(plate_number)
    
    if not vehicle:
        return {
            'plate_number': plate_number,
            'registered': False,
            'owner_name': 'Unknown',
            'state': 'Unknown',
            'vehicle_type': 'Unknown',
            'color': 'Unknown',
            'year': None,
            'plate_type': 'Unknown'
        }
    
    return {
        'plate_number': plate_number,
        'registered': True,
        **vehicle
    }


def add_vehicle(plate_number, owner_name, state, vehicle_type, color, year, plate_type):
    """
    Add a new vehicle to the database (for demo purposes).
    
    Args:
        plate_number: License plate number
        owner_name: Owner's name
        state: Registration state
        vehicle_type: Type of vehicle
        color: Vehicle color
        year: Year of registration/manufacture
        plate_type: Type of plate (Personal/Commercial/Government)
    
    Returns:
        bool: True if added successfully
    """
    plate_number = plate_number.strip().upper()
    
    if plate_number in VEHICLE_DATABASE:
        return False  # Already exists
    
    VEHICLE_DATABASE[plate_number] = {
        'owner_name': owner_name,
        'state': state,
        'vehicle_type': vehicle_type,
        'color': color,
        'year': year,
        'plate_type': plate_type
    }
    
    return True


def delete_vehicle(plate_number):
    """
    Remove a vehicle from the database (for demo purposes).
    
    Args:
        plate_number: License plate number
    
    Returns:
        bool: True if deleted successfully
    """
    plate_number = plate_number.strip().upper()
    
    if plate_number in VEHICLE_DATABASE:
        del VEHICLE_DATABASE[plate_number]
        return True
    
    return False
