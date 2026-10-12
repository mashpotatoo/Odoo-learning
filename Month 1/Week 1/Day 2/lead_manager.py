lead_status = (
    "Premium Lead",
    "Qualified Lead",
    "Low Budget Lead"
)

def classify_lead(budget):
    if budget >= 40000:
        return lead_status[0]
    elif budget >= 25000:
        return lead_status[1]
    else:
        return lead_status[2]

leads = []
unique_city = set()

while True:
    try:
        lead_num = int(input("How many leads do you want to enter? "))
        if lead_num <= 0:
            print("Please enter a number greater than 0.")
            continue
        break
    except ValueError:
        print("Invalid input. Please enter a whole number.")

for i in range(1, lead_num + 1):
    print(f"\n--- Lead #{i} ---")
    name = input("Name: ").strip()
    phone = input("Phone: ").strip()
    city = input("City: ").strip()

    while True:
        try:
            budget = int(input("Budget: "))
            if budget <= 0:
                print("Please enter a budget greater than 0.")
                continue
            break
        except ValueError:
            print("Invalid budget. Please enter a valid number.")

    product = input("Interested Product: ").strip()

    status = classify_lead(budget)

    lead = {
        "name": name,
        "phone": phone,
        "city": city,
        "budget": budget,
        "product": product,
        "status": status
    }

    leads.append(lead)
    if city:
        unique_city.add(city)

total_leads = len(leads)

premium_count = 0
qualified_count = 0
low_budget_count = 0

for lead in leads:
    if lead["status"] == lead_status[0]:
        premium_count += 1
    elif lead["status"] == lead_status[1]:
        qualified_count += 1
    else:
        low_budget_count += 1

print("\n========== LEAD SUMMARY ==========\n")
print(f"Total Leads: {total_leads}")
print(f"Premium Leads: {premium_count}")
print(f"Qualified Leads: {qualified_count}")
print(f"Low Budget Leads: {low_budget_count}")

print("\nUnique Cities:")
for city_name in unique_city:
    print(city_name)

for number, lead in enumerate(leads, start=1):
    print(f"\n---------- Lead {number} ----------")
    print(f"Name:     {lead['name']}")
    print(f"Phone:    {lead['phone']}")
    print(f"City:     {lead['city']}")
    print(f"Product:  {lead['product']}")
    print(f"Budget:   BDT {lead['budget']:,.2f}")
    print(f"Status:   {lead['status']}")