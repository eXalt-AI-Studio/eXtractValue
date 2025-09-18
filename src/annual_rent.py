import pandas as pd

def get_annual_rents(df):
    results = []
    for idx, row in df.iterrows():
        start = pd.to_datetime(row["Date de début"])
        end = pd.to_datetime(row["Date d'expiration"])
        duration = row["Durée (années)"]
        rent = row["Loyer annuel (euros)"]
        landlord = row["Bailleur"]
        tenant = row["Locataire"]
        address = row["Adresse location"]
        city = row["Ville location"]
        for year in range(start.year, end.year + 1):
            # Determine the amount for partial years
            if year == start.year: 
                months = 12 - start.month + 1
            elif year == end.year:
                months = end.month
            else:
                months = 12
            annual_rent = (rent / 12) * months
            results.append({
                'Year': year,
                'Landlord': landlord,
                'Tenant': tenant,
                'Address': address,
                'City': city,
                'Expected Rent (€)': annual_rent
            })
    return pd.DataFrame(results)

