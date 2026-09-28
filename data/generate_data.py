import numpy as np
import pandas as pd
import os

def generate_housing_dataset():
    np.random.seed(42)
    n_samples = 650

    locations = [
        ('Whitefield, Bangalore', 7200, 1.15),
        ('Indiranagar, Bangalore', 12500, 1.55),
        ('Koramangala, Bangalore', 13500, 1.60),
        ('Bandra West, Mumbai', 22000, 2.20),
        ('Andheri East, Mumbai', 14500, 1.65),
        ('Gachibowli, Hyderabad', 6800, 1.10),
        ('Cyber City, Gurgaon', 8900, 1.30),
        ('Kothrud, Pune', 6400, 1.05)
    ]
    
    loc_names = [l[0] for l in locations]
    loc_base_rates = {l[0]: l[1] for l in locations}
    loc_mults = {l[0]: l[2] for l in locations}

    chosen_locs = np.random.choice(loc_names, size=n_samples, p=[0.16, 0.12, 0.12, 0.10, 0.14, 0.13, 0.12, 0.11])

    # Area in square feet: between 600 and 5200 sqft
    areas = np.round(np.random.gamma(shape=9.0, scale=220, size=n_samples)).astype(int)
    areas = np.clip(areas, 650, 5500)

    # Bedrooms correlated with area
    bedrooms = []
    for a in areas:
        if a < 1000:
            b = np.random.choice([1, 2], p=[0.75, 0.25])
        elif a < 1600:
            b = np.random.choice([2, 3], p=[0.60, 0.40])
        elif a < 2500:
            b = np.random.choice([2, 3, 4], p=[0.15, 0.65, 0.20])
        elif a < 3600:
            b = np.random.choice([3, 4, 5], p=[0.20, 0.65, 0.15])
        else:
            b = np.random.choice([4, 5], p=[0.50, 0.50])
        bedrooms.append(b)
    bedrooms = np.array(bedrooms)

    # Bathrooms correlated with bedrooms
    bathrooms = []
    for b in bedrooms:
        if b == 1:
            ba = 1
        elif b == 2:
            ba = np.random.choice([1, 2], p=[0.30, 0.70])
        elif b == 3:
            ba = np.random.choice([2, 3], p=[0.45, 0.55])
        elif b == 4:
            ba = np.random.choice([3, 4], p=[0.50, 0.50])
        else:
            ba = np.random.choice([3, 4], p=[0.30, 0.70])
        bathrooms.append(ba)
    bathrooms = np.array(bathrooms)

    # Floors / Stories: 1 to 4
    floors = np.random.choice([1, 2, 3, 4], size=n_samples, p=[0.35, 0.40, 0.18, 0.07])

    # Main road: 'yes' (85%), 'no' (15%)
    main_road = np.random.choice(['yes', 'no'], size=n_samples, p=[0.84, 0.16])

    # Guestroom: 'yes' (20%), 'no' (80%)
    guestroom = np.random.choice(['yes', 'no'], size=n_samples, p=[0.22, 0.78])

    # Basement: 'yes' (30%), 'no' (70%)
    basement = np.random.choice(['yes', 'no'], size=n_samples, p=[0.32, 0.68])

    # Air conditioning: 'yes' (40%), 'no' (60%)
    air_conditioning = np.random.choice(['yes', 'no'], size=n_samples, p=[0.42, 0.58])

    # Parking: 0, 1, 2, 3 spaces
    parking = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.25, 0.45, 0.22, 0.08])

    # Preferred area: 'yes' (25%), 'no' (75%)
    preferred_area = np.random.choice(['yes', 'no'], size=n_samples, p=[0.26, 0.74])

    # Furnishing status: 'Furnished', 'Semi-Furnished', 'Unfurnished'
    furnishing_status = np.random.choice(['Furnished', 'Semi-Furnished', 'Unfurnished'], size=n_samples, p=[0.30, 0.45, 0.25])

    # Calculate realistic market price (in INR ₹)
    prices = []
    for i in range(n_samples):
        loc = chosen_locs[i]
        rate_per_sqft = loc_base_rates[loc]
        base_val = areas[i] * rate_per_sqft

        # Feature premiums
        bed_prem = (bedrooms[i] - 1) * 350000
        bath_prem = (bathrooms[i] - 1) * 280000
        floor_prem = (floors[i] - 1) * 320000
        park_prem = parking[i] * 300000

        amenity_bonus = 0
        if main_road[i] == 'yes':
            amenity_bonus += 450000
        if guestroom[i] == 'yes':
            amenity_bonus += 380000
        if basement[i] == 'yes':
            amenity_bonus += 420000
        if air_conditioning[i] == 'yes':
            amenity_bonus += 550000
        if preferred_area[i] == 'yes':
            amenity_bonus += 750000

        furnish_bonus = 0
        if furnishing_status[i] == 'Furnished':
            furnish_bonus = 600000
        elif furnishing_status[i] == 'Semi-Furnished':
            furnish_bonus = 250000

        # Realistic noise (+- 7% gaussian noise to reflect natural market negotiation)
        noise = np.random.normal(0, 0.065) * base_val

        price = base_val + bed_prem + bath_prem + floor_prem + park_prem + amenity_bonus + furnish_bonus + noise
        # Round to nearest 10,000 INR
        price = int(round(price / 10000) * 10000)
        # Floor price check
        price = max(price, 2500000)
        prices.append(price)

    df = pd.DataFrame({
        'price': prices,
        'area': areas,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'floors': floors,
        'location': chosen_locs,
        'main_road': main_road,
        'guestroom': guestroom,
        'basement': basement,
        'air_conditioning': air_conditioning,
        'parking': parking,
        'preferred_area': preferred_area,
        'furnishing_status': furnishing_status
    })

    out_path = r'C:\Users\ramac\.gemini\antigravity-ide\scratch\estateai\data\house_prices.csv'
    df.to_csv(out_path, index=False)
    print(f"Generated dataset with {len(df)} records at {out_path}")
    print(df.head())
    print("\nSummary Statistics:")
    print(df.describe())

if __name__ == '__main__':
    generate_housing_dataset()
